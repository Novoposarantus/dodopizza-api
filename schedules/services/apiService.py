from datetime import datetime
from models.getScheduleResponse import GetSchedulesResponse
from models.addSchedulesRequest import AddSchedulesRequest
from models.getStaffAvailabilityResponse import GetStaffAvailabilityResponse
from models.constants import DATE_TIME_FORMAT
from services.helper import ArrayHelper
import requests
import services.config as config

class ApiService:
    def __init__(self, api_url, token) -> None:
        self.api_url = api_url
        self.token = token

    def getSchedules(self, units: list[str], beginFrom: datetime, beginTo: datetime) -> list[GetSchedulesResponse.Schedule]:
        schedules: list[GetSchedulesResponse.Schedule] = []
        isEndOfListReached: bool = False

        while not isEndOfListReached:
            result = requests.get(
                url = f'{self.api_url}/staff/schedules',
                params = {
                    'units': ','.join(units),
                    'beginFrom': beginFrom.strftime(DATE_TIME_FORMAT),
                    'beginTo': beginTo.strftime(DATE_TIME_FORMAT),
                    'skip': len(schedules),
                },
                headers = {
                    'Authorization': f'Bearer {self.token}'
                })
            if (result.status_code != 200):
                print("Error on get schedules")
                return []
            
            resultJson = result.json()
            schedules += [GetSchedulesResponse.Schedule.fromJson(jsonSchedule) for jsonSchedule in resultJson['schedules']]
            isEndOfListReached = resultJson['isEndOfListReached']
        
        return schedules
    
    def addSchedules(self, schedules: list[AddSchedulesRequest.Schedule]):
        if not any(schedules):
            return

        schedulesChunks = ArrayHelper.getArrayChunks(schedules, 30)
        for schedulesChunk in schedulesChunks:
            print(f'Start add schedules chunk sizeof {len(schedulesChunk)}')
            result = requests.post(
                url=f'{self.api_url}/staff/schedules',
                json= AddSchedulesRequest(schedules= schedulesChunk).getObject(),
                headers = {
                    'Authorization': f'Bearer {self.token}'
                }
            )

            if (result.status_code != 200):
                print("Error on add schedules chunk")
                return
            
            print(f'Schedules chunk added')

    def deleteSchedule(self, id: str):
        result = requests.delete(
            url=f"{config.api_url}/staff/schedules/{id}",
            headers = {
                "Authorization": f"Bearer {self.token}"
            }
        )

        if (result.status_code != 204):
            print("Error on delete schedule")
            return False
        
        return True
        
    def getStaffAvailability(self, units: list[str], fromDate: datetime, toDate: datetime) -> list[GetStaffAvailabilityResponse.AvailabilityPeriod]:
        result = requests.get(
            url = f'{config.api_url}/staff/schedules/availability-periods',
            params = {
                'units': ','.join(units),
                'from': fromDate.strftime(DATE_TIME_FORMAT),
                'to': toDate.strftime(DATE_TIME_FORMAT),
            },
            headers = {
                'Authorization': f'Bearer {self.token}'
            })
        
        if (result.status_code != 200):
            print("Error on get staff availability")
            return []
        
        resultJson = result.json()
        return [GetStaffAvailabilityResponse.AvailabilityPeriod.fromJson(availabilityPeriod) for availabilityPeriod in resultJson['availabilityPeriods']]