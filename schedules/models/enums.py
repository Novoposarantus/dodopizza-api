from __future__ import annotations
from enum import Enum

class StaffType(Enum):
    Operator = "Operator"
    KitchenMember = "KitchenMember"
    Courier = "Courier"
    Cashier = "Cashier"
    PersonalManager = "PersonalManager"

    Unknown = "Unknown"

    def fromStr(value: str) -> StaffType:
        match value.lower():
            case "operator":
                return StaffType.Operator
            case "kitchenmember":
                return StaffType.KitchenMember
            case "courier":
                return StaffType.Courier
            case "cashier":
                return StaffType.Cashier
            case "personalmanager":
                return StaffType.PersonalManager
            case _:
                return StaffType.Unknown

class StaffStatus(Enum):
    Dismissed = "Dismissed"
    Suspended = "Suspended"
    Active = "Active"

    Unknown = "Unknown"

    def fromStr(value: str) -> StaffStatus:
        match value.lower():
            case "dismissed":
                return StaffStatus.Dismissed
            case "suspended":
                return StaffStatus.Suspended
            case "active":
                return StaffStatus.Active
            case _:
                return StaffStatus.Unknown
            