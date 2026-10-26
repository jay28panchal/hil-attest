# Signed GitHub artifact attestations

GitHub's official `actions/attest` action accepts a custom predicate and
creates the in-toto statement, Sigstore signature, and GitHub attestation
record. It must receive only the Test Result predicate, not the complete
statement emitted by `hil-attest create`.

## Workflow fragment

Run this after the firmware and real hardware test evidence exist. Adapt paths
to the build and HIL environment.

~~~yaml
permissions:
  contents: read
  id-token: write
  attestations: write

steps:
  - uses: actions/checkout@v7
  - name: Check out a pinned hil-attest revision
    uses: actions/checkout@v7
    with:
      repository: jay28panchal/hil-attest
      ref: PINNED_RELEASE_OR_COMMIT
      path: .hil-attest
  - uses: actions/setup-python@v7
    with:
      python-version: "3.13"
  - name: Install hil-attest
    run: python -m pip install ./.hil-attest
  - name: Create HIL Test Result
    shell: bash
    run: |
      hil-attest create \
        --artifact build/firmware.bin \
        --junit build/hil-results.xml \
        --dut build/dut.json \
        --evidence build/uart.log \
        --run-url "$GITHUB_SERVER_URL/$GITHUB_REPOSITORY/actions/runs/$GITHUB_RUN_ID" \
        --output build/hil-statement.json
      hil-attest export-predicate build/hil-statement.json \
        --output build/hil-predicate.json
  - name: Sign and publish Test Result
    uses: actions/attest@v4
    with:
      subject-path: build/firmware.bin
      predicate-type: https://in-toto.io/attestation/test-result/v0.1
      predicate-path: build/hil-predicate.json
~~~

Replace `PINNED_RELEASE_OR_COMMIT` with a reviewed release tag or full commit
SHA. Do not execute an unpinned moving branch in a release workflow.

Artifact attestations are available for public repositories on current GitHub
plans. Private repositories have additional plan requirements. Keep the
permission block narrow: signing needs `id-token: write` and publication needs
`attestations: write`.

## Consumer verification

Verify the artifact identity, workflow signer, and predicate type with the
GitHub CLI:

~~~console
gh attestation verify build/firmware.bin \
  --repo OWNER/REPOSITORY \
  --predicate-type https://in-toto.io/attestation/test-result/v0.1
~~~

To inspect the verified predicate:

~~~console
gh attestation verify build/firmware.bin \
  --repo OWNER/REPOSITORY \
  --predicate-type https://in-toto.io/attestation/test-result/v0.1 \
  --format json \
  --jq '.[].verificationResult.statement.predicate'
~~~

Then enforce project policy on `result`, DUT configuration, and expected test
names. Signature verification alone does not decide whether the test evidence
is sufficient for release.

## Trust boundary

The workflow identity is meaningful only when the job executes on a controlled
runner connected to the intended hardware. Do not label fixture, emulator, or
host-only results as physical HIL evidence. Protect self-hosted runners and
avoid running untrusted pull-request code on hardware-connected runners with
write-capable tokens.

Official references:

- https://github.com/actions/attest
- https://docs.github.com/actions/how-tos/secure-your-work/use-artifact-attestations
