import pytest
from fastapi.testclient import TestClient
from app.persistence.in_memory.result_repository import InMemoryResultRepository
from app.services.result_service import ResultService
from main import app, results_router


@pytest.fixture
def client():
    repo = InMemoryResultRepository()
    service = ResultService(repo)
    results_router.service = service
    return TestClient(app)


VALID_XML = b"""
<mcq-test-results>
    <mcq-test-result scanned-on="2017-12-04T12:12:10+11:00">
        <first-name>Jane</first-name>
        <last-name>Austen</last-name>
        <student-number>521585128</student-number>
        <test-id>1234</test-id>
        <summary-marks available="20" obtained="13" />
    </mcq-test-result>
</mcq-test-results>
"""


# --- /import tests ---

def test_import_valid_xml(client):
    response = client.post(
        "/import",
        content=VALID_XML,
        headers={"Content-Type": "text/xml+markr"}
    )
    assert response.status_code == 200


def test_import_wrong_content_type(client):
    response = client.post(
        "/import",
        content=VALID_XML,
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 400


def test_import_malformed_xml(client):
    response = client.post(
        "/import",
        content=b"this is not xml",
        headers={"Content-Type": "text/xml+markr"}
    )
    assert response.status_code == 400


def test_import_wrong_root_tag(client):
    response = client.post(
        "/import",
        content=b"<wrong-root><mcq-test-result/></wrong-root>",
        headers={"Content-Type": "text/xml+markr"}
    )
    assert response.status_code == 400


def test_import_missing_required_field(client):
    xml = b"""
    <mcq-test-results>
        <mcq-test-result>
            <student-number>123</student-number>
            <summary-marks available="10" obtained="5" />
        </mcq-test-result>
    </mcq-test-results>
    """
    response = client.post(
        "/import",
        content=xml,
        headers={"Content-Type": "text/xml+markr"}
    )
    assert response.status_code == 400


def test_import_rejects_entire_document_if_one_result_invalid(client):
    xml = b"""
    <mcq-test-results>
        <mcq-test-result>
            <student-number>111</student-number>
            <test-id>1234</test-id>
            <summary-marks available="10" obtained="5" />
        </mcq-test-result>
        <mcq-test-result>
            <student-number>222</student-number>
            <summary-marks available="10" obtained="5" />
        </mcq-test-result>
    </mcq-test-results>
    """
    response = client.post(
        "/import",
        content=xml,
        headers={"Content-Type": "text/xml+markr"}
    )
    assert response.status_code == 400


# --- /results/{test_id}/aggregate tests ---

def test_aggregate_returns_correct_shape(client):
    client.post("/import", content=VALID_XML, headers={"Content-Type": "text/xml+markr"})
    response = client.get("/results/1234/aggregate")
    assert response.status_code == 200
    data = response.json()
    for key in ["mean", "stddev", "min", "max", "p25", "p50", "p75", "count"]:
        assert key in data


def test_aggregate_correct_values(client):
    client.post("/import", content=VALID_XML, headers={"Content-Type": "text/xml+markr"})
    response = client.get("/results/1234/aggregate")
    data = response.json()
    assert data["mean"] == 65.0
    assert data["count"] == 1


def test_aggregate_test_not_found(client):
    response = client.get("/results/99999/aggregate")
    assert response.status_code == 404


# --- duplicate handling ---

def test_duplicate_keeps_highest_obtained(client):
    low = b"""
    <mcq-test-results>
        <mcq-test-result>
            <student-number>111</student-number>
            <test-id>5678</test-id>
            <summary-marks available="10" obtained="3" />
        </mcq-test-result>
    </mcq-test-results>
    """
    high = b"""
    <mcq-test-results>
        <mcq-test-result>
            <student-number>111</student-number>
            <test-id>5678</test-id>
            <summary-marks available="10" obtained="8" />
        </mcq-test-result>
    </mcq-test-results>
    """
    client.post("/import", content=low, headers={"Content-Type": "text/xml+markr"})
    client.post("/import", content=high, headers={"Content-Type": "text/xml+markr"})
    response = client.get("/results/5678/aggregate")
    data = response.json()
    assert data["max"] == 80.0  

def test_duplicate_in_single_request_keeps_highest(client):
    xml = b"""
    <mcq-test-results>
        <mcq-test-result>
            <student-number>111</student-number>
            <test-id>9999</test-id>
            <summary-marks available="10" obtained="3" />
        </mcq-test-result>
        <mcq-test-result>
            <student-number>111</student-number>
            <test-id>9999</test-id>
            <summary-marks available="10" obtained="8" />
        </mcq-test-result>
    </mcq-test-results>
    """
    client.post("/import", content=xml, headers={"Content-Type": "text/xml+markr"})
    response = client.get("/results/9999/aggregate")
    data = response.json()
    assert data["count"] == 1
    assert data["max"] == 80.0