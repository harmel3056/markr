from app.persistence.interfaces.result_repository import ResultRepository

class InMemoryResultRepository(ResultRepository):
    def __init__(self):
        self._store = []

    def save(self, result):
        self._store.append(result)
        return result
