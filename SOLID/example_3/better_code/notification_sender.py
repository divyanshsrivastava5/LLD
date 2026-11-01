from email_notification import EmailNotification
from sms_notification import SMSNotification
from push_notification import PushNotification

class NotificationSender:

    def send_notification(self, notification_types: list[str], message: str):
        for notification_type in notification_types:
            match notification_type:
                case "EMAIL":
                    email_notification = EmailNotification()
                    email_notification.send_email_notification(message)
                case "SMS":
                    sms_notification = SMSNotification()
                    sms_notification.send_sms_notification(message)
                case "PUSH":
                    push_notification = PushNotification()
                    push_notification.send_push_notification(message)
                case _:
                    print(f"Unknown notification type: {notification_type}")