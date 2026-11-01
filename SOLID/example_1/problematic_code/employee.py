class Employee:
    id: int
    name: str
    address: str

    def __init__(self, id: int, name: str, address: str):
        self.id = id
        self.name = name
        self.address = address

    def print_performance_report(self):
        print(f"Performance report for employee {self.name} (ID: {self.id})")

    def compute_salary(self):
        return 1000.0

    def update_employee_record(self, name: str, address: str):
        self.name = name
        self.address = address
        print("Employee data updated successfully.")

    def fetch_employee_record(self):
        print(f"Employee ID: {self.id}, Name: {self.name}, Address: {self.address}")