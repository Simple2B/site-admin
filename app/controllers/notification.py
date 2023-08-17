from flask import current_app
import firebase_admin

# from fastapi import status, HTTPException
from firebase_admin import credentials
from firebase_admin import messaging
from firebase_admin.exceptions import FirebaseError
from werkzeug.exceptions import HTTPException

from app.common import models as m
from app import schema as s
from app.database import db
from app.logger import log


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
            android=messaging.AndroidConfig(
                ttl=3600,
                priority="high",
            ),
            apns=messaging.APNSConfig(
                payload=messaging.APNSPayload(
                    aps=messaging.Aps(
                        content_available=True,
                        mutable_content=True,
                    ),
                    headers={"apns-priority": "5"},
                ),
            ),
        )

        try:
            messaging.send_multicast(multicast_message=message)
            log(log.INFO, "Notification sended")
            return {"status": "should be done"}

        except FirebaseError:
            log(log.ERROR, "Error while sending message")
            raise HTTPException(
                code=409,
                description="Error while sending message",
            )

        except (ValueError, TypeError):
            log(log.ERROR, "Message arguments invalid")
            raise HTTPException(code=409, description="Message arguments invalid")


def case_created_notify(case: s.PushNotificationPayload):
    db.session.refresh(case)
    devices: list[str] = db.session.query(m.Device.token).all()

    push_handler = PushHandler()
    push_handler.send_notification(
        s.PushNotificationMessage(
            device_tokens=devices,
            payload=get_notification_payload(
                notification_type=s.NotificationType.CASE_CREATED, case=case
            ),
        )
    )

    log(log.INFO, "[%d] notifications sended", len(devices))


def get_notification_payload(notification_type: s.NotificationType, case: m.Case):
    return s.PushNotificationPayload(
        notification_type=notification_type,
        title=case.title,
        sub_title=case.sub_title,
        project_link=case.project_link,
    )
