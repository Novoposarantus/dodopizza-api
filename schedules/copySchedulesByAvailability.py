from __future__ import annotations
from datetime import datetime, timedelta
from services.apiService import ApiService
from services.helper import Confirmation, DateHelper
from models.getScheduleResponse import GetSchedulesResponse
from models.addSchedulesRequest import AddSchedulesRequest
from models.getStaffAvailabilityResponse import GetStaffAvailabilityResponse
from models.period import Period
from models.constants import DATE_FORMAT
import services.auth as auth
import services.config as config

class CopySchedulesByAvailability:
    def __init__(self, apiService: ApiService) -> None:
        self.apiService = apiService

    def copySchedules(
            self,
            unit: str,
            weekFromMonday: datetime,
            weekToMonday: datetime):
        
        schedules = self.__getSchedules(unit, weekFromMonday)
        staffAvailabilityPeriods = self.__getStaffAvailabilityPeriods(unit, weekToMonday)

        if not any(schedules) or not any(staffAvailabilityPeriods):
            return

        
        schedulesToAdd = CopySchedulesByAvailability.__getCopyOfSchedules(
            weekFromMonday= weekFromMonday,
            weekToMonday= weekToMonday,
            schedules= schedules,
            staffAvailabilityPeriods= staffAvailabilityPeriods
        )

        if not Confirmation.check('adding schedules'):
            return

        self.apiService.addSchedules(schedulesToAdd)

    def __getSchedules(self, unit: str, weekFromMonday: datetime) -> list[GetSchedulesResponse.Schedule]:
        nextWeekMonday: datetime = weekFromMonday + timedelta(days= 7)
        schedules = self.apiService.getSchedules(
            units= [unit],
            beginFrom= weekFromMonday.date(),
            beginTo= nextWeekMonday.date()
        )
        
        weekFromSunday: datetime = weekFromMonday + timedelta(days= 6)
        print(f'{len(schedules)} schedules loaded from {weekFromMonday.date().strftime(DATE_FORMAT)} to {weekFromSunday.date().strftime(DATE_FORMAT)}')

        return schedules
    
    def __getStaffAvailabilityPeriods(self, unit: str, weekToMonday: datetime) -> list[GetStaffAvailabilityResponse.AvailabilityPeriod]:
        weekToSunday: datetime = weekToMonday + timedelta(days= 6)
        staffAvailabilityPeriods = self.apiService.getStaffAvailability(
            units=[unit],
            fromDate= weekToMonday.date(),
            toDate= weekToSunday.date()
        )
    
        print(f'{len(staffAvailabilityPeriods)} staff availability periods loaded from {weekToMonday.date().strftime(DATE_FORMAT)} to {weekToSunday.date().strftime(DATE_FORMAT)}')

        return staffAvailabilityPeriods
    
    def __getCopyOfSchedules(
        weekFromMonday: datetime,
        weekToMonday: datetime,
        schedules: list[GetSchedulesResponse.Schedule],
        staffAvailabilityPeriods: list[GetStaffAvailabilityResponse.AvailabilityPeriod]
    )-> list[AddSchedulesRequest.Schedule]:
        
        result: list[AddSchedulesRequest.Schedule] = []
        for schedule in schedules:
            scheduleToAdd = CopySchedulesByAvailability.__getCopyOfSchedule(
                weekFromMonday= weekFromMonday,
                weekToMonday= weekToMonday,
                schedule= schedule,
                staffAvailabilityPeriods= staffAvailabilityPeriods,
                schedulesToAdd= result
            )
            if scheduleToAdd == None:
                print(f'Cant add copy of schedule {schedule.id}')
                continue

            result.append(scheduleToAdd)
        
        return result
    
    def __getCopyOfSchedule(
        weekFromMonday: datetime,
        weekToMonday: datetime,
        schedule: GetSchedulesResponse.Schedule,
        staffAvailabilityPeriods: list[GetStaffAvailabilityResponse.AvailabilityPeriod],
        schedulesToAdd: list[AddSchedulesRequest.Schedule]
    ) -> AddSchedulesRequest.Schedule | None:
        schedulePeriodOnWeekTo: Period = CopySchedulesByAvailability.__getSchedulePeriodOnWeekTo(schedule, weekFromMonday, weekToMonday)
        scheduleToAdd: AddSchedulesRequest.Schedule  = AddSchedulesRequest.Schedule.fromSchedule(schedule).changeDate(schedulePeriodOnWeekTo.fromLocal, schedulePeriodOnWeekTo.toLocal)

        if CopySchedulesByAvailability.__canCopyScheduleAsIs(schedule, schedulePeriodOnWeekTo, staffAvailabilityPeriods, schedulesToAdd):
            return scheduleToAdd
        
        replacementStaffMemberId = CopySchedulesByAvailability.__getStaffReplacement(
            schedule= schedule,
            schedulePeriodOnWeekTo= schedulePeriodOnWeekTo,
            staffAvailabilityPeriods= staffAvailabilityPeriods,
            schedulesToAdd= schedulesToAdd
        )

        if replacementStaffMemberId == None:
            return None

        scheduleToAdd.staffId = replacementStaffMemberId
        return scheduleToAdd

    def __canCopyScheduleAsIs(
            schedule: GetSchedulesResponse.Schedule,
            schedulePeriodOnWeekTo: Period,
            staffAvailabilityPeriods: list[GetStaffAvailabilityResponse.AvailabilityPeriod],
            schedulesToAdd: list[AddSchedulesRequest.Schedule]
    ) -> bool:

        availabilityPeriods = (availabilityPeriod for availabilityPeriod in staffAvailabilityPeriods if availabilityPeriod.staffId == schedule.staffId 
                               and availabilityPeriod.period.contains(schedulePeriodOnWeekTo))
        return any(availabilityPeriods) and not CopySchedulesByAvailability.__isAnyInterseptions(schedulesToAdd, schedule.staffId, schedulePeriodOnWeekTo)
    
    def __isAnyInterseptions(
            schedulesToAdd: list[AddSchedulesRequest.Schedule],
            staffId: str,
            period: Period):
        return any((schedule for schedule in schedulesToAdd if schedule.staffId == staffId 
                    and schedule.scheduledShiftPeriod.isInterseption(period)))
    
    def __getSchedulePeriodOnWeekTo(schedule: GetSchedulesResponse.Schedule, weekFromMondayDate: datetime, weekToMondayDate: datetime) -> Period:
        deltaStartDays: int = (schedule.scheduledShiftStartAtLocal.date() - weekFromMondayDate.date()).days
        deltaEndDays: int = (schedule.scheduledShiftEndAtLocal.date() - weekFromMondayDate.date()).days

        scheduleStartDate: datetime = weekToMondayDate + timedelta(days= deltaStartDays)
        scheduleEndDate: datetime = weekToMondayDate + timedelta(days= deltaEndDays)
        return Period(
            fromLocal= DateHelper.setDate(schedule.scheduledShiftStartAtLocal, scheduleStartDate),
            toLocal= DateHelper.setDate(schedule.scheduledShiftEndAtLocal, scheduleEndDate))
    
    def __getStaffReplacement(
        schedule: GetSchedulesResponse.Schedule,
        schedulePeriodOnWeekTo: Period,
        staffAvailabilityPeriods: list[GetStaffAvailabilityResponse.AvailabilityPeriod],
        schedulesToAdd: list[AddSchedulesRequest.Schedule]
    ) -> str | None:
        availablePeriods = (availablePeriod for availablePeriod in staffAvailabilityPeriods if 
                            (availablePeriod.positionId == schedule.staffPositionId or availablePeriod.positionId == schedule.staffShiftPositionId)
                            and availablePeriod.period.contains(schedulePeriodOnWeekTo)
                            and not CopySchedulesByAvailability.__isAnyInterseptions(schedulesToAdd, availablePeriod.staffId, schedulePeriodOnWeekTo))
        
        availablePeriod = next(availablePeriods, None)
        return availablePeriod.staffId if availablePeriod != None else None


token = auth.authorize()
apiService = ApiService(config.api_url, token)
copySchedulesByAvailability = CopySchedulesByAvailability(apiService)
copySchedulesByAvailability.copySchedules(
    unit= config.unit,
    weekFromMonday= config.copySchedulesFromWeekMonday,
    weekToMonday= config.copySchedulesToWeekMonday,
)