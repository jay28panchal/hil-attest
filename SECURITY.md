# Security policy

Please report vulnerabilities privately to the repository owner before opening
a public issue.

## Trust boundary

hil-attest 0.1 creates and validates unsigned in-toto statements. It verifies
hash linkage and internal consistency; it does not authenticate who ran a test
or whether metadata truthfully describes the connected hardware.

Do not use an unsigned statement as the sole release authorization. A secure
deployment should:

1. Run on a controlled HIL worker.
2. Protect the signing identity outside the repository.
3. Sign the completed statement.
4. Verify the signer, firmware digest, expected DUT configuration, and required
   test names in release policy.
5. Retain original test logs according to the project retention policy.

Raw device serial numbers, network addresses, and personal identifiers are
rejected from DUT metadata by default. This is a guardrail, not a complete
data-loss-prevention system.

