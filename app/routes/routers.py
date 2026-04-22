from fastapi import APIRouter, Body, Header, HTTPException
from app.schemas.schemas import AnalyticsResponse

router = APIRouter()

# will be injected from app.py
router.service = None


@router.post("/import")
def import_results(
    xml_data = Body(..., media_type="application/xml"),
    content_type = Header(None)
):
    if content_type != "text/xml+markr":
        raise HTTPException(
            status_code=400,
            detail="Content-Type must be text/xml+markr"
        )

    router.service.process_results_and_save(xml_data)
    return {"status": "ok"}


@router.get("/results/{test_id}/aggregate", response_model=AnalyticsResponse)
def get_analytics(test_id):
    return router.service.generate_analytics(test_id)