"""
Cross-pod integration test: Validation Engine -> Outcome Classifier ->
Verdict Publisher, run against the frozen mock evidence/rule fixtures.

This is the Week 12 Pod Beta deliverable from the execution plan:
  1. Run the full Validation Engine integration test suite using mock
     evidence events; confirm correct generation across all 4 verdict
     classes with accurate causal chains and confidence scores.
  2. Test end-to-end integration across Validation Engine, Outcome
     Classifier, and Verdict Publisher; verify verdicts flow correctly
     through the full pipeline, including out to the message bus that
     Module 3 and Module 4 both consume.
"""
import json

import pytest

from services.outcome_classifier.app.classifier import OutcomeClassifier
from services.validation_engine.app.engine import ValidationEngine
from services.verdict_publisher.app.kafka_client import MockMessageBus
from services.verdict_publisher.app.publisher import VerdictPublisher, VERDICT_TOPIC

from tests.integration.conftest import EXPECTED_VERDICTS


# A control ref is only offered up for the two techniques with a mapped
# NIST CSF control in this fixture set, to mirror how Module 3's real
# control registry would only cover some techniques.
CONTROL_REF_BY_TECHNIQUE = {
    "T1486": ["NIST-CSF-DE.CM-1"],
    "T1098": ["NIST-CSF-PR.AC-4"],
}


@pytest.mark.asyncio
async def test_full_pipeline_produces_all_four_verdict_classes(
    evidence_events, detection_rules, connector_registry
):
    engine = ValidationEngine(connector_registry)
    classifier = OutcomeClassifier()
    bus = MockMessageBus()
    publisher = VerdictPublisher(bus)

    published = {}
    for evidence in evidence_events:
        raw = await engine.validate(evidence, detection_rules)
        verdict = classifier.classify(
            raw, regulatory_control_refs=CONTROL_REF_BY_TECHNIQUE.get(evidence.technique_ref)
        )
        event = await publisher.publish(verdict, tenant_id="tenant-demo")
        published[evidence.action_id] = (verdict, event)

    # -- 1. every action got the verdict the scenario was designed for --
    for action_id, expected_verdict in EXPECTED_VERDICTS.items():
        verdict, _event = published[action_id]
        assert verdict.verdict == expected_verdict, f"{action_id} expected {expected_verdict}, got {verdict.verdict}"

    # -- 2. all four verdict classes actually appeared in this one batch --
    produced_classes = {verdict.verdict for verdict, _ in published.values()}
    assert produced_classes == {"Detected", "Missed", "Partial", "NoData"}

    # -- 3. causal chains are always populated, for every verdict class --
    for verdict, _event in published.values():
        assert len(verdict.causal_chain) >= 2

    # -- 4. confidence scores match what the doc's own DET-005 example expects --
    detected_verdict, _ = published["act-001"]
    partial_verdict, _ = published["act-003"]
    missed_verdict, _ = published["act-002"]
    assert detected_verdict.confidence == 1.0
    assert partial_verdict.confidence == 0.5
    assert missed_verdict.confidence == 0.0

    # -- 5. MTTD only computed for Detected, never for the other three --
    assert detected_verdict.mttd_seconds == 5.0
    for action_id in ("act-002", "act-003", "act-004", "act-005"):
        assert published[action_id][0].mttd_seconds is None

    # -- 6. evidence-backed compliance: only Detected/Partial ever carry a
    #        control ref, and only when the caller supplied one for that
    #        technique (T1098 -> Partial here, still gets credited) --
    assert detected_verdict.regulatory_control_refs == ["NIST-CSF-DE.CM-1"]
    assert partial_verdict.regulatory_control_refs == ["NIST-CSF-PR.AC-4"]
    assert missed_verdict.regulatory_control_refs == []
    no_data_verdict_1, _ = published["act-004"]
    no_data_verdict_2, _ = published["act-005"]
    assert no_data_verdict_1.regulatory_control_refs == []
    assert no_data_verdict_2.regulatory_control_refs == []


@pytest.mark.asyncio
async def test_pipeline_output_conforms_to_the_frozen_verdict_schema(
    evidence_events, detection_rules, connector_registry
):
    with open("contracts/verdict_schema.json") as f:
        schema = json.load(f)

    engine = ValidationEngine(connector_registry)
    classifier = OutcomeClassifier()
    bus = MockMessageBus()
    publisher = VerdictPublisher(bus)

    evidence = evidence_events[0]  # act-001, the Detected scenario
    raw = await engine.validate(evidence, detection_rules)
    verdict = classifier.classify(raw)
    event = await publisher.publish(verdict, tenant_id="tenant-demo")

    dumped = event.model_dump()
    for field in schema["required"]:
        assert field in dumped, f"published event missing contract field: {field}"
    assert dumped["verdict"] in schema["verdict_enum"]
    assert len(dumped["content_hash"]) == 64


@pytest.mark.asyncio
async def test_module_3_and_module_4_each_receive_every_verdict_event(
    evidence_events, detection_rules, connector_registry
):
    """Cross-pod consumer check: two independent consumer groups on the
    verdict topic must each see a full, identical copy of the batch."""
    engine = ValidationEngine(connector_registry)
    classifier = OutcomeClassifier()
    bus = MockMessageBus()
    publisher = VerdictPublisher(bus)

    for evidence in evidence_events:
        raw = await engine.validate(evidence, detection_rules)
        verdict = classifier.classify(raw)
        await publisher.publish(verdict, tenant_id="tenant-demo")

    module3_batch = bus.get_messages(VERDICT_TOPIC, "module3")
    module4_batch = bus.get_messages(VERDICT_TOPIC, "module4")

    assert len(module3_batch) == len(evidence_events)
    assert len(module4_batch) == len(evidence_events)
    assert module3_batch == module4_batch  # identical, independent copies
    assert bus.lag(VERDICT_TOPIC, "module3") == 0
    assert bus.lag(VERDICT_TOPIC, "module4") == 0


@pytest.mark.asyncio
async def test_verdict_events_are_immutable_end_to_end(
    evidence_events, detection_rules, connector_registry
):
    from pydantic import ValidationError

    engine = ValidationEngine(connector_registry)
    classifier = OutcomeClassifier()
    bus = MockMessageBus()
    publisher = VerdictPublisher(bus)

    evidence = evidence_events[0]
    raw = await engine.validate(evidence, detection_rules)
    verdict = classifier.classify(raw)
    event = await publisher.publish(verdict, tenant_id="tenant-demo")

    with pytest.raises(ValidationError):
        event.confidence = 0.0
