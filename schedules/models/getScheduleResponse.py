from __future__ import annotations
from datetime import datetime
from models.enums import StaffType
from models.constants import DATE_TIME_FORMAT
from models.period import Period

class GetSchedulesResponse:
    def __init__(self, schedules: list[GetSchedulesResponse.Schedule], isEndOfListReached: bool) -> None:
        self.schedules = schedules
        self.isEndOfListReached = isEndOfListReached

    def fromJson(json) -> GetSchedulesResponse:
        return GetSchedulesResponse(
            schedules = [GetSchedulesResponse.Schedule.fromJson(schedule) for schedule in json["schedules"]],
            isEndOfListReached = json["isEndOfListReached"]
        )

    class Schedule:
        def __init__(
                self,
                id: str,
                scheduledShiftEndAtLocal: datetime,
                scheduledShiftStartAtLocal: datetime,
                workStationId: str,
                workStationName: str,
                staffPositionId: str,
                staffId: str,
                staffPositionName: str,
                staffShiftPositionId: str,
                staffShiftPositionName: str,
                staffTypeName: StaffType,
                unitId: str,
                unitName: str,
                modifiedAtUtc: datetime,
                modifiedByUserId: str) -> None:
            self.id: str = id
            self.scheduledShiftEndAtLocal: datetime = scheduledShiftEndAtLocal
            self.scheduledShiftStartAtLocal: datetime = scheduledShiftStartAtLocal
            self.workStationId: str = workStationId
            self.workStationName: str = workStationName
            self.staffPositionId: str = staffPositionId
            self.staffId: str = staffId
            self.staffPositionName: str = staffPositionName
            self.staffShiftPositionId: str = staffShiftPositionId
            self.staffShiftPositionName: str = staffShiftPositionName
            self.staffTypeName: StaffType = staffTypeName
            self.unitId: str = unitId
            self.unitName: str = unitName
            self.modifiedAtUtc: datetime = modifiedAtUtc
            self.modifiedByUserId: str = modifiedByUserId


        @property
        def scheduledShiftPeriod(self) -> Period:
            return Period(self.scheduledShiftStartAtLocal, self.scheduledShiftEndAtLocal)

        def fromJson(json) -> GetSchedulesResponse.Schedule:
            return GetSchedulesResponse.Schedule(
                id = json["id"],
                scheduledShiftEndAtLocal = datetime.strptime(json["scheduledShiftEndAtLocal"], DATE_TIME_FORMAT),
                scheduledShiftStartAtLocal = datetime.strptime(json["scheduledShiftStartAtLocal"], DATE_TIME_FORMAT),
                workStationId = json["workStationId"],
                workStationName = json["workStationName"],
                staffPositionId = json["staffPositionId"],
                staffId = json["staffId"],
                staffPositionName = json["staffPositionName"],
                staffShiftPositionId = json["staffShiftPositionId"],
                staffShiftPositionName = json["staffShiftPositionName"],
                staffTypeName = json["staffTypeName"],
                unitId = json["unitId"],
                unitName = json["unitName"],
                modifiedAtUtc = datetime.strptime(json["modifiedAtUtc"], DATE_TIME_FORMAT),
                modifiedByUserId = json["modifiedByUserId"])