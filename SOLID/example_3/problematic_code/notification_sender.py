from SOLID.example_3.problematic_code.notification_type import NotificationType

class NotificationSender:

    def send_notification(self, notification_types: list, message: str):
        for notification_type in notification_types:
            match notification_type:
                case NotificationType.EMAIL:
                    NotificationType.send_email_notification(message)
                case NotificationType.SMS:
                    NotificationType.send_sms_notification(message)
                case NotificationType.PUSH:
                    NotificationType.send_push_notification(message)
                case _:
                    print(f"Unknown notification type: {notification_type}")

        