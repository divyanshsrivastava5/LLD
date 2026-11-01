# This class is only responsible for generating the performance report of an employee.
class EmployeePerformanceReportGenerator:
    def __init__(self, employee):
        self.employee = employee

    def generate_report(self):
        return f"Performance report for {self.employee.name}"