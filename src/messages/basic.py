from uagents import Model
from typing import List, Dict, Tuple


class ConvertRequest(Model):
    base_currency: str
    target_currencies: List[str]


class ConvertResponse(Model):
    rates: Dict[str, float]


class Error(Model):
    error: str


class Notification(Model):
    name: str
    email: str
    base_cur: str
    notif: List[Tuple[str, float, float]]


class NotificationResponse(Model):
    success: bool
