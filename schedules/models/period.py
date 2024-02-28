from __future__ import annotations
from datetime import datetime
from services.helper import DateHelper
from models.constants import DATE_TIME_FORMAT

class Period:
    def __init__(self, fromLocal : datetime, toLocal : datetime) -> None:
        self.fromLocal: datetime = fromLocal
        self.toLocal: datetime = toLocal
    
    def contains(self, period: Period) -> bool:
        return self.fromLocal <= period.fromLocal and period.toLocal <= self.toLocal
    
    def changeDate(self, newFromDate: datetime, newToDate: datetime) -> Period:
        self.fromLocal = DateHelper.setDate(self.fromLocal, newFromDate)
        self.toLocal = DateHelper.setDate(self.toLocal, newToDate)
        return self
    
    def isInterseption(self, to: Period) -> bool:
        return self.fromLocal <= to.toLocal and to.fromLocal <= self.toLocal
    
    def __str__(self) -> str:
        return f'{self.fromLocal.strftime(DATE_TIME_FORMAT)} - {self.toLocal.strftime(DATE_TIME_FORMAT)}'