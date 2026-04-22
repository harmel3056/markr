from dataclasses import dataclass

@dataclass
class TestResult:
    student_number: str
    test_id: str
    marks_obtained: int
    marks_available: int

    def percentage(self) -> float:
        return (self.marks_obtained / self.marks_available) * 100
