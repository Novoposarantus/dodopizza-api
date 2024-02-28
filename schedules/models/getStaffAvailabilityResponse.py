from __future__ import annotations
from datetime import datetime
from models.period import Period
from models.constants import DATE_TIME_FORMAT

class GetStaffAvailabilityResponse:
    def __init__(self, availabilityPeriods: list[GetStaffAvailabilityResponse.AvailabilityPeriod]) -> None:
        self.availabilityPeriods = availabilityPeriods

    def fromJson(json) -> GetStaffAvailabilityResponse:
        availabilityPeriods = [GetStaffAvailabilityResponse.AvailabilityPeriod.fromJson(period) for period in json["availabilityPeriods"]]
        return GetStaffAvailabilityResponse(
            availabilityPeriods=availabilityPeriods
        )

    class AvailabilityPeriod:
        def __init__(
                self,
                staffId: str,
                unitId: str,
                positionId: str,
                fromLocal: datetime,
                toLocal: datetime) -> None:
            self.staffId: str = staffId
            self.unitId: str = unitId
            self.positionId: str = positionId
            self.fromLocal: datetime = fromLocal
            self.toLocal: datetime = toLocal

        def fromJson(json) -> GetStaffAvailabilityResponse.AvailabilityPeriod:
            return GetStaffAvailabilityResponse.AvailabilityPeriod(
                staffId = json["staffId"],
                unitId = json["unitId"],
                positionId = json["positionId"],
                fromLocal = datetime.strptime(json["fromLocal"], DATE_TIME_FORMAT),
                toLocal = datetime.strptime(json["toLocal"], DATE_TIME_FORMAT))

        @property
        def period(self) -> Period:
            return Period(self.fromLocal, self.toLocal)