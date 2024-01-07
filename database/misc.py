from pprint import pprint
from typing import List
import httpx, json
from datetime import datetime

from sqlalchemy import delete
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.hub.models import HubShifts, TaskIdHubIdShiftId
from src.order.models import Orders
from src.shared.service_registry_interface import service_registry_client
from src.tasks.models import TaskIdGeneratedMapRouteGeometries, TaskIdLocationItems, TaskIdVroomJson
from fastapi import HTTPException, status
import os
import pytz

import timeutils
from .schemas import RouteSpecificData, OrdersOutput, ServiceTimeEstimationData
from decouple import config


def is_TaskIdHubIdShiftId_for_today(task_id_hub_id_shift_id: TaskIdHubIdShiftId):
    if timeutils.astimezone(task_id_hub_id_shift_id.created_at).date() == timeutils.now().date():
        print("its today!")
        return True
    else:
        return False


def is_TaskIdHubIdShiftId_for_the_date(task_id_hub_id_shift_id: TaskIdHubIdShiftId, the_date: datetime):
    if timeutils.astimezone(task_id_hub_id_shift_id.created_at).date() == timeutils.astimezone(the_date).date():
        print(f"its for {the_date.date()} !")
        return True
    else:
        return False


def get_the_current_clock_shift(all_hub_shifts: list[HubShifts]) -> HubShifts | None:
    for hub_shift in all_hub_shifts:
        if hub_shift.start_time <= datetime.utcnow().time() <= hub_shift.finish_time:
            return hub_shift
    return None


def get_shift_by_shift_id(all_hub_shifts: list[HubShifts], shift_id: int) -> HubShifts | None:
    for hub_shift in all_hub_shifts:
        if hub_shift.id == shift_id:
            return hub_shift
    return None


def check_to_see_if_HubShift_is_for_current_clock_time_or_after(hub_shift: HubShifts):
    if hub_shift.start_time <= datetime.utcnow().time() <= hub_shift.finish_time:
        return True
    elif datetime.utcnow().time() <= hub_shift.start_time:
        return True
    else:
        return False


# This will make sure that:
# 1. Validates given shift, or finds a suitable shift (more on that below)
# 2. the "task_id_hub_id_shift_id" objects that are affected (and also the other task_id related) are for today only and not the other days.
async def clear_all_related_generated_route_data_for_hub_and_its_shift(session: AsyncSession, hubid: int,
                                                                       shift_id: int | None = None):
    # Lets first of all validate the shift

    # If shift_id is not specificed, then the shift at current time is selected. If no shift is available for the current clock time, then return False
    # If shift_id is specified then we should check it to be at the current time or after the current time. If yes it is selected and actions will be done for it, if not will return False

    # get all of hub shifts
    query_results: Result = await session.execute(select(HubShifts)
                                                  .where(HubShifts.hub_id == hubid))
    allHubShifts: list[HubShifts] = query_results.scalars().fetchall()

    # store variable, to be used later
    currentHubShift: HubShifts | None = None

    if shift_id is None:
        currentHubShift = get_the_current_clock_shift(allHubShifts)
        if currentHubShift is None:
            print("Unfortunately looks like we can not find a shift for the current clock time. "
                  "Looks like the clock time is not at any shift. Come back later.")
            return False
    else:
        inputHubShift: HubShifts = get_shift_by_shift_id(allHubShifts, shift_id)
        if inputHubShift is None:
            print("There is not HubShift for this shift_id!")
            return False
        if not check_to_see_if_HubShift_is_for_current_clock_time_or_after(inputHubShift):
            print("The HubShift for shift_id time is past. We should not do anything about it")
            return False
        currentHubShift = inputHubShift

    ####################################################################################################
    ####################################################################################################
    ####################################################################################################

    # Get them to remove related TaskIdVroomJson
    print("=-" * 50, "lets remove all vroom valhalla bullshit tasks")
    query_results: Result = await session.execute(select(TaskIdHubIdShiftId)
                                                  .where(TaskIdHubIdShiftId.hub_id == hubid)
                                                  .where(TaskIdHubIdShiftId.shift_id == currentHubShift.id))
    task_id_hub_id_shift_ids: List[TaskIdHubIdShiftId] = query_results.scalars().fetchall()

    for task_id_hub_id_shift_id in task_id_hub_id_shift_ids:
        if is_TaskIdHubIdShiftId_for_today(task_id_hub_id_shift_id):
            try:
                await session.execute(
                    delete(TaskIdVroomJson).where(TaskIdVroomJson.task_id == task_id_hub_id_shift_id.task_id))
            except:
                pass
            try:
                await session.execute(
                    delete(TaskIdLocationItems).where(TaskIdLocationItems.task_id == task_id_hub_id_shift_id.task_id))
            except:
                pass
            try:
                await session.execute(delete(TaskIdGeneratedMapRouteGeometries).where(
                    TaskIdGeneratedMapRouteGeometries.task_id == task_id_hub_id_shift_id.task_id))
            except:
                pass

            # Remove only for today
            await session.execute(delete(TaskIdHubIdShiftId)
                                  .where(TaskIdHubIdShiftId.id == task_id_hub_id_shift_id.id))

    print("done.")
    return True


# Using the function below, we can get data we need for each route generation.
async def get_needed_route_visualization_data_for_each_hub_shift(session: AsyncSession, hubid: int, shift_id: int, filter_today: bool = True):
    query_results: Result = await session.execute(select(TaskIdHubIdShiftId)
                                                  .where(TaskIdHubIdShiftId.hub_id == hubid)
                                                  .where(TaskIdHubIdShiftId.shift_id == shift_id)
                                                  .order_by(TaskIdHubIdShiftId.id))
    taskIdHubIdShiftIds: List[TaskIdHubIdShiftId] = query_results.scalars().fetchall()

    if len(taskIdHubIdShiftIds) == 0:
        return None

    last_taskIdHubIdShiftIds = taskIdHubIdShiftIds[-1]

    if filter_today and not is_TaskIdHubIdShiftId_for_today(last_taskIdHubIdShiftIds):
        print("Got data is for earlier than today, so we can not return those")
        return None

    ####################################################################################################
    ####################################################################################################
    ####################################################################################################

    last_task_id = last_taskIdHubIdShiftIds.task_id
    print("last_task_id:", last_task_id)

    # lets get vroom_json
    query_results: Result = await session.execute(
        select(TaskIdVroomJson).where(TaskIdVroomJson.task_id == last_task_id)
    )
    task_id_vroom_json: TaskIdVroomJson = query_results.scalars().first()
    vroom_json = task_id_vroom_json.vroom_json

    # lets get generated_map_route_geometries
    query_results: Result = await session.execute(
        select(TaskIdGeneratedMapRouteGeometries).where(TaskIdGeneratedMapRouteGeometries.task_id == last_task_id)
    )
    task_id_generated_map_route_geometries: TaskIdGeneratedMapRouteGeometries = query_results.scalars().first()
    generated_map_route_geometries = task_id_generated_map_route_geometries.generated_map_route_geometries
    unassigned_data = task_id_generated_map_route_geometries.unassigned_data

    # lets get the generated route data for this freakin task_id
    async with httpx.AsyncClient() as client:
        response = await client.post(f"http://{service_registry_client.SERVICE_VROOM_ENGINE}/solver/give_me_solution_json", json={
            "task_id": last_task_id
        }, timeout=None)

        solution = response.json()["solution"]

        return {
            "solution": json.dumps(solution),
            "vroom_json": json.dumps(vroom_json),
            "generated_map_route_geometries": json.dumps(generated_map_route_geometries),
            "unassigned_data": json.dumps(unassigned_data)
        }


#
#
#
#
#
#
#
#
#
#
#

from math import radians, sin, cos, sqrt, atan2
import math


def calc_route_distance(route):
    total_distance = 0.0
    for i in range(len(route) - 1):
        lat1, lon1 = route[i]
        lat2, lon2 = route[i + 1]
        # convert latitudes and longitudes to radians
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        # calculate distance using haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        distance = 6371 * c  # Earth's radius in km
        total_distance += distance
    return total_distance


def calculate_missionPerHour(numberOfMissions, routeDuration):
    try:
        print("calculate_missionPerHour: numberOfMissions", numberOfMissions)
        print("calculate_missionPerHour: routeDuration", routeDuration)
        print("calculate_missionPerHour: math.ceil(routeDuration / 3600)", math.ceil(routeDuration / 3600))
        return round(numberOfMissions / math.ceil(routeDuration / 3600), 1)
    except:
        return 0


def calculate_costPerDelivery(numberOfMissions):
    try:
        print("calculate_costPerDelivery: numberOfMissions", numberOfMissions)
        return round(10000 / numberOfMissions, 1)
    except:
        return 0


def calculate_numberOfDelayedMissions():
    return 1


def calculate_percentageOfDelayedMissions(numberOfDelayedMissions, numberOfMissions):
    try:
        return math.floor((numberOfDelayedMissions / numberOfMissions) * 100)
    except:
        return 0


def read_routeSolution_get_data_back_as_desired_format(routeSolution, vroom_json, generated_map_route_geometries,
                                                       all_parcel_types) -> list[RouteSpecificData]:
    # Data that we want to give back for each route:
    # 1. Number of missions
    # 2. Route distances
    # 3. Route duration
    # 4. Mission per hour
    # 5. Cost per delivery
    # 6. Number of delayed missions
    # 7. Percentage of delayed missions
    # 8. Fuel consumption
    # 9. CO Emission

    output: list[RouteSpecificData] = []

    for i, eachRoute in enumerate(routeSolution["routes"]):
        # An array like so ["Regular", "ECO", ... ]
        routes_parcels = []

        vehicle_id = eachRoute["vehicle"]
        vehicle_skills = []
        for eachVehicle in vroom_json["vehicles"]:
            if eachVehicle["id"] == vehicle_id:
                vehicle_skills = eachVehicle["skills"]
        for each_vehicle_skill in vehicle_skills:
            for parcelType in all_parcel_types:
                if parcelType.id == each_vehicle_skill:
                    routes_parcels.append(parcelType.name)

        # [todo] if the route "Is Return" we should subtract 1 from it instead of 2 (Or maybe not IDK)
        numberOfMissions = len(eachRoute["steps"]) - 2

        route_segments = generated_map_route_geometries[i]["this_route_segments"]
        combined_route_segments = []
        for xcv in route_segments:
            for xcv2 in xcv:
                combined_route_segments.append(xcv2)
        calculated_distance = calc_route_distance(combined_route_segments)  # km

        route_duration = eachRoute["steps"][-1]["arrival"] - eachRoute["steps"][0]["arrival"]

        for rc in routes_parcels:
            output.append(
                RouteSpecificData(
                    route_id=i,
                    parcel_type=rc,

                    number_of_missions=numberOfMissions,
                    route_distances=calculated_distance,
                    route_duration=route_duration,
                    mission_per_hour=calculate_missionPerHour(numberOfMissions, route_duration),
                    cost_per_delivery=calculate_costPerDelivery(numberOfMissions),
                    number_of_delayed_missions=calculate_numberOfDelayedMissions(),
                    percentage_of_delayed_missions=calculate_percentageOfDelayedMissions(
                        calculate_numberOfDelayedMissions(), numberOfMissions),
                    fuel_consumption=1,
                    co_emission=1
                )
            )

    return output


#
#
#
#
#
#
#
#
#

async def turn_unassigned_order_ids_into_order_datas(session: AsyncSession, unassigned_data: str):
    from pydantic import parse_obj_as

    print("turn_unassigned_order_ids_into_order_datas: unassigned_data:")
    unassigned_data = json.loads(unassigned_data)
    pprint(unassigned_data)

    order_datas = []

    for x in unassigned_data:
        order_id = x["order_id"]
        found_order: Orders = (await session.execute(
            select(Orders)
            .where(Orders.id == order_id)
        )).scalars().first()
        print("order_data", found_order)

        ddd = parse_obj_as(OrdersOutput, found_order)
        print(ddd)
        order_datas.append(ddd)

    return order_datas


#
#
#
#
#
#
#
#
#

def is_local():
    try:
        if config("LOCAL") == "TRUE":
            return True
        else:
            return False
    except:
        return False


async def create_the_data_that_we_need_for_service_time_estimation() -> list[ServiceTimeEstimationData]:
    pass

