# Design and research rationale

## Problem

Embedded projects commonly have three separate records:

1. build provenance for the firmware artifact;
2. a hardware test report from pytest, Twister, or a lab system;
3. UART, RTT, debugger, or power-measurement logs.

Those records are rarely bound together in one portable statement. A renamed
binary or detached log can therefore be mistaken for evidence about a different
firmware build.

## Existing foundations

- GitHub artifact attestations establish build provenance and can be verified
  offline:
  https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations
- The in-toto Test Result predicate defines a standard representation for test
  configuration and passed, warned, and failed tests:
  https://github.com/in-toto/attestation/blob/main/spec/predicates/test-result.md
- pytest-embedded provides UART, ESP-IDF, JTAG, emulator, and multi-DUT
  services:
  https://docs.espressif.com/projects/pytest-embedded/en/latest/concepts/services.html
- Zephyr provides coredump and serial-log workflows:
  https://docs.zephyrproject.org/latest/services/debugging/coredump.html
- labgrid abstracts hardware control for pytest-based embedded automation:
  https://labgrid.readthedocs.io/

hil-attest composes these foundations instead of inventing a test framework or
attestation schema.

## Design decisions

### Deterministic output

Generated JSON excludes timestamps and absolute paths. The same inputs produce
the same bytes, which simplifies review, caching, signing, and reproduction.

### Standard predicate

The output uses in-toto Statement v1 and Test Result v0.1. Firmware artifacts
are subjects. DUT metadata, JUnit input, and logs are configuration resource
descriptors.

### Privacy-safe device identity

Board family and target are required. Raw serial numbers and network identifiers
are rejected by default. Teams that need per-device correlation should add a
salted or otherwise privacy-reviewed one-way hash.

### Honest trust claims

Version 0.1 does not sign statements. It proves digest relationships, not the
identity or honesty of the producer. Signing and release-policy examples will
be added without weakening that distinction.

## Near-term roadmap

1. Add optional interoperability checks against upstream language bindings as
   they stabilize; the current conformance mapping is documented and tested.
2. Add Sigstore/cosign and GitHub Actions examples.
3. Add adapters for Zephyr Twister and pytest-embedded metadata.
4. Run and document physical-board pilots for nRF52 and ESP32.
5. Propose improvements upstream when hardware-specific configuration needs are
   demonstrated by real integrations.

