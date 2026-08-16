from datetime import datetime

from pydantic import BaseModel, SecretStr


class KiteSessionData(BaseModel):
    user_id: str
    user_name: str
    access_token: SecretStr
    login_time: datetime


class KiteTokenResponse(BaseModel):
    status: str
    data: KiteSessionData
