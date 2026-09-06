# Outcome Classifier - Security Validation

## Overview

The **Outcome Classifier** is a security validation component designed to analyze detection evidence and classify security validation results into meaningful verdicts.

It evaluates whether a security detection rule successfully identified the expected activity and produces one of four outcomes:

* **Detected** - The expected malicious activity was successfully detected.
* **Partial** - Some expected evidence or detection conditions were matched.
* **Missed** - The expected activity was not detected.
* **NoData** - Required evidence was unavailable or insufficient for validation.

The project also provides **causal chain analysis, alert fidelity assessment, and MTTD (Mean Time to Detect) calculation** to make security validation results explainable and measurable.

## Key Features

### 1. Outcome Classification

Classifies validation results into:

```text
Detected
Partial
Missed
NoData
```

The classification is based on factors such as detection evidence, confidence, and matched security events.

### 2. Causal Chain Analysis

Generates an explainable chain showing how the available evidence led to the final security verdict.

This helps security teams understand **why a detection was classified as Detected, Partial, Missed, or NoData**.

### 3. Alert Fidelity Assessment

Evaluates the quality of generated security alerts based on factors such as:

* Technique specificity
* Required field coverage
* Detection quality
* Available evidence

Alerts can be categorized as:

```text
High Fidelity
Medium Fidelity
Low Fidelity
```

### 4. MTTD Calculation

Calculates **Mean Time to Detect (MTTD)** to measure how quickly security detections identify simulated or observed security activity.

MTTD can help security teams evaluate and improve detection performance.

### 5. REST API

The application provides REST APIs using **FastAPI**, allowing other services to submit validation evidence and retrieve security verdicts.

FastAPI also provides automatic OpenAPI/Swagger API documentation.

### 6. Automated Testing

The project uses **Pytest** for unit and integration testing.

Contract tests verify that generated verdicts conform to the project's frozen schemas.

---

## Technology Stack

| Technology     | Purpose                    |
| -------------- | -------------------------- |
| Python 3.12    | Backend development        |
| FastAPI        | REST API framework         |
| Pydantic       | Data validation and models |
| Pytest         | Automated testing          |
| MITRE ATT&CK   | Security technique mapping |
| PostgreSQL     | Persistent data storage    |
| Redis          | Caching                    |
| Kafka/Redpanda | Event streaming            |
| Docker         | Containerized development  |
| React          | Frontend/dashboard         |
| TypeScript     | Frontend development       |
| Tailwind CSS   | UI styling                 |

The broader Validator platform uses PostgreSQL, Redis, Kafka/Redpanda, React, TypeScript, Tailwind CSS, and Docker alongside the Python/FastAPI backend.

---

## Project Structure

```text
module2-validator/
│
├── services/
│   ├── validation_engine/
│   │   └── app/
│   │
│   ├── outcome_classifier/
│   │   └── app/
│   │       ├── classifier.py
│   │       ├── causal_chain.py
│   │       ├── confidence.py
│   │       ├── matcher.py
│   │       └── mttd.py
│   │
│   └── ...
│
├── contracts/
│   ├── verdict_schema.json
│   ├── connector_spec.json
│   └── evidence_fixture.json
│
├── tests/
│
├── docker/
│
├── docs/
│
├── requirements.txt
└── README.md
```

The project specification defines the Validator around services including the **Validation Engine and Outcome Classifier**, with frozen contracts for verdicts, connectors, and evidence.

---

## How the Classification Works

The general validation flow is:

```text
Security Rule
      │
      ▼
Validation Engine
      │
      ▼
Evidence Collection
      │
      ▼
Evidence Matching
      │
      ▼
Confidence Assessment
      │
      ▼
Outcome Classifier
      │
      ├── Detected
      ├── Partial
      ├── Missed
      └── NoData
      │
      ▼
Causal Chain + Fidelity + MTTD
      │
      ▼
Security Verdict
```

---

## Example Input

```json
{
  "action_id": "action-001",
  "confidence": 0.9,
  "matched_events": [
    {
      "alert_name": "Suspicious Login Detection"
    }
  ]
}
```

## Example Output

```json
{
  "outcome": "Detected",
  "confidence": 0.9,
  "alert_fidelity": "High",
  "causal_chain": [
    "Security activity observed",
    "Relevant event matched",
    "Detection condition satisfied",
    "Verdict generated"
  ]
}
```

*The exact response fields depend on the implemented API/schema.*

---

## Installation

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd module2-validator
```

### 2. Create a Virtual Environment

```bash
python3.12 -m venv .venv
```

Activate it:

**Linux/macOS**

```bash
source .venv/bin/activate
```

**Windows**

```powershell
.venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Start Infrastructure

If Docker Compose is configured:

```bash
docker compose up -d
```

The development environment uses services such as PostgreSQL, Redis, and Kafka.

### 5. Run Database Migrations

```bash
alembic upgrade head
```

---

## Running the Application

Start the FastAPI application:

```bash
uvicorn services.validation_engine.app.main:app --reload --port 8002
```

Verify that the service is running:

```bash
curl http://localhost:8002/health
```

The documented local development process uses port `8002` and provides a health endpoint for verification.

---

## API Documentation

After starting the FastAPI server, API documentation can be accessed through:

```text
http://localhost:8002/docs
```

FastAPI automatically generates interactive OpenAPI/Swagger documentation.

---

## Testing

Run the complete test suite:

```bash
pytest
```

Run tests with coverage:

```bash
pytest --cov=services --cov-report=term-missing
```

Contract tests validate that the generated verdict contains the required schema fields and that the verdict event receives a SHA-256 content hash.

---

## Contract Validation

The project uses frozen contracts to ensure consistent communication between services.

Important contract files include:

```text
contracts/
├── verdict_schema.json
├── connector_spec.json
└── evidence_fixture.json
```

Contract testing verifies that the implementation consumes and produces data according to the published schemas.

---

## Security Considerations

The project follows several security and engineering practices:

* No hardcoded credentials or secrets
* Environment variables/vaults for sensitive configuration
* Type hints for Python functions
* Meaningful error handling
* Automated testing
* Contract validation
* Immutable verdict events
* Read-only SIEM connectors
* OCSF data provenance tracking
* Current API documentation

These practices are part of the project's technical quality and security checklist.

---

## Future Improvements

Potential improvements include:

* Additional SIEM integrations
* Advanced detection scoring
* More MITRE ATT&CK technique mappings
* Improved causal-chain visualization
* Real-time validation dashboards
* Additional automated integration tests
* Performance and load testing
* Enhanced alert fidelity algorithms

---

## Learning Outcomes

This project provides practical experience with:

* Python backend development
* FastAPI REST APIs
* Security detection validation
* SIEM concepts
* Security alert analysis
* MITRE ATT&CK
* Evidence matching
* Alert fidelity
* MTTD calculation
* Automated testing
* API contract validation
* Docker-based development
* Redis caching
* Event-driven architecture

---

## Author

**Aluru Rajanikanth**

Cybersecurity | Network Security | SOC | Python

GitHub: `https://github.com/rajini72342`

---

## Disclaimer

This project is intended for **educational, development, and authorized security-testing purposes only**.

Use the validation and security-testing capabilities only against systems and environments for which you have explicit authorization.
