from app.models.domain_models import TestResult

class ResultRepository:
    def save(self, result: TestResult) -> TestResult:
        raise NotImplementedError

    def get_by_student_and_test(
        self,
        student_number: str,
        test_id: str
    ) -> TestResult | None:
        raise NotImplementedError

    def get_by_test_id(self, test_id: str) -> list[TestResult]:
        raise NotImplementedError
