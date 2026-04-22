import xml.etree.ElementTree as ET
import statistics

from app.models.domain_models import TestResult
from app.errors.exceptions import (
    InvalidRootTagError,
    InvalidXMLFormatError,
    MissingRequiredFieldError,
    TestNotFoundError,
)


class ResultService:
    def __init__(self, repo):
        self.repo = repo

    # POST requests

    def process_results_and_save(self, xml_data):
        raw_results = self._parse_and_validate_xml(xml_data)
        compiled_results = []

        for item in raw_results:
            compiled = self._normalise_required_data(item)
            compiled_results.append(compiled)

        # build domain model
        results = []

        for data in compiled_results:
            result = TestResult(
                student_number=data["student_number"],
                test_id=data["test_id"],
                marks_obtained=data["marks_obtained"],
                marks_available=data["marks_available"],
            )
            results.append(result)

        # resolve any duplicate entries, only reached if all valid
        for result in results:
            self._handle_existing_entries(result)

        return results


    def _parse_and_validate_xml(self, xml_data):
        # parse incoming data
        try:
            root = ET.fromstring(xml_data)
        except ET.ParseError as e:
            raise InvalidXMLFormatError(f"Malformed XML: {e}")

        # check for required root tag
        if root.tag != "mcq-test-results":
            raise InvalidRootTagError(
                f"Expected root tag <mcq-test-results> but got <{root.tag}>"
            )

        # extract required fields only
        result_elements = root.findall("mcq-test-result")
        if not result_elements:
            raise MissingRequiredFieldError("No <mcq-test-result> elements found in XML")
        
        raw_results = []
        for element in result_elements:
            summary = element.find("summary-marks")
            if summary is None:
                raise MissingRequiredFieldError("Required field <summary-marks> is missing")

            required = {
                "student_number": element.findtext("student-number"),
                "test_id": element.findtext("test-id"),
                "marks_available": summary.get("available"),
                "marks_obtained": summary.get("obtained"),
            }

            for key, value in required.items():
                if value is None:
                    raise MissingRequiredFieldError(
                        f"Required field '{key}' is missing"
                    )

            raw_results.append(required)
        
        return raw_results


    def _normalise_required_data(self, raw):
        return {
            "student_number": raw["student_number"].strip(),
            "test_id": raw["test_id"].strip(),
            "marks_available": int(raw["marks_available"].strip()),
            "marks_obtained": int(raw["marks_obtained"].strip()),
        }


    def _handle_existing_entries(self, new_result):
        existing = self.repo.get_by_student_and_test(
            new_result.student_number,
            new_result.test_id
        )

        # if no existing record, save new record
        if existing is None:
            self.repo.save(new_result)
            return

        # first, prioritise the scan with highest available marks
        if new_result.marks_available > existing.marks_available:
            self.repo.save(new_result)
            return

        # if available is equal, prefer the higher obtained score
        if (
            new_result.marks_available == existing.marks_available and
            new_result.marks_obtained > existing.marks_obtained
        ):
            self.repo.save(new_result)


    # GET queries

    def generate_analytics(self, test_id):
        results = self.repo.get_by_test_id(test_id)
        marks = []

        for result in results:
            marks.append(result.percentage())

        if not marks:
            raise TestNotFoundError(
                f"No results found for test_id '{test_id}'"
            )

        # calculate percentiles as required
        q1, q2, q3 = statistics.quantiles(marks, n=4)

        return {
            "mean": self._round(statistics.mean(marks)),
            "stddev": self._round(statistics.pstdev(marks)),
            "min": self._round(min(marks)),
            "max": self._round(max(marks)),
            "p25": self._round(q1),
            "p50": self._round(q2),
            "p75": self._round(q3),
            "count": len(marks),
        }

    def _round(self, x):
        return round(x, 1)