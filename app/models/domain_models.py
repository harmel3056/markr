from dataclasses import dataclass

@dataclass
class TestResult:
    student_number: str
    test_id: str
    marks_obtained: int
    marks_available: int

    def percentage(self) -> float:
        if self.marks_available == 0:
            return 0.0
        return (self.marks_obtained / self.marks_available) * 100
