# Child Welfare Early Risk Signal Prototype

## Overview

This repository contains a **prototype decision-support system** designed to help child welfare agencies **surface early risk signals** that may warrant human review. The system is **advisory only**, **human-in-the-loop at all times**, and **not an automated decision or enforcement tool**.

The prototype is intended for **limited pilot evaluation** under local governance, with **independent validation required** prior to any broader use.

## What This Is

* A **prevention-oriented prototype** that aggregates and scores signals for **early attention**
* A **technical exploration** of low-cost, resilient system design for constrained environments
* A **human decision-support aid**, not a replacement for professional judgment

## What This Is Not

* Not a production system
* Not an automated decision-maker
* Not an enforcement or investigative tool
* Not a guaranteed predictor of outcomes
* Not validated on real-world ground-truth datasets

## Core Principles

### Human-in-the-Loop (Mandatory)

All outputs are **recommendations only**.
Human operators retain **full authority, discretion, and accountability**.

### Conservative Claims

This repository intentionally avoids performance, cost, or outcome claims.
Any evaluation is **forward-looking** and must be independently conducted.

### Governance by Design

Explicit boundaries on system claims, usage, and communication are enforced via repository governance artifacts.

## Intended Use (Pilot Scope)

This prototype is suitable for:

* A **single jurisdiction pilot**
* A **defined review workflow**
* **Advisory use only**, alongside existing processes
* Evaluation by technical, legal, and ethics reviewers

See: `docs/pilot.md` for a constrained pilot outline.

## Repository Structure (High-Level)

```
README.md                ← Public-facing overview (this file)
.claims_lock             ← Governance: allowed claims and language
docs/
  pilot.md               ← Pilot scope and adoption pathway
  technical/             ← Algorithm design and system architecture
ontology/                ← Conceptual models (private / internal use)
control/                 ← Execution and orchestration layer
```

## Data & Evaluation

* No live case data is included
* No claims are made about accuracy or outcomes
* Any metrics referenced in technical documents are **simulated or synthetic**
* Real-world evaluation requires:

  * Approved datasets
  * Independent validation
  * Local policy authorization

## Safety & Accountability

* Human review is required for all outputs
* The system cannot act autonomously
* Local agencies define thresholds, workflows, and safeguards
* Operators remain accountable for all decisions

## Status

**Prototype. Pilot-ready under constrained scope.**
**Independent validation required before any expansion.**

## Contact / Stewardship

This repository is stewarded with an emphasis on:

* Safety
* Restraint
* Transparency
* Institutional compatibility

Contributions or deployments must comply with `.claims_lock`.