# hil-attest change log

Updated: 2026-10-26

## Current objective

Validate whether a vendor-neutral hardware-in-the-loop test-attestation tool
solves a real open-source need, while maintaining an executable MVP that can
bind firmware artifacts to JUnit results, privacy-safe DUT metadata, and test
evidence.

The project must earn adoption through genuine usefulness. It is not a
guaranteed or automatic route to any OpenAI program benefit.

## Repository state

- Workspace: /home/jay/jay-work/personal/hil-attest
- Branch: main
- Repository: initialized locally
- Remote: none
- Commit state: initial/root commit authorized on 2026-10-26; use
  git rev-parse HEAD for its exact identifier
- Publication state: not published
- Program application: not submitted

Do not create additional commits, create a remote, push, publish a package, or
submit an application without explicit user instruction.

## 2026-10-26 — Research, project selection, and MVP

The user explicitly authorized the first repository commit. That authorization
covers the initial tested project snapshot only and does not authorize a remote
repository or push.

### Research decision

Research rejected another generic UART/RTT viewer because mature or active
alternatives already cover that space, including SEGGER RTT Viewer, Serial
Studio, LogScope, Cortex-Debug, and newer crash-analysis tools.

The selected experiment is hil-attest: create portable in-toto Test Result
statements that bind exact firmware digests to hardware-test results and
evidence. Existing foundations address adjacent layers:

- GitHub artifact attestations cover build provenance.
- in-toto defines a generic Test Result predicate.
- pytest-embedded, Zephyr, labgrid, and similar systems execute embedded tests.

The hypothesis is that a small interoperability layer connecting those outputs
is useful. This remains a hypothesis until external maintainers and users
validate it.

### Implemented

- Dependency-free Python 3.10+ package and CLI.
- create command supporting multiple firmware artifacts.
- JUnit XML parsing with passed, skipped/warned, and failed test lists.
- Deterministic in-toto Statement v1 / Test Result v0.1 JSON.
- Canonical embedded DUT metadata requiring board and target.
- Default rejection of raw serial numbers, MAC/IP addresses, and similar
  identifiers.
- SHA-256 descriptors for firmware, JUnit XML, and arbitrary evidence files.
- verify command for structure, consistency, embedded metadata, firmware,
  JUnit, DUT, and evidence digests.
- inspect command for a compact human-readable summary.
- Atomic output writing.
- Cross-platform GitHub Actions matrix for Python 3.10 and 3.13 on Ubuntu,
  Windows, and macOS.
- MIT license, security policy, contribution guide, examples, integration
  recipes, and design rationale.
- Repository-local AGENTS.md requiring change-log and AI_UPDATE maintenance
  after completed tasks.
- A project-specific deep-research prompt.
- A separate, general prompt for discovering and evaluating entirely new
  open-source project ideas:
  docs/new-oss-project-discovery-prompt.md.

### Verification

All verification below used fixtures or host-side tests, not physical hardware.

- rtk proxy python3 -m compileall -q src tests
  - Passed.
- rtk proxy env PYTHONPATH=src python3 -m unittest discover -s tests -v
  - Passed: 11 tests.
- Example create command using examples/firmware.bin, results.xml, dut.json,
  and uart.log
  - Passed; generated /tmp/hil-attest-example.json.
- Example verify command recomputing all four input classes
  - Passed: valid attestation.
- rtk proxy python3 -m pip wheel --no-deps --no-build-isolation .
  - Passed after the final verifier extension; built
    hil_attest-0.1.0-py3-none-any.whl.

### Known limitations

- No real nRF, ESP32, STM32, Zephyr, or other physical-board test has run.
- Output is unsigned; it links digests but does not authenticate the producer
  or prove that a physical test occurred.
- Output has not yet been validated against upstream machine-readable in-toto
  schemas.
- No Sigstore/cosign or GitHub attestation publication workflow exists.
- No replay protection or trusted HIL worker identity exists.
- Only JUnit XML is parsed; framework-specific metadata adapters are pending.
- CI is defined but has not run on GitHub because the repository is local.
- No external users, reviews, issues, downloads, releases, or adoption exist.
- The MIT license is a local initial choice and can be reconsidered before the
  first public release.

## Next actions

1. Run the general discovery prompt independently and compare its winner
   against hil-attest; accept a pivot or no-go result.
2. Ask in-toto, pytest-embedded, Zephyr, and labgrid maintainers whether the
   interoperability gap is real and whether upstream contribution is better.
3. Validate generated output against upstream schemas.
4. Add a controlled signing and verification example.
5. Run a clearly documented physical nRF52840 test pilot, then an ESP32 pilot.
6. Add adapters only after real workflows demonstrate what metadata is needed.
7. Rerun the wheel build and all tests again immediately before any commit.
8. Publish only after explicit user authorization; the initial local commit
   does not authorize creating a remote or pushing.

## Handoff

Start here, then read:

- ../AI_UPDATE/hil-attest/INDEX.md
- ../AI_UPDATE/hil-attest/initial_research_mvp_20261026.md
- docs/design.md
- docs/new-oss-project-discovery-prompt.md

The source package is small, but the files above are the authoritative project
state and should be sufficient for normal continuation without reading every
source file.

