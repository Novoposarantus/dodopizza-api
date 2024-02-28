import services.auth as auth
import services.config as config
from models.constants import DATE_FORMAT
from datetime import datetime, timedelta
from services.apiService import ApiService
from services.helper import Confirmation
from models.getScheduleResponse import GetSchedulesResponse

def deleteSchedules(schedulesIds: list[str], token: str) -> None:
    deleted = 0
    countToDelete = len(schedulesIds)

    for id in schedulesIds:
        deleted += 1
        process = round((deleted / countToDelete) * 100, 2)

        if ApiService.deleteSchedule(id, token):
            print(f'Schedule {id} deleted. Process: {process}%')
        else:
            print(f'Error on delete schedule {id}. Process: {process}%')
    
def deleteSchedulesOnWeek(unit: str, weekMondayDate: datetime):
    token = auth.authorize()

    weekSundayDate = weekMondayDate + timedelta(days=6)
    schedules: list[GetSchedulesResponse.Schedule] = ApiService.getSchedules(
        units=[unit],
        beginFrom=weekMondayDate.date(),
        beginTo=(weekSundayDate + timedelta(days=1)).date(),
        token=token
    )

    print(f'{len(schedules)} schedules loaded from {weekMondayDate.date().strftime(DATE_FORMAT)} to {weekSundayDate.date().strftime(DATE_FORMAT)}')
    
    if not any(schedules):
        return
    
    if not Confirmation.check('deletion schedules'):
        return
    
    schedulesIds = list((schedule.id for schedule in schedules))

    deleteSchedules(schedulesIds, token)

deleteSchedulesOnWeek(
    unit=config.unit,
    weekMondayDate=config.copySchedulesToWeekMonday
)