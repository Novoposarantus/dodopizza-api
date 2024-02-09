from __future__ import annotations
from collections.abc import Generator
from datetime import datetime, timedelta
import requests
import auth
import config

DATE_TIME_FORMAT = '%Y-%m-%dT%H:%M:%S'
DATE_FORMAT = '%Y-%m-%d'

def getArrayChunks(list: list[any], chunkSize: int) -> Generator[list[any]]:
    chunkSize = max(1, chunkSize)
    return (list[i:i+chunkSize] for i in range(0, len(list), chunkSize))

def strToDateTime(dateTimeStr: str) -> datetime:
    return datetime.strptime(dateTimeStr, DATE_TIME_FORMAT)

def setDate(dateTimeTo: datetime, date: datetime) -> datetime:
    return datetime(
            year= date.year,
            month= date.month,
            day= date.day,
            hour= dateTimeTo.hour, 
            minute= dateTimeTo.minute,
            second= dateTimeTo.second,
            microsecond= dateTimeTo.microsecond)

def getSchedules(units: list[str], beginFrom: datetime, beginTo: datetime, token: str) -> list:
    schedules = []
    isEndOfListReached = False

    while not isEndOfListReached:
        result = requests.get(
            url = f'{config.api_url}/staff/schedules',
            params = {
                'units': ','.join(units),
                'beginFrom': beginFrom.strftime(DATE_TIME_FORMAT),
                'beginTo': beginTo.strftime(DATE_TIME_FORMAT),
                'skip': len(schedules),
            },
            headers = {
                'Authorization': f'Bearer {token}'
            })
        if (result.status_code != 200):
            return []
        
        resultJson = result.json()
        schedules += resultJson['schedules']
        isEndOfListReached = resultJson['isEndOfListReached']
    
    return schedules

def scheduleToDate(schedule, weekMondayFromDate: datetime, weekMondayToDate: datetime) -> object:
    scheduledShiftStartAtLocal = strToDateTime(schedule['scheduledShiftStartAtLocal'])
    scheduledShiftEndAtLocal = strToDateTime(schedule['scheduledShiftEndAtLocal'])

    deltaStartDays = (scheduledShiftStartAtLocal.date() - weekMondayFromDate.date()).days
    deltaEndDays = (scheduledShiftEndAtLocal.date() - weekMondayFromDate.date()).days

    scheduleStartDate = weekMondayToDate + timedelta(days= deltaStartDays)
    scheduleEndDate = weekMondayToDate + timedelta(days= deltaEndDays)

    return {
            'unitId': schedule['unitId'],
            'staffId': schedule['staffId'],
            'scheduledShiftStartAtLocal': setDate(scheduledShiftStartAtLocal, scheduleStartDate).strftime(DATE_TIME_FORMAT),
            'scheduledShiftEndAtLocal': setDate(scheduledShiftEndAtLocal, scheduleEndDate).strftime(DATE_TIME_FORMAT),
            'workStationId': schedule['workStationId'],
            'shiftPositionId': schedule['staffShiftPositionId'] if schedule['staffShiftPositionId'] != None else schedule['staffPositionId']
        }

def addSchedules(schedules: list, token: str):
    if not any(schedules):
        return True

    schedulesChunks = getArrayChunks(schedules, 30)
    for schedulesChunk in schedulesChunks:
        print(f'Start add schedules chunk sizeof {len(schedulesChunk)}')
        result = requests.post(
            url=f'{config.api_url}/staff/schedules',
            json= {
                'schedules': schedulesChunk
            },
            headers = {
                'Authorization': f'Bearer {token}'
            }
        )

        if (result.status_code != 200):
            return
        
        print(f'Schedules chunk added')

def copySchedules(
        unit: str,
        weekMondayFrom: datetime,
        weekMondayTo: datetime):
    token = auth.authorize()

    weekFromSunday = weekMondayFrom + timedelta(days=6)
    schedules = getSchedules(
        units=[unit],
        beginFrom=weekMondayFrom.date(),
        beginTo=(weekFromSunday + timedelta(days=1)).date(),
        token=token
    )

    print(f'{len(schedules)} schedules loaded from {weekMondayFrom.date().strftime(DATE_FORMAT)} to {weekFromSunday.date().strftime(DATE_FORMAT)}')

    if not any(schedules):
        return
    
    print(f'Confirm adding. Y/N')
    confirmation = input()
    if confirmation.lower().strip() != 'y':
        print('adding canceled')
        return
    
    schedulesToAdd = list(map(lambda schedule: scheduleToDate(schedule, weekMondayFrom, weekMondayTo), schedules))

    addSchedules(
        schedules=schedulesToAdd,
        token=token
    )

copySchedules(
    unit= config.unit,
    weekMondayFrom= config.copySchedulesFromWeekMonday,
    weekMondayTo= config.copySchedulesToWeekMonday,
)