from notification import Notification

class SMSNotification(Notification):
    def send_notification(self, message: str):
        # Logic to send SMS notification
        print(f"Sending SMS notification: {message}")