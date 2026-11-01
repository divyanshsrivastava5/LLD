from SOLID.example_2.better_code.user import User

class ActivityLogger:
    def log_user_activity(self, user: User, activity: str):
        print(f"Logging activity for {user.name}: {activity}")