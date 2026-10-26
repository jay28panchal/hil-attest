# Integration recipes

## pytest and pytest-embedded

Generate JUnit XML with the normal pytest option:

~~~console
pytest --embedded-services serial --port /dev/ttyACM0 \
  --junitxml build/hil-results.xml
hil-attest create \
  --artifact build/firmware.bin \
  --junit build/hil-results.xml \
  --dut ci/dut.json \
  --evidence build/uart.log \
  --output build/hil-attestation.json
~~~

The same pattern applies to ESP-IDF services, JTAG services, emulators, and
multi-DUT tests. The DUT metadata should describe whether the run used physical
hardware or emulation.

## Zephyr

Use the JUnit XML produced by Twister or a pytest-based device test and bind it
to the ELF and flash image:

~~~console
hil-attest create \
  --artifact twister-out/<platform>/zephyr/zephyr.elf \
  --artifact twister-out/<platform>/zephyr/zephyr.hex \
  --junit twister-out/twister.xml \
  --dut ci/zephyr-dut.json \
  --evidence twister-out/device.log \
  --output twister-out/hil-attestation.json
~~~

Replace placeholders with the paths produced by the project. Record the exact
board qualifier and runner in the DUT JSON.

## labgrid

labgrid is normally combined with pytest. Emit JUnit XML from pytest, export
the console log as evidence, and use the environment or target name in
privacy-reviewed DUT metadata.

## Signing

The 0.1 CLI emits an unsigned statement. Sign the completed JSON with a
controlled signing system only after local verification. Verification policy
must check signer identity as well as the firmware digest, DUT configuration,
and required tests.

