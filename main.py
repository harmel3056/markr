from fastapi import FastAPI

from app.persistence.sqlite.tables import metadata
from app.persistence.sqlite.db import engine
from app.persistence.sqlite import tables
from app.persistence.sqlite.sqlite_repo import SQLiteResultsRepository
from app.services.result_service import ResultService
from app.routes.routers import router as results_router

from app.errors.errors import (
    handle_invalid_xml,
    handle_invalid_root,
    handle_missing_field,
    handle_test_not_found,
)

from app.errors.exceptions import (
    InvalidXMLFormatError,
    InvalidRootTagError,
    MissingRequiredFieldError,
    TestNotFoundError,
)

app = FastAPI()
metadata.create_all(engine)

# register handlers
app.add_exception_handler(InvalidXMLFormatError, handle_invalid_xml)
app.add_exception_handler(InvalidRootTagError, handle_invalid_root)
app.add_exception_handler(MissingRequiredFieldError, handle_missing_field)
app.add_exception_handler(TestNotFoundError, handle_test_not_found)

repo = SQLiteResultsRepository()
service = ResultService(repo)

# inject service into router
results_router.service = service

app.include_router(results_router)
