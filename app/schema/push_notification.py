from pydantic import BaseModel

from .enums import NotificationType


class PushNotificationPayload(BaseModel):
    notification_type: NotificationType
    title: str
    sub_title: str
    project_link: str | None


class PushNotificationMessage(BaseModel):
    payload: PushNotificationPayload
    device_tokens: list[str] | None
