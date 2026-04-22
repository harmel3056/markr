# Markr: Data Ingestion & Processing Service

A FastAPI microservice that parses MCQ test results from legacy grading machines and produces analytics for the visualisation team.

---

## How to run it

**Requirements:** Docker and Docker Compose.

From the project root:

```bash
docker-compose up --build
```

This builds the image, starts the service on port **4567**, and creates the SQLite database on first run.

Data is persisted to `./data/markr.db` via a Docker volume, so it survives container restarts.

### Import sample data

```bash
curl -X POST \
  -H 'Content-Type: text/xml+markr' \
  --data-binary @app/tests/sample_results.xml \
  http://localhost:4567/import
```

### Query an aggregate

```bash
curl http://localhost:4567/results/9863/aggregate
```

### Run the test suite locally

```bash
python -m pytest app/tests/unit_tests.py -v
```

### API docs

Swagger UI is available at:

```jsx
http://localhost:4567/docs
```

---

## Approach

I started by breaking the brief into its essentials, so that I would have a concrete list to work with, and began a list of assumptions. From there, I sketched out a plan for myself based on the criteria, with emphasis on:

- loose architecture framework with some pseudocode
- researching unknowns (XML parsing, ideal Docker patterns, SQLite)
- updating README documentation as I go

I wanted to implement a build that reflects my values in coding. My key concerns were clarity, portability, extensibility and - of course - functionality. The infrastructure therefore features a DDD-lite approach, where each layer serves a specific purpose, and would make it straightforward to swap the persistence layer or extend the service without a significant refactor. 

**Key considerations**

- **Framework:** FastAPI was a good option for a quick(ish) build, while keeping routing, validation, and testing simple and explicit
- **For persistence:** I chose SQLite (via SQLAlchemy) as a lightweight persistence option that needs no external services. I implemented in-memory storage initially, as I wanted to be able to run end-to-end testing to surface any logic bugs independently of any bugs that could crop up during Docker and SQLite implementation.
- **Validation and error handling:** Pydantic models validate the shape of outgoing data only, as the brief identified that strict validation of incoming data would be the wrong choice.
Exceptions are raised in the service layer and bubble up to a dedicated exception-handler layer, which provides a layer of abstraction from the business logic, makes the service portable, and also facilitates smoother testing.
- **Testing:** I built a list of edge cases that I wanted to test as I was building, so I used AI assistance to generate a small testing suite for them. This actually surfaced a couple of bugs that I was able to fix, so I would love to expand this further.

**Key data flow:**

```bash
Request
  ↓
Router (validates content-type, applies request/response schemas)
  ↓
Service (parses XML, validates, builds domain model, applies business logic)
  ↓
Repository (fetches/stores data)
  ↓
Domain Model (returned to service)
  ↓
Router (applies response schema)
  ↓
Response
```

---

## Assumptions

- `<summary_marks>` is adequate to proceed with as our “source of truth”
- POST requests come with content-type `text/xml+markr` so we assume that no other types of requests should be permitted. We are aware that there are other kinds of XML documents but the brief states they are not applicable.
- We validate that the XML root element is `<mcq-test-results>` based upon the examples provided
- curl test provided for `GET` queries models the desired outcome - the min, max, and stddev were not spelled out but if that is the expected output then it seemed like the right direction to take
- Using port 4567 in my docker-compose to match the curl example
- `scanned-on` field not touched in notation and, based on the fact that it didn’t appear in the curl example, I believe it might be some of the excess data not required for our purposes, have ignored
- `<first-name>` and `<last-name>` constitute unessential data, given that they don’t serve the generation of report data and students can be identified with their `<student-number>`, perhaps this will act as foreign key if extensibility is required.
- I prioritised the scan with the highest `<available>` marks because this value reflects how much of the test was actually visible to the scanner. In theory, a folded or partially obscured page would reduce the available marks, so the scan with the highest available value should represent the most complete version of the test. When two scans show the same available marks, I then let priority fall to the one with the higher obtained score seeing as both scans captured the full test and the higher score is [again, theoretically] the more accurate result.
- Round aggregate numbers to one decimal point in alignment with the data provided in curl test example provided

---

## Notes on the implementation

- **Whole‑document atomicity:** upon POST request, the service fully processes the entire XML payload before allowing a `save` action to be completed. If an entry is invalid, the entire document is rejected
- **Duplicate handling:** multiple scans for the same student/test are resolved using a clear priority rule (highest `available` marks, then highest `obtained`)
- **Minimal required fields:** only fields needed for analytics are parsed; unused fields like `<first-name>`, `<last-name>`, and `scanned-on` are ignored
- **Stable aggregate output:** the aggregate endpoint returns the JSON shape demonstrated in the curl example, including rounding to one decimal place
- **Restart‑safe persistence:** data survives container restarts as required
- **Clear error responses:** unsupported content types, malformed XML, wrong root tags, and missing fields all produce explicit, consistent errors

---

## Performance & scalability

The current implementation computes aggregates at read time by querying all rows for a given `test_id`.This is perfectly adequate for the sake of building out a prototype, however if the API were to scale for a real-time dashboard scenario I can see that the workload is heavily weighted at read time. If we shifted the focus to pre-computing the aggregate values at save time it would dramatically speed up the read time (and admittedly slow the save time, but I would consider that a favourable trade-off).

Overall, my implementation has been designed with portability in mind: the domain, service, and persistence layers all operate independently, with just the routers as the wiring. The brief hinted that this prototype could eventually be used in practice, which was grounding for the decision to keep the layers clean and swappable. If the system grows, the service layer can evolve without touching the API, and the same with the persistence layer which can essentially be replaced or extended without interrupting the core logic.