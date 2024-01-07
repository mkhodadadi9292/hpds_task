from datetime import date, datetime, timedelta
from typing import List

from fastapi import HTTPException, status
from sqlalchemy import and_
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from ..courier.models import VehicleTypes
from ..customer.models import ParcelType
from ..hub.models import Regions
from ..order.models import Orders
from ..regions.repository import RegionRepo, RegionRepoAbstract
from ..routes.models import Routes
from ..shared.schemas import RegionsInput
from .constants import OrderStatusTypes


async def get_unassigned_orders(
    hub_id: int, shift_id: int, date: date | None, session: AsyncSession
):
    if date is None:
        date = datetime.strptime(datetime.utcnow().strftime("%Y-%m-%d"), "%Y-%m-%d")

    query_results: Result = await session.execute(
        select(Orders).where(
            and_(
                Orders.hub_id == hub_id,
                Orders.shift_id == shift_id,
                Orders.created_at >= date,
                Orders.created_at < (date + timedelta(days=1)),
                Orders.status == OrderStatusTypes.Unassigned.value,
            )
        )
    )
    unassigned_order_list: List[Orders] = query_results.scalars().fetchall()
    return unassigned_order_list


async def get_all_routes(
    hub_id: int, shift_id: int, date: date | None, session: AsyncSession
):
    if date is None:
        # TODO: Please remove the tomb from this systomb :
        date = datetime.strptime(datetime.utcnow().strftime("%Y-%m-%d"), "%Y-%m-%d")

    query_results: Result = await session.execute(
        select(Routes).where(
            and_(
                Routes.hub_id == hub_id,
                Routes.shift_id == shift_id,
                Routes.created_at >= date,
                Routes.created_at < (date + timedelta(days=1)),
            )
        )
    )
    route_list: List[Routes] = query_results.scalars().fetchall()
    return route_list


async def get_route(route_id: int, session: AsyncSession):
    query_results: Result = await session.execute(
        select(Routes).where(Routes.id == route_id).options(joinedload(Routes.missions))
    )
    route: Routes = query_results.scalars().first()

    if route is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail="Invalid RouteID.",
        )

    return route


async def get_all_parcel_types(session: AsyncSession):
    query_results: Result = await session.execute(select(ParcelType))
    parcel_type_list = query_results.scalars().fetchall()

    return parcel_type_list


async def get_all_vehicle_types(session: AsyncSession):
    query_results: Result = await session.execute(select(VehicleTypes))
    vehicle_type_list = query_results.scalars().fetchall()

    return vehicle_type_list


####################### Region ###############################
class RegionService:
    def __init__(self, session: AsyncSession):
        ##
        self._region_data: RegionRepoAbstract = RegionRepo(session=session)

    async def create(self, data: RegionsInput):
        return await self._region_data.create(data=data)

    async def update(self, data: RegionsInput, pk: int = None):
        return await self._region_data.update(data=data, pk=pk)

    async def list_items(self) -> List[Regions]:
        return await self._region_data.list_items()

    async def get(self, pk):
        return await self._region_data.get(pk=pk)
