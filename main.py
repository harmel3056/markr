from fastapi import FastAPI

from app.persistence.in_memory.result_repository import InMemoryResultRepository
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

# register handlers
app.add_exception_handler(InvalidXMLFormatError, handle_invalid_xml)
app.add_exception_handler(InvalidRootTagError, handle_invalid_root)
app.add_exception_handler(MissingRequiredFieldError, handle_missing_field)
app.add_exception_handler(TestNotFoundError, handle_test_not_found)

repo = InMemoryResultRepository()
service = ResultService(repo)

# inject service into router
results_router.service = service

app.include_router(results_router)
