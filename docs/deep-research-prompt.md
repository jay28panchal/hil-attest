# Deep-research prompt for hil-attest

Copy the prompt below into a research-capable AI. It is intentionally written
to challenge the project rather than justify a predetermined answer.

---

You are a senior embedded-systems engineer, open-source maintainer, software
supply-chain security researcher, and developer-tools product strategist.

Conduct a rigorous, source-backed investigation of the following proposed
open-source project. Your job is to determine whether it solves a real,
underserved problem. Do not assume the idea is good. Recommend GO, PIVOT, or
NO-GO based on evidence.

## Proposed project

Working name: hil-attest

Concept: a vendor-neutral, cross-platform CLI that binds exact firmware
artifacts to physical hardware-in-the-loop test evidence using standard in-toto
attestation formats.

Inputs may include:

- one or more firmware artifacts such as ELF, HEX, BIN, UF2, or full images;
- JUnit XML from pytest, pytest-embedded, Zephyr Twister, labgrid, LAVA,
  OpenHTF, or custom test systems;
- privacy-safe device-under-test metadata such as board, SoC, hardware
  revision, transport, runner, and a one-way device identifier;
- UART, SEGGER RTT, OpenOCD, GDB, power, network, or other test logs;
- an optional CI or laboratory-run URL.

Initial output: a deterministic in-toto Statement v1 using the Test Result
v0.1 predicate. Firmware artifacts are subjects. Test configuration, DUT
metadata, and evidence are represented by resource descriptors and SHA-256
digests. The tool validates internal consistency and can recompute artifact
digests offline.

Longer-term possibilities include Sigstore/cosign signing, GitHub Actions
integration, release-policy checks, adapters for Zephyr and ESP-IDF, physical
runner identity, replay protection, and reusable verification policies.

The initial maintainer has practical experience with nRF52/nRF54, Zephyr/nRF
Connect SDK, UART, SEGGER J-Link RTT, BLE, OpenWrt gateways, Python, C/C++, and
Linux-based firmware tooling.

## Non-negotiable principles

1. Do not design a repository merely to qualify for grants, free subscriptions,
   stars, or publicity.
2. Do not claim that an unsigned JSON statement proves a physical test occurred.
3. Do not invent adoption, users, downloads, partnerships, benchmarks, or
   hardware verification.
4. Prefer established standards and upstream contributions over new proprietary
   schemas.
5. Protect raw device identifiers, credentials, customer logs, source paths,
   and other sensitive laboratory information.
6. Distinguish fixture tests, emulation, and real-hardware verification.
7. Treat grant eligibility as a secondary consequence of authentic maintenance
   and adoption, never as evidence that the project is useful.

## Research questions

### 1. Problem validation

- How do embedded teams currently prove that an exact firmware digest passed
  tests on a physical device?
- Where do build provenance, test reports, lab-controller records, and device
  logs become disconnected?
- Find primary evidence in issue trackers, discussions, specifications,
  conference talks, maintainer documentation, or engineering reports.
- Identify at least three concrete failure scenarios, such as evidence attached
  to the wrong binary, renamed artifacts, stale logs, incorrect board revision,
  replayed results, or unverifiable outsourced-manufacturing tests.
- Separate regulated or high-assurance needs from ordinary developer
  convenience.

### 2. Existing standards

Read the current primary specifications, not summaries:

- in-toto Statement and ResourceDescriptor specifications;
- in-toto Test Result predicate;
- SLSA provenance and verification model;
- Sigstore/cosign bundles and signing/verification flows;
- GitHub artifact attestations and custom-predicate capabilities;
- SPDX and CycloneDX only where relevant.

Determine:

- whether the existing Test Result predicate can correctly represent HIL runs;
- whether DUT identity belongs in configuration, evidence, another existing
  predicate, or a separate linked attestation;
- whether hil-attest should generate only a statement, a DSSE envelope, a
  Sigstore bundle, or multiple layers;
- which fields are required, optional, prohibited, or ignored by conforming
  consumers;
- how canonicalization and deterministic serialization should work;
- whether an upstream contribution would be better than a standalone schema.

### 3. Competitor and substitute analysis

Investigate current releases and primary repositories for at least:

- pytest-embedded;
- Zephyr Twister and Zephyr coredump tooling;
- labgrid;
- LAVA;
- OpenHTF;
- Memfault or comparable embedded observability systems;
- GitHub artifact attestations;
- in-toto and Sigstore tooling;
- relevant Jenkins, GitLab, Buildkite, or Tekton test-evidence features;
- firmware release systems that already bind hardware results to artifacts.

Create a comparison table containing:

- project and canonical URL;
- license and governance;
- maintained status and latest meaningful activity;
- supported devices/frameworks;
- firmware hashing;
- JUnit ingestion;
- physical DUT identity;
- log/evidence hashing;
- standard attestation output;
- cryptographic signing;
- offline verification;
- release-policy enforcement;
- adoption indicators;
- exact overlap with the proposal;
- unresolved gap, if any.

Do not treat GitHub stars alone as proof of user need.

### 4. User and maintainer demand

Define the primary users precisely. Consider:

- individual firmware developers;
- open-source RTOS and board maintainers;
- hardware-in-the-loop CI operators;
- device manufacturers and contract manufacturers;
- release/security engineers;
- regulated-device teams;
- AI coding agents that can build firmware but cannot honestly claim physical
  verification.

For each group, document:

- current workflow;
- pain severity and frequency;
- existing workaround;
- who controls signing keys and lab workers;
- willingness to add another CLI;
- integration constraints;
- what evidence would make the output trustworthy.

Propose ten interview questions that do not lead respondents toward the idea.
Define what answers would disprove the need.

### 5. Threat model

Model at least these threats:

- modified or substituted firmware;
- modified logs or JUnit XML;
- false DUT metadata;
- a compromised HIL runner;
- replay of an old passing result;
- a valid test run against the wrong hardware revision;
- forged or stolen signing identity;
- nondeterministic test configuration;
- leakage of serial numbers, MAC addresses, source paths, secrets, and customer
  data;
- maliciously large XML or JSON;
- path traversal and unsafe file handling;
- SHA-256 name collisions caused by duplicate basenames;
- confusion between simulation and physical hardware.

State which threats the MVP can mitigate, which require signing or trusted
hardware, and which remain organizational controls.

### 6. Technical feasibility

Evaluate a Python 3.10+, dependency-light implementation on Windows, macOS, and
Linux.

Review:

- safe JUnit parsing and file-size limits;
- multi-artifact subjects;
- canonical privacy-safe DUT JSON;
- evidence resource descriptors;
- deterministic byte-for-byte output;
- schema validation;
- offline verification;
- error handling and exit codes;
- compatibility with PowerShell, Bash, and CI runners;
- packaging through PyPI and standalone executables;
- signing integrations that do not require private keys in source repositories.

Recommend a versioned data contract and compatibility policy.

### 7. MVP and roadmap

Define the smallest credible MVP. At minimum assess:

- create command;
- verify command;
- inspect command;
- multiple firmware artifacts;
- JUnit parsing;
- DUT metadata validation;
- privacy guardrails;
- evidence digests;
- deterministic output;
- cross-platform unit tests;
- example fixtures;
- documentation that clearly limits trust claims.

Then define:

- version 0.2 signing and verification;
- version 0.3 framework adapters;
- a physical nRF52840 pilot;
- an ESP32/pytest-embedded pilot;
- a public CI example;
- upstream collaboration with in-toto or test-framework maintainers.

Avoid a large GUI until command-line adoption proves a need.

### 8. Adoption strategy

Design an ethical path to real usage:

- publish a clear problem statement and design discussion before promotion;
- request review from relevant upstream maintainers;
- integrate with one existing open-source firmware example;
- document real physical-board runs separately from fixtures;
- create issues suitable for first-time contributors;
- publish a compatibility matrix;
- provide reproducible examples and release artifacts;
- ask users for workflow feedback rather than stars.

Define measurable 30-, 60-, and 90-day goals. Include external users,
integrations, bug reports, contributors, releases, and upstream feedback.

### 9. Falsification and stop conditions

Explicitly recommend PIVOT or NO-GO if research shows any of the following:

- a mature maintained tool already solves the same problem;
- in-toto or GitHub already provides a straightforward official workflow;
- teams do not need portable evidence outside their lab system;
- trustworthy physical identity makes a dependency-light CLI impractical;
- the tool adds ceremony without improving a real release decision;
- no external maintainer validates the problem after focused outreach.

Suggest the best upstream contribution or narrower pivot if a standalone
project is unjustified.

### 10. Open-source and governance

Recommend:

- project name after collision and trademark checks;
- MIT versus Apache-2.0 with practical tradeoffs;
- governance and maintainer expectations;
- contribution, security, and disclosure policies;
- release cadence and semantic versioning;
- artifact signing and trusted publishing;
- documentation required before calling the project production-ready.

### 11. Program-fit analysis

Read the current official Codex for Open Source criteria and terms. Explain
accurately:

- why no repository can guarantee acceptance;
- which objective evidence OpenAI says it may consider;
- how a brand-new repository differs from an actively maintained or widely used
  project;
- what would be truthful to state in an application today;
- what evidence might support a future application after genuine adoption.

Do not propose fake users, fabricated metrics, artificial stars, misleading
claims, duplicate accounts, or other attempts to manipulate selection.

## Source requirements

- Browse current sources; do not rely on model memory.
- Prefer specifications, official documentation, canonical repositories,
  issue trackers, release notes, and maintainer discussions.
- For technical claims, cite primary sources.
- Include access or publication dates when recency matters.
- Clearly label inference and unresolved uncertainty.
- Quote sparingly and link every material factual claim near the claim.
- Search for evidence against the proposal as aggressively as evidence for it.

## Required output

Return a decision document with these sections:

1. Executive verdict: GO, PIVOT, or NO-GO.
2. One-sentence problem and one-sentence target user.
3. Evidence that the problem exists.
4. Standards and architecture findings.
5. Competitor/substitute matrix.
6. Differentiation and remaining gap.
7. Threat model and trust boundaries.
8. MVP specification with explicit exclusions.
9. 30/60/90-day adoption and validation plan.
10. Falsification criteria and stop conditions.
11. Program-fit assessment with no promise of approval.
12. Prioritized next actions.
13. Sources.

End with a direct recommendation:

- Build hil-attest as proposed;
- pivot to a narrower integration or upstream contribution; or
- stop and invest in another problem.

If recommending GO, provide a concise repository specification: final name,
tagline, license recommendation, package layout, CLI contract, output example,
test plan, release checklist, and first ten GitHub issues.

---

