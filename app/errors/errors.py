from fastapi import Request
from fastapi.responses import JSONResponse

from app.domain.exceptions import (
    InvalidRootTagError,
    InvalidXMLFormatError,
    MissingRequiredFieldError,
    TestNotFoundError,
)


@app.exception_handler(InvalidXMLFormatError)
async def handle_invalid_xml(request: Request, exc: InvalidXMLFormatError):
    return JSONResponse(
        status_code=400,
        content={"error": "INVALID_XML_FORMAT", "message": str(exc)},
    )

@app.exception_handler(InvalidRootTagError)
async def handle_invalid_root(request: Request, exc: InvalidRootTagError):
    return JSONResponse(
        status_code=400,
        content={"error": "INVALID_ROOT_TAG", "message": str(exc)},
    )

@app.exception_handler(MissingRequiredFieldError)
async def handle_missing_field(request: Request, exc: MissingRequiredFieldError):
    return JSONResponse(
        status_code=400,
        content={"error": "MISSING_REQUIRED_FIELD", "message": str(exc)},
    )

@app.exception_handler(TestNotFoundError)
async def handle_test_not_found(request: Request, exc: TestNotFoundError):
    return JSONResponse(
        status_code=404,
        content={"error": "TEST_NOT_FOUND", "message": str(exc)},
    )
