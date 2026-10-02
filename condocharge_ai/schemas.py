from datetime import datetime 
from pydantic import BaseModel
from enum import Enum

class SessionStatus(str, Enum):
    COMPLETED = "completed"
    ABNORMAL_DISCONNECTION = "abnormal_disconnection"
    STOPPED_BY_USER = "stopped_by_user"
    INTERRUPTED_BY_FAILURE = "interrupted_by_failure"


class SessionDTO(BaseModel):
    session_id: str
    charger_id: str
    card_id: str
    started_at: datetime
    ended_at: datetime
    total_kwh: float
    green_kwh: float
    grid_kwh: float
    average_power_kw: float
    max_power_kw: float
    status: SessionStatus