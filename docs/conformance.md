# in-toto conformance profile

hil-attest emits a deterministic subset of the upstream
[in-toto Statement v1](https://github.com/in-toto/attestation/blob/main/spec/v1/statement.md)
and
[Test Result v0.1](https://github.com/in-toto/attestation/blob/main/spec/predicates/test-result.md)
specifications.

## Generated statement mapping

| Upstream field | hil-attest behavior |
|---|---|
| `_type` | Always `https://in-toto.io/Statement/v1` |
| `subject` | One descriptor per firmware artifact, with a stable basename and SHA-256 digest |
| `predicateType` | Always `https://in-toto.io/attestation/test-result/v0.1` |
| `predicate.result` | Always `PASSED`, `WARNED`, or `FAILED` |
| `predicate.configuration` | DUT metadata, JUnit input, and optional evidence descriptors |
| `predicate.url` | Included only when supplied by the caller |
| Per-test lists | Emitted as string lists; accepted as optional during verification |

Every generated subject has the digest required by Statement v1. Every
configuration entry has a SHA-256 digest, which is stricter than the general
ResourceDescriptor requirement. Embedded DUT content is base64 encoded and its
digest is calculated over the decoded canonical JSON bytes.

## Validation boundary

The `verify` command validates the hil-attest profile and recomputes supplied
file digests. It is not a general validator for every legal in-toto extension,
digest algorithm, envelope, or predicate type. It accepts omitted optional
Test Result per-test lists and ignores unknown fields as required by in-toto's
forward-compatible parsing model.

The upstream protobuf definitions explicitly leave field validation to users,
and the in-toto project is still discussing JSON Schema support. For that
reason, this project uses focused conformance tests rather than claiming that a
protobuf decode alone proves semantic validity.

## Security boundary

Conformance is not authenticity. A bare JSON statement is unsigned and cannot
prove which runner produced it or that physical hardware was present. Release
policy must separately authenticate a trusted HIL runner and authorize the
expected DUT configuration.
