import base64
import json
from pathlib import Path
import tempfile
import unittest

from hil_attest.attestation import (
    PREDICATE_TYPE,
    STATEMENT_TYPE,
    create_statement,
    evaluate_policy,
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

    def test_accepts_omitted_optional_test_lists(self) -> None:
        statement = self._statement()
        predicate = statement["predicate"]
        predicate["result"] = "FAILED"
        del predicate["passedTests"]
        del predicate["warnedTests"]
        del predicate["failedTests"]

        self.assertEqual(verify_statement(statement), [])

    def test_reports_malformed_digest_objects(self) -> None:
        statement = self._statement()
        statement["subject"][0]["digest"] = None
        statement["subject"].append(
            {"name": "firmware.hex", "digest": {"sha256": "0" * 64}}
        )
        statement["predicate"]["configuration"][0]["digest"] = "invalid"

        issues = verify_statement(statement)

        self.assertIn("subject digest must be an object", issues)
        self.assertIn("duplicate subject name: firmware.hex", issues)
        self.assertIn(
            "configuration digest must be an object for 'dut/dut.json'", issues
        )

    def test_rejects_inconsistent_outcome_lists(self) -> None:
        statement = self._statement()
        statement["predicate"]["result"] = "PASSED"
        statement["predicate"]["failedTests"] = ["boot::crashes"]

        self.assertIn(
            "result must be FAILED when failedTests is non-empty",
            verify_statement(statement),
        )

    def test_policy_accepts_expected_result_dut_and_test(self) -> None:
        self.assertEqual(
            evaluate_policy(
                self._statement(),
                required_result="WARNED",
                required_board="nrf52840dk_nrf52840",
                required_target="nRF52840",
                required_passed_tests=["boot::banner"],
            ),
            [],
        )

    def test_policy_reports_unsatisfied_requirements(self) -> None:
        issues = evaluate_policy(
            self._statement(),
            required_result="PASSED",
            required_board="esp32_devkitc",
            required_target="ESP32",
            required_passed_tests=["wifi::connects"],
        )

        self.assertIn("policy requires result 'PASSED'; found 'WARNED'", issues)
        self.assertIn("policy requires a passing test: wifi::connects", issues)
        self.assertIn(
            "policy requires DUT board 'esp32_devkitc'; "
            "found 'nrf52840dk_nrf52840'",
            issues,
        )
        self.assertIn(
            "policy requires DUT target 'ESP32'; found 'nRF52840'", issues
        )

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

    def test_rejects_camel_case_device_identifier(self) -> None:
        self.dut.write_text(
            json.dumps(
                {
                    "board": "custom",
                    "target": "nRF52840",
                    "serialNumber": "123456789",
                }
            ),
            encoding="utf-8",
        )

        with self.assertRaisesRegex(ValueError, "serialNumber"):
            load_dut_metadata(self.dut)

    def test_requires_board_and_target(self) -> None:
        self.dut.write_text('{"board": "custom"}', encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "target"):
            load_dut_metadata(self.dut)


if __name__ == "__main__":
    unittest.main()

