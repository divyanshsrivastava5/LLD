from SOLID.example_2.better_code.user import User

class UserManager:
    def __init__(self):
        self.users = []

    def add_user(self, user: User):
        self.users.append(user)
        print(f"User {user.name} added successfully.")

    def remove_user(self, user: User):
        if user in self.users:
            self.users.remove(user)
            print(f"User {user.name} removed successfully.")
        else:
            print(f"User {user.name} not found.")

    def update_user(self, user: User, new_name: str):
        if user in self.users:
            user.name = new_name
            print(f"User updated to {new_name}.")
        else:
            print(f"User {user.name} not found.")