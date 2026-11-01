class NotificationType:
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"

    def send_sms_notification(self, message: str):
        # Logic to send SMS notification
        print(f"Sending SMS notification: {message}")

    def send_push_notification(self, message: str):
        # Logic to send push notification
        print(f"Sending push notification: {message}")

    def send_email_notification(self, message: str):
        # Logic to send email notification
        print(f"Sending email notification: {message}")
        