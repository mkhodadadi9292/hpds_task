from enum import Enum


class RoleTypes(Enum):
    Admin = 1
    Customer = 2
    Transporter = 3
    Courier = 4


class OrderStatusTypes(Enum):
    Registered = "Registered"
    Scheduled = "Scheduled"
    Delivered = "Delivered"
    Cancelled = "Cancelled"
    # TODO: Remove Delayed in the future
    Delayed = "Delayed"
    Postponed = "Postponed"
    Unassigned = "Unassigned"


class CourierStates(Enum):
    ArrivedAtDelivery = "ArrivedAtDelivery"  # mission
    ArrivedAtHub = "ArrivedAtHub"
    ScanParcel = "ScanParcel"  # mission
    Delivered = "Delivered"  # mission
    Undelivered = "Undelivered"  # mission
    StartLoading = "StartLoading"
    StartRoute = "StartRoute"


class ParcelTypeValues(Enum):
    Regular = "Regular"
    Eco = "Eco"
    Large = "Large"
    Cold = "Cold"


class FuelType(Enum):
    Diesel = "Diesel"
    Petrol = "Petrol"
    Electrical = "Electrical"
    Hybrid = "Hybrid"


class RouteStates(Enum):
    Scheduled = "Scheduled"
    Ongoing = "Ongoing"
    Done = "Done"
    Cancelled = "Cancelled"
