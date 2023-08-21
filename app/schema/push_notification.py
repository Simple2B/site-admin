from pydantic import BaseModel


class PushNotificationPayload(BaseModel):
    notification_type: str
    title: str
    sub_title: str
    project_link: str | None


class PushNotificationMessage(BaseModel):
    payload: PushNotificationPayload
    device_tokens: list[str] | None
