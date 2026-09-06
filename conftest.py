"""
Shared fixtures for unit + integration tests: loads the frozen mock
data and wires up a MockConnector per vendor with canned results that
deliberately produce one of each of the four verdict classes.

Scenario map (matches contracts/evidence_fixture.json):
  act-001 / DET-001 (splunk)   -> full indicator match       -> Detected
  act-002 / DET-002 (sentinel) -> empty query results        -> Missed
  act-003 / DET-005 (splunk)   -> partial indicator match    -> Partial
  act-004 (T1548.002)          -> no rule maps to technique  -> NoData
  act-005 / DET-003 (qradar)   -> connector unavailable      -> NoData
"""
import json
from pathlib import Path

import pytest

from services.connector_framework.app.base_connector import ConnectorConfig
from services.connector_framework.app.connectors.mock_connector import MockConnector
from services.connector_framework.app.registry import ConnectorRegistry
from services.validation_engine.app.models import DetectionRule, EvidenceEvent

CONTRACTS_DIR = Path(__file__).resolve().parents[2] / "contracts"


@pytest.fixture
def evidence_events():
    data = json.loads((CONTRACTS_DIR / "evidence_fixture.json").read_text())
    return [EvidenceEvent(**item) for item in data]


@pytest.fixture
def detection_rules():
    data = json.loads((CONTRACTS_DIR / "detection_rules_fixture.json").read_text())
    return [DetectionRule(**item) for item in data]


@pytest.fixture
def connector_registry():
    registry = ConnectorRegistry()

    splunk = MockConnector(
        ConnectorConfig(connector_id="splunk-1", vendor="splunk"),
        canned_results={
            "DET-001": [
                {
                    "host": "host-fileserver-01",
                    "Image": "C:\\Windows\\System32\\vssadmin.exe",
                    "CommandLine": "vssadmin.exe delete shadows /all /quiet && cipher /e",
                    "_time": "2026-06-01T10:00:05Z",
                }
            ],
            "DET-005": [
                {
                    "eventName": "AttachUserPolicy",
                    "user": "svc-deploy",
                    "sourceIPAddress": "10.0.0.5",
                    "_time": "2026-06-01T10:10:03Z",
                }
            ],
        },
    )

    sentinel = MockConnector(
        ConnectorConfig(connector_id="sentinel-1", vendor="sentinel"),
        canned_results={
            "DET-002": [],  # queried fine, found nothing -> Missed
        },
    )

    qradar = MockConnector(
        ConnectorConfig(connector_id="qradar-1", vendor="qradar"),
        canned_results={},
        unavailable_rule_ids=["DET-003"],  # simulate SIEM outage -> NoData
    )

    registry.register("splunk", splunk)
    registry.register("sentinel", sentinel)
    registry.register("qradar", qradar)
    return registry


EXPECTED_VERDICTS = {
    "act-001": "Detected",
    "act-002": "Missed",
    "act-003": "Partial",
    "act-004": "NoData",
    "act-005": "NoData",
}
