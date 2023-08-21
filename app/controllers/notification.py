from flask import current_app
import firebase_admin

# from fastapi import status, HTTPException
from firebase_admin import credentials
from firebase_admin import messaging
from firebase_admin.exceptions import FirebaseError
from werkzeug.exceptions import Conflict

from app.common import models as m
from app import schema as s
from app.database import db
from app.logger import log

android_config = messaging.AndroidConfig(
    ttl=3600,
    priority="high",
)

APNSConfig = messaging.APNSConfig(
    payload=messaging.APNSPayload(
        aps=messaging.Aps(
            content_available=True,
            mutable_content=True,
        ),
        headers={"apns-priority": "5"},
    ),
)


class PushHandler:
    _is_initialized = False

    def __init__(self):
        if PushHandler._is_initialized:
            log(log.INFO, "Firebase was initialized")
            return

        cred = credentials.Certificate(
            current_app.config["GOOGLE_SERVICE_ACCOUNT_PATH"]
        )
        firebase_admin.initialize_app(cred)
        PushHandler._is_initialized = True

    def send_notification(self, message_data: s.PushNotificationMessage):
        if not message_data.device_tokens:
            log(log.INFO, "User has no tokens to push")
            return

        message = messaging.MulticastMessage(
            tokens=message_data.device_tokens,
            data=message_data.payload.dict(),
            android=android_config,
            apns=APNSConfig,
        )

        try:
            messaging.send_multicast(multicast_message=message)
            log(log.INFO, "Notification sended")
            return {"status": "should be done"}

        except FirebaseError:
            log(log.ERROR, "Error while sending message")
            raise Conflict(
                description="Error while sending message",
            )

        except (ValueError, TypeError):
            log(log.ERROR, "Message arguments invalid")
            raise Conflict(description="Message arguments invalid")


def notify_case_created(case: s.PushNotificationPayload):
    db.session.refresh(case)
    all_devices: list[m.Device] = db.session.query(m.Device).all()

    devices: list[str] = list()

    if all_devices:
        for device in all_devices:
            devices.append(device.token)

    push_handler = PushHandler()
    push_handler.send_notification(
        s.PushNotificationMessage(
            device_tokens=devices,
            payload=get_notification_payload(
                notification_type=s.NotificationType.CASE_CREATED.value,
                case=case,
            ),
        )
    )

    log(log.INFO, "[%d] notifications sended", len(devices))


def get_notification_payload(notification_type: str, case: s.PushNotificationPayload):
    return s.PushNotificationPayload(
        notification_type=notification_type,
        title=case.title,
        sub_title=case.sub_title,
        project_link=case.project_link,
    )
