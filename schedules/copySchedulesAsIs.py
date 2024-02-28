from __future__ import annotations
from datetime import datetime, timedelta
from services.apiService import ApiService
from services.helper import Confirmation
from models.getScheduleResponse import GetSchedulesResponse
from models.addSchedulesRequest import AddSchedulesRequest
from models.constants import DATE_FORMAT
import services.auth as auth
import services.config as config

def scheduleToDate(schedule: GetSchedulesResponse.Schedule, weekFromMondayDate: datetime, weekToMondayDate: datetime) -> AddSchedulesRequest.Schedule:
    deltaStartDays: int = (schedule.scheduledShiftStartAtLocal.date() - weekFromMondayDate.date()).days
    deltaEndDays: int = (schedule.scheduledShiftEndAtLocal.date() - weekFromMondayDate.date()).days

    scheduleStartDate: datetime = weekToMondayDate + timedelta(days= deltaStartDays)
    scheduleEndDate: datetime = weekToMondayDate + timedelta(days= deltaEndDays)

    scheduleToAdd: AddSchedulesRequest.Schedule = AddSchedulesRequest.Schedule.fromSchedule(schedule)
    scheduleToAdd.changeDate(
        newStartDate= scheduleStartDate,
        newEndDate= scheduleEndDate
    )
    return scheduleToAdd

def copySchedules(
        unit: str,
        weekFromMonday: datetime,
        weekToMonday: datetime):
    token: str = auth.authorize()

    weekFromSunday: datetime = weekFromMonday + timedelta(days=6)
    schedules: list[GetSchedulesResponse.Schedule] = ApiService.getSchedules(
        units=[unit],
        beginFrom=weekFromMonday.date(),
        beginTo=(weekFromSunday + timedelta(days=1)).date(),
        token=token
    )

    print(f'{len(schedules)} schedules loaded from {weekFromMonday.date().strftime(DATE_FORMAT)} to {weekFromSunday.date().strftime(DATE_FORMAT)}')

    if not any(schedules):
        return
    
    if not Confirmation.check('adding schedules'):
        return
    
    schedulesToAdd: list[AddSchedulesRequest.Schedule] = [scheduleToDate(schedule, weekFromMonday, weekToMonday) for schedule in schedules]

    ApiService.addSchedules(
        schedules=schedulesToAdd,
        token=token
    )

copySchedules(
    unit= config.unit,
    weekFromMonday= config.copySchedulesFromWeekMonday,
    weekToMonday= config.copySchedulesToWeekMonday,
)