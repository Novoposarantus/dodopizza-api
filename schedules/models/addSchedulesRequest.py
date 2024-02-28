from __future__ import annotations
from datetime import datetime
from models.constants import DATE_TIME_FORMAT
from models.period import Period
from models.getScheduleResponse import GetSchedulesResponse
from services.helper import DateHelper

class AddSchedulesRequest:
    def __init__(self, schedules: list[AddSchedulesRequest.Schedule]) -> None:
        self.schedules = schedules

    def getObject(self) -> object:
        return {
            "schedules": [x.getObject() for x in self.schedules]
        }

    class Schedule:
        def __init__(
                self,
                unitId: str,
                staffId: str,
                scheduledShiftStartAtLocal: datetime,
                scheduledShiftEndAtLocal: datetime,
                workStationId: str,
                shiftPositionId: str) -> None:
            self.unitId: str = unitId
            self.staffId: str = staffId
            self.scheduledShiftStartAtLocal: datetime = scheduledShiftStartAtLocal
            self.scheduledShiftEndAtLocal: datetime = scheduledShiftEndAtLocal
            self.workStationId: str = workStationId
            self.shiftPositionId: str = shiftPositionId

        @property
        def scheduledShiftPeriod(self) -> Period:
            return Period(self.scheduledShiftStartAtLocal, self.scheduledShiftEndAtLocal)

        def getObject(self) -> dict[str, any]:
            return {
                'unitId': self.unitId,
                'staffId': self.staffId,
                'scheduledShiftStartAtLocal': self.scheduledShiftStartAtLocal.strftime(DATE_TIME_FORMAT),
                'scheduledShiftEndAtLocal': self.scheduledShiftEndAtLocal.strftime(DATE_TIME_FORMAT),
                'workStationId': self.workStationId,
                'shiftPositionId': self.shiftPositionId
            }
        
        def changeDate(self, newStartDate: datetime, newEndDate: datetime) -> AddSchedulesRequest.Schedule:
            self.scheduledShiftStartAtLocal = DateHelper.setDate(
                self.scheduledShiftStartAtLocal,
                newStartDate
            )
            self.scheduledShiftEndAtLocal = DateHelper.setDate(
                self.scheduledShiftEndAtLocal,
                newEndDate
            )
            
            return self
        
        def fromSchedule(schedule: GetSchedulesResponse.Schedule) -> AddSchedulesRequest.Schedule:
            return AddSchedulesRequest.Schedule(
                unitId= schedule.unitId,
                staffId= schedule.staffId,
                scheduledShiftStartAtLocal = schedule.scheduledShiftStartAtLocal,
                scheduledShiftEndAtLocal= schedule.scheduledShiftEndAtLocal,
                workStationId= schedule.workStationId,
                shiftPositionId= schedule.staffShiftPositionId if schedule.staffShiftPositionId != None else schedule.staffPositionId
            )