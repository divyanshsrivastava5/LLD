from notification import Notification

class EmailNotification(Notification):
    def send_notification(self, message: str):
        # Logic to send email notification
        print(f"Sending email notification: {message}")