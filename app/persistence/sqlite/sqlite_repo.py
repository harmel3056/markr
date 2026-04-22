from sqlalchemy import insert, select, delete
from app.persistence.sqlite.db import engine
from app.persistence.sqlite.tables import results_table
from app.models.domain_models import TestResult


class SQLiteResultsRepository:

    def save(self, result):
        # using overwrite behaviour in lieu of update functionality
        # delete any existing row with same <student_id> or <test_id>
        # insert the new row
        delete_stmt = (
            delete(results_table)
            .where(results_table.c.student_id == result.student_number)
            .where(results_table.c.test_id == result.test_id)
        )

        insert_stmt = insert(results_table).values(
            student_id=result.student_number,
            test_id=result.test_id,
            marks_obtained=result.marks_obtained,
            marks_available=result.marks_available,
        )

        with engine.begin() as conn:
            conn.execute(delete_stmt)
            conn.execute(insert_stmt)

        return result

    def get_by_student_and_test(self, student_number, test_id):
        stmt = (
            select(results_table)
            .where(results_table.c.student_id == student_number)
            .where(results_table.c.test_id == test_id)
        )

        with engine.begin() as conn:
            row = conn.execute(stmt).fetchone()

        if row is None:
            return None

        return TestResult(
            student_number=row.student_id,
            test_id=row.test_id,
            marks_obtained=row.marks_obtained,
            marks_available=row.marks_available,
        )

    def get_by_test_id(self, test_id):
        stmt = select(results_table).where(results_table.c.test_id == test_id)

        with engine.begin() as conn:
            rows = conn.execute(stmt).fetchall()

        results = []
        for row in rows:
            results.append(
                TestResult(
                    student_number=row.student_id,
                    test_id=row.test_id,
                    marks_obtained=row.marks_obtained,
                    marks_available=row.marks_available,
                )
            )

        return results
