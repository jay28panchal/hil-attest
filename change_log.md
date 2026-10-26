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
- Remote: origin at https://github.com/jay28panchal/hil-attest.git
- Commit state: commits e3f599f and 48dead8 are pushed; the conformance,
  signing-integration, platform-support, and policy-gate batch below is
  authorized for commit and push
- Publication state: public at https://github.com/jay28panchal/hil-attest
- Program application: not submitted

Do not create additional commits or pushes, publish a package, or submit an
application without explicit user instruction.

## 2026-10-26 — Conformance, signed-publication path, and support baselines

The user asked work to continue and subsequently authorized committing and
pushing this tested batch. Package publication, program application, and
maintainer contact remain unauthorized and were not performed.

### Research findings

- The official in-toto Test Result v0.1 specification makes `passedTests`,
  `warnedTests`, and `failedTests` optional. The old verifier incorrectly
  required all three and inferred `PASSED` when they were absent.
- The upstream protobuf definitions explicitly leave field validation to
  consumers. There is no stable upstream JSON Schema to vendor as a complete
  semantic validator, so conformance is documented as a tested subset.
- GitHub's official `actions/attest@v4` custom mode accepts a predicate object,
  predicate type, and subject path. It creates and signs the surrounding
  in-toto statement; passing hil-attest's complete statement would duplicate
  that wrapper.
- Official 2026 lifecycle information supports Ubuntu 24.04 LTS, Windows 11
  25H2, and macOS 15 as defensible maintained minimums. GitHub provides pinned
  runner labels for Ubuntu 24.04, Windows Server 2025, and macOS 15.
- Current official GitHub Action documentation uses `actions/checkout@v7` and
  `actions/setup-python@v7`, which run on Node.js 24 and remove the prior CI
  deprecation warnings.

### Implemented

- Accept omitted optional Test Result per-test lists.
- Validate the result enum and reject only contradictions established by
  non-empty failure or warning lists.
- Convert malformed subject/configuration digest objects into validation
  issues instead of uncaught exceptions.
- Detect duplicate descriptor names independently of digest validity and
  normalize snake_case, kebab-case, and camelCase privacy-sensitive DUT keys.
- Make `inspect` safe for malformed predicate, subject, digest, and test-list
  shapes.
- Add `export-predicate` for GitHub/Sigstore publication tools; it validates the
  statement before writing the predicate atomically.
- Add release-policy checks for required overall result, DUT board, DUT target,
  and named passing tests through `verify` CLI flags.
- Add conformance mapping and signed GitHub artifact-attestation guidance,
  including least-privilege permissions, pinned tool checkout, consumer
  verification, and self-hosted HIL runner warnings.
- Replace ambiguous Windows 10/macOS 12/current-Linux claims with documented
  Ubuntu 24.04 LTS, Windows 11 25H2, and macOS 15 support baselines.
- Pin CI OS images and upgrade checkout/setup-python to v7.
- Expand the suite from 11 to 18 tests.

### Verification

All checks remain host-side or fixture-based; no physical hardware was used.

- `python3 -m compileall -q src tests`: passed.
- `PYTHONPATH=src python3 -m unittest discover -s tests -v`: 18 tests passed.
- Wheel build without dependency downloads: passed; generated
  `hil_attest-0.1.0-py3-none-any.whl`. Wheel archives include build metadata,
  so no reproducible-wheel digest is claimed.
- Example create and full file-digest verification: passed.
- Example predicate export: passed.
- Updated GitHub Actions workflow parsed successfully as YAML.
- `git diff --check`: passed.

### Current limitations

- The new pinned CI matrix has not run on GitHub because these changes are not
  committed or pushed.
- Generated statement JSON is deterministic, but reproducible wheel archives
  are not yet part of the project guarantee.
- The signed GitHub attestation workflow is documented but has not executed on
  a controlled HIL runner, and no signed Test Result has been published.
- There is still no physical nRF52, ESP32, STM32, or other board result.
- `verify` validates the hil-attest SHA-256 profile, not every legal in-toto
  digest algorithm, envelope, predicate type, or extension.
- There is no external adoption, maintainer review, release, or program
  acceptance evidence.

## 2026-10-26 — Public repository and first CI run

The user authorized proceeding after the initial commit. Created the public
GitHub repository, configured origin, and pushed main at e3f599f.
The user subsequently authorized committing and pushing this publication and
CI handoff record.

Repository metadata:

- Description: Vendor-neutral in-toto attestations for embedded
  hardware-in-the-loop test evidence
- License detected by GitHub: MIT
- Topics: attestation, embedded, firmware, hardware-in-the-loop, in-toto,
  pytest, supply-chain-security, zephyr
- Issues: enabled

GitHub Actions run 40294115019 passed all six jobs:

- Ubuntu latest: Python 3.10 and 3.13
- macOS latest: Python 3.10 and 3.13
- Windows latest: Python 3.10 and 3.13

Every job passed installation, the 11-test suite, and the example create/verify
round trip. GitHub emitted non-failing warnings that actions/checkout@v4 and
actions/setup-python@v5 target deprecated Node.js 20 and are being forced onto
Node.js 24. Upgrade those actions when stable successor releases are selected.

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

### Limitations at the initial MVP snapshot

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

1. Confirm the six-job pinned OS matrix passes on GitHub after the authorized
   push.
2. Execute the signed custom-attestation example on a controlled HIL runner;
   do not substitute fixture results for a physical-board claim.
3. Run a documented physical nRF52840 pilot, then an ESP32 pilot.
4. Ask in-toto, pytest-embedded, Zephyr, and labgrid maintainers whether the
   interoperability gap is real, but only after authorization to contact them.
5. Run the general discovery prompt independently and compare its winner
   against hil-attest; accept a pivot or no-go result.
6. Add adapters only after real workflows demonstrate required metadata.

## Handoff

Start here, then read:

- ../AI_UPDATE/hil-attest/INDEX.md
- ../AI_UPDATE/hil-attest/initial_research_mvp_20261026.md
- docs/design.md
- docs/conformance.md
- docs/github-attestations.md
- docs/platform-support.md
- docs/new-oss-project-discovery-prompt.md

The source package is small, but the files above are the authoritative project
state and should be sufficient for normal continuation without reading every
source file.

