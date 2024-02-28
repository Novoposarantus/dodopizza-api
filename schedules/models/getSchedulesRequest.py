import datetime

from models.enums import StaffType
from models.constants import DATE_TIME_FORMAT

class GetSchedulesRequest:
    def __init__(
            self,
            beginFrom: datetime.datetime,
            beginTo: datetime.datetime,
            units: list[str],
            staffType: StaffType | None = None,
            skip: int | None = None,
            take: int | None = None) -> None:
        self.beginFrom: datetime.datetime = beginFrom
        self.beginTo: datetime.datetime = beginTo
        self.units: list[str] = units
        self.staffType: StaffType | None = staffType
        self.skip: int | None = skip
        self.take: int | None = take

    def getObject(self) -> dict[str, any]:
        return {
            'beginFrom': self.beginFrom.strftime(DATE_TIME_FORMAT),
            'beginTo': self.beginTo.strftime(DATE_TIME_FORMAT),
            'units': ','.join(self.units),
            'staffType': None if self.staffType == None else str(self.staffType),
            'skip': None if self.skip == None else self.skip,
            'take': None if self.take == None else self.take,
        }