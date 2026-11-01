from notification import Notification

class NotificationSender:

    def send_notification(self, notifications: list[Notification], message: str):
        for notification in notifications:
            notification.send_notification(message)