# hil-attest

Create reproducible, vendor-neutral evidence that a specific firmware artifact
was exercised by a specific hardware-in-the-loop test run.

hil-attest converts JUnit XML, privacy-safe device-under-test metadata, firmware
artifacts, and optional UART/RTT logs into an
[in-toto Test Result](https://github.com/in-toto/attestation/blob/main/spec/predicates/test-result.md)
statement. It also validates the statement and recomputes firmware digests
offline.

## Why this exists

Build provenance answers “where did this binary come from?” Hardware test
frameworks answer “did this test pass?” Embedded release workflows also need a
portable answer to “was this exact binary tested on the intended physical
target, and which evidence belongs to that run?”

hil-attest is the bridge. It does not replace pytest-embedded, Zephyr Twister,
labgrid, or GitHub artifact attestations.

## Status

Version 0.1 is an alpha-quality deterministic statement generator and verifier.
It does not prove the identity of the machine or operator until its output is
signed by a trusted system. Signing and CI publication are roadmap items.

## Requirements

- Python 3.10 or newer
- Windows 10+, macOS 12+, or a current Linux distribution
- JUnit XML from any test harness

The core has no runtime dependencies.

## Install for development

~~~console
python -m venv .venv
.venv/bin/python -m pip install -e .
~~~

On Windows, use .venv\Scripts\python.exe.

## Create an attestation

Prepare a small DUT metadata file:

~~~json
{
  "board": "nrf52840dk_nrf52840",
  "target": "nRF52840",
  "transport": "J-Link RTT",
  "runner": "pytest-embedded",
  "device_id_hash": "sha256:replace-with-a-one-way-hash"
}
~~~

Then bind the test evidence to the firmware:

~~~console
hil-attest create \
  --artifact build/zephyr/zephyr.hex \
  --artifact build/zephyr/zephyr.elf \
  --junit build/test-results.xml \
  --dut dut.json \
  --evidence build/uart.log \
  --output build/hil-attestation.json
~~~

Raw serial numbers, MAC addresses, IP addresses, and similar identifiers are
rejected by default. Store one-way hashes when correlation is necessary.

## Verify

~~~console
hil-attest verify build/hil-attestation.json \
  --artifact build/zephyr/zephyr.hex \
  --artifact build/zephyr/zephyr.elf \
  --junit build/test-results.xml \
  --dut dut.json \
  --evidence build/uart.log
hil-attest inspect build/hil-attestation.json
~~~

Verification checks structure, result consistency, embedded metadata integrity,
and supplied firmware, JUnit, DUT, and evidence files. An unsigned statement
provides integrity linkage, not signer identity.

## Output model

- Subject: each tested firmware image or ELF, identified by SHA-256.
- Configuration: canonical DUT metadata, JUnit XML digest, and evidence digests.
- Result: PASSED, WARNED, or FAILED.
- Tests: stable lists of passed, skipped/warned, and failed test names.
- URL: optional CI or lab-run link.

Absolute local paths and timestamps are intentionally omitted so identical
inputs produce identical output.

## Supported test ecosystems

Any harness that emits JUnit XML works. Initial integration documentation
covers pytest-embedded, Zephyr/Twister, and labgrid-style pytest runs. See
[docs/integrations.md](docs/integrations.md).

## Security and trust

Read [SECURITY.md](SECURITY.md) before using statements as release gates.
hil-attest does not claim a physical test occurred merely because a file says
so. A production policy should require a signature from a controlled HIL runner
and verify the expected board configuration.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). The design and research rationale are
documented in [docs/design.md](docs/design.md).

