from app.persistence.interfaces.result_repository import ResultRepository

class InMemoryResultRepository(ResultRepository):
    def __init__(self):
        # key: (student_number, test_id)
        # value: TestResult domain object
        self._store = {}

    def save(self, result):
        key = (result.student_number, result.test_id)
        self._store[key] = result
        return result

    def get_by_student_and_test(self, student_number, test_id):
        return self._store.get((student_number, test_id))

    def get_by_test_id(self, test_id):
        results = []
        
        for (student, stored_test_id), result in self._store.items():
            if stored_test_id == test_id:
                results.append(result)

        return results