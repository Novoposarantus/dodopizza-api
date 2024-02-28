from datetime import datetime
from models.getScheduleResponse import GetSchedulesResponse
from models.addSchedulesRequest import AddSchedulesRequest
from models.getStaffAvailabilityResponse import GetStaffAvailabilityResponse
from models.constants import DATE_TIME_FORMAT
from services.helper import ArrayHelper
import requests
import services.config as config

class ApiService:
    def getSchedules(units: list[str], beginFrom: datetime, beginTo: datetime, token: str) -> list[GetSchedulesResponse.Schedule]:
        schedules: list[GetSchedulesResponse.Schedule] = []
        isEndOfListReached: bool = False

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
                print("Error on get schedules")
                return []
            
            resultJson = result.json()
            schedules += [GetSchedulesResponse.Schedule.fromJson(jsonSchedule) for jsonSchedule in resultJson['schedules']]
            isEndOfListReached = resultJson['isEndOfListReached']
        
        return schedules
    
    def addSchedules(schedules: list[AddSchedulesRequest.Schedule], token: str):
        if not any(schedules):
            return

        schedulesChunks = ArrayHelper.getArrayChunks(schedules, 30)
        for schedulesChunk in schedulesChunks:
            print(f'Start add schedules chunk sizeof {len(schedulesChunk)}')
            result = requests.post(
                url=f'{config.api_url}/staff/schedules',
                json= AddSchedulesRequest(schedules= schedulesChunk).getObject(),
                headers = {
                    'Authorization': f'Bearer {token}'
                }
            )

            if (result.status_code != 200):
                print("Error on add schedules chunk")
                return
            
            print(f'Schedules chunk added')

    def deleteSchedule(id: str, token: str):
        result = requests.delete(
            url=f"{config.api_url}/staff/schedules/{id}",
            headers = {
                "Authorization": f"Bearer {token}"
            }
        )

        if (result.status_code != 204):
            print("Error on delete schedule")
            return False
        
        return True
        
    def getStaffAvailability(units: list[str], fromDate: datetime, toDate: datetime, token: str) -> list[GetStaffAvailabilityResponse.AvailabilityPeriod]:
        result = requests.get(
            url = f'{config.api_url}/staff/schedules/availability-periods',
            params = {
                'units': ','.join(units),
                'from': fromDate.strftime(DATE_TIME_FORMAT),
                'to': toDate.strftime(DATE_TIME_FORMAT),
            },
            headers = {
                'Authorization': f'Bearer {token}'
            })
        
        if (result.status_code != 200):
            print("Error on get staff availability")
            return []
        
        resultJson = result.json()
        return [GetStaffAvailabilityResponse.AvailabilityPeriod.fromJson(availabilityPeriod) for availabilityPeriod in resultJson['availabilityPeriods']]