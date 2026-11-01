# This class follows SRP

# This class is now reponsible for Employee creation and data management.
class Employee:
    id: int
    name: str
    address: str

    def __init__(self, id: int, name: str, address: str):
        self.id = id
        self.name = name
        self.address = address

    def fetch_employee_record(self):
        print(f"Employee ID: {self.id}, Name: {self.name}, Address: {self.address}")