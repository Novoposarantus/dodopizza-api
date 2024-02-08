import requests
import auth
import config
from datetime import datetime, timedelta

DATE_TIME_FORMAT = '%Y-%m-%dT%H:%M:%S'
DATE_FORMAT = '%Y-%m-%d'

def getSchedules(units: list[str], beginFrom: datetime, beginTo: datetime, token: str) -> list:
    schedules = []
    isEndOfListReached = False

    while not isEndOfListReached:
        result = requests.get(
            url = f"{config.api_url}/staff/schedules",
            params = {
                'units': ','.join(units),
                'beginFrom': beginFrom.strftime(DATE_TIME_FORMAT),
                'beginTo': beginTo.strftime(DATE_TIME_FORMAT),
                'skip': len(schedules)
            },
            headers = {
                "Authorization": f"Bearer {token}"
            })
        if (result.status_code != 200):
            return []
        
        resultJson = result.json()
        schedules += resultJson['schedules']
        isEndOfListReached = resultJson['isEndOfListReached']
    
    return schedules

def deleteSchedules(schedulesIds: list[str], token: str) -> None:
    deleted = 0
    countToDelete = len(schedulesIds)

    for id in schedulesIds:
        deleted += 1
        process = round((deleted / countToDelete) * 100, 2)

        if deleteSchedule(id, token):
            print(f'Schedule {id} deleted. Process: {process}%')
        else:
            print(f'Error on delete schedule {id}. Process: {process}%')


def deleteSchedule(id: str, token: str) -> bool:
    result = requests.delete(
        url=f"{config.api_url}/staff/schedules/{id}",
        headers = {
            "Authorization": f"Bearer {token}"
        }
    )

    if (result.status_code != 204):
        return False
    
    return True
    
def deleteSchedulesOnWeek(unit: str, weekMondayDate: datetime):
    token = auth.authorize()

    weekSundayDate = weekMondayDate + timedelta(days=6)
    schedules = getSchedules(
        units=[unit],
        beginFrom=weekMondayDate.date(),
        beginTo=(weekSundayDate + timedelta(days=1)).date(),
        token=token
    )

    print(f'{len(schedules)} schedules loaded from {weekMondayDate.date().strftime(DATE_FORMAT)} to {weekSundayDate.date().strftime(DATE_FORMAT)}')
    
    if not any(schedules):
        return
    
    print(f'Confirm deletion. Y/N')
    confirmation = input()
    if confirmation.lower().strip() != 'y':
        print('deletion canceled')
        return
    
    schedulesIds = list(map(lambda schedule: schedule['id'], schedules))

    deleteSchedules(schedulesIds, token)

deleteSchedulesOnWeek(
    unit=config.unit,
    weekMondayDate=config.copySchedulesToWeekMonday
)