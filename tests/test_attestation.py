import base64
import json
from pathlib import Path
import tempfile
import unittest

from hil_attest.attestation import (
    PREDICATE_TYPE,
    STATEMENT_TYPE,
    create_statement,
    load_dut_metadata,
    verify_statement,
)


class AttestationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.artifact = self.root / "firmware.hex"
        self.junit = self.root / "results.xml"
        self.dut = self.root / "dut.json"
        self.log = self.root / "uart.log"

        self.artifact.write_bytes(b":020000040000FA\n")
        self.junit.write_text(
            """<testsuite name="hil">
  <testcase classname="boot" name="banner"/>
  <testcase classname="ble" name="advertises"><skipped/></testcase>
</testsuite>""",
            encoding="utf-8",
        )
        self.dut.write_text(
            json.dumps(
                {
                    "board": "nrf52840dk_nrf52840",
                    "target": "nRF52840",
                    "transport": "J-Link RTT",
                    "device_id_hash": "sha256:test-value",
                }
            ),
            encoding="utf-8",
        )
        self.log.write_text("READY\n", encoding="utf-8")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _statement(self) -> dict:
        return create_statement(
            artifacts=[self.artifact],
            junit=self.junit,
            dut=self.dut,
            evidence=[self.log],
            run_url="https://ci.example/runs/42",
        )

    def test_creates_standard_statement(self) -> None:
        statement = self._statement()

        self.assertEqual(statement["_type"], STATEMENT_TYPE)
        self.assertEqual(statement["predicateType"], PREDICATE_TYPE)
        self.assertEqual(statement["predicate"]["result"], "WARNED")
        self.assertEqual(statement["predicate"]["passedTests"], ["boot::banner"])
        self.assertEqual(
            statement["predicate"]["warnedTests"], ["ble::advertises"]
        )
        self.assertEqual(statement["predicate"]["failedTests"], [])
        self.assertEqual(verify_statement(statement), [])

    def test_embeds_canonical_dut_metadata(self) -> None:
        statement = self._statement()
        descriptor = statement["predicate"]["configuration"][0]
        decoded = base64.b64decode(descriptor["content"])
        metadata = json.loads(decoded)

        self.assertEqual(metadata["board"], "nrf52840dk_nrf52840")
        self.assertNotIn(str(self.root), decoded.decode("utf-8"))

    def test_detects_changed_artifact(self) -> None:
        statement = self._statement()
        self.artifact.write_bytes(b"tampered")

        issues = verify_statement(statement, artifacts=[self.artifact])

        self.assertIn(f"artifact digest mismatch: {self.artifact}", issues)

    def test_verifies_all_supplied_inputs(self) -> None:
        statement = self._statement()
        issues = verify_statement(
            statement,
            artifacts=[self.artifact],
            junit=self.junit,
            dut=self.dut,
            evidence=[self.log],
        )
        self.assertEqual(issues, [])

        self.log.write_text("modified\n", encoding="utf-8")
        issues = verify_statement(statement, evidence=[self.log])
        self.assertIn(f"configuration digest mismatch: {self.log}", issues)

    def test_output_is_deterministic(self) -> None:
        first = self._statement()
        second = self._statement()
        first_json = json.dumps(first, sort_keys=True, separators=(",", ":"))
        second_json = json.dumps(second, sort_keys=True, separators=(",", ":"))
        self.assertEqual(first_json, second_json)

    def test_rejects_raw_device_identifier(self) -> None:
        self.dut.write_text(
            json.dumps(
                {
                    "board": "custom",
                    "target": "nRF52840",
                    "serial_number": "123456789",
                }
            ),
            encoding="utf-8",
        )

        with self.assertRaisesRegex(ValueError, "sensitive identifiers"):
            load_dut_metadata(self.dut)

    def test_requires_board_and_target(self) -> None:
        self.dut.write_text('{"board": "custom"}', encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "target"):
            load_dut_metadata(self.dut)


if __name__ == "__main__":
    unittest.main()

