# CyBreach Module 2 — The Validator (Pod Beta)

Detection validation and evidence verification services for the CyBreach
platform. Given a simulated attack's evidence event and a set of detection
rules, this pipeline answers one question: **did the defensive stack
actually see it, and can we prove it?**

Built against the frozen Module 2 contracts, following a zero-interdependency
model — no other module's live code is required to build or test this.
Module 1's evidence events and detection rules are consumed as versioned
JSON fixtures under `contracts/`.

## What it does

For every simulated attack action, the pipeline produces one of four
verdicts, each backed by a step-by-step causal chain:

| Verdict    | Meaning                                                   |
|------------|------------------------------------------------------------|
| `Detected` | The rule fired and matched the expected observable          |
| `Partial`  | Some evidence matched, but not everything expected          |
| `Missed`   | The rule exists but nothing fired — a real coverage gap      |
| `NoData`   | No rule maps to this technique, or the connector was down    |

A hard rule is enforced in code, not just policy: **a verdict of `Missed`
or `NoData` can never carry a regulatory control reference.** No security
control is ever marked as satisfied without linked, validated evidence.

## Architecture
