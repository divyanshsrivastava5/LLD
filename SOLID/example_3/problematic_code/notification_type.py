class NotificationType:
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"

    @classmethod
    def send_email_notification(cls, message: str):
        print(f"Sending email notification: {message}")

    @classmethod
    def send_sms_notification(cls, message: str):
        print(f"Sending SMS notification: {message}")

    @classmethod
    def send_push_notification(cls, message: str):
        print(f"Sending push notification: {message}")