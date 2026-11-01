from notification import Notification

class PushNotification(Notification):
    def send_notification(self, message: str):
        # Logic to send push notification
        print(f"Sending push notification: {message}")