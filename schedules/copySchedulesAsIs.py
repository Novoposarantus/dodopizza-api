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
        apiService: ApiService,
        unit: str,
        weekFromMonday: datetime,
        weekToMonday: datetime):
    weekFromSunday: datetime = weekFromMonday + timedelta(days=6)
    schedules: list[GetSchedulesResponse.Schedule] = apiService.getSchedules(
        units=[unit],
        beginFrom=weekFromMonday.date(),
        beginTo=(weekFromSunday + timedelta(days=1)).date()
    )

    print(f'{len(schedules)} schedules loaded from {weekFromMonday.date().strftime(DATE_FORMAT)} to {weekFromSunday.date().strftime(DATE_FORMAT)}')

    if not any(schedules):
        return
    
    if not Confirmation.check('adding schedules'):
        return
    
    schedulesToAdd: list[AddSchedulesRequest.Schedule] = [scheduleToDate(schedule, weekFromMonday, weekToMonday) for schedule in schedules]

    apiService.addSchedules(schedulesToAdd)

token = auth.authorize()
apiService = ApiService(config.api_url, token)
copySchedules(
    apiService=apiService,
    unit= config.unit,
    weekFromMonday= config.copySchedulesFromWeekMonday,
    weekToMonday= config.copySchedulesToWeekMonday,
)