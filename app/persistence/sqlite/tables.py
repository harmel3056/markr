from sqlalchemy import Table, Column, String, Integer, MetaData

metadata = MetaData()

results_table = Table(
    "results",
    metadata,
    Column("student_id", String, primary_key=True),
    Column("test_id", String, primary_key=True),
    Column("marks_obtained", Integer),
    Column("marks_available", Integer),
)
