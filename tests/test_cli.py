import json
from pathlib import Path
import tempfile
import unittest

from hil_attest.cli import main


class CliTests(unittest.TestCase):
    def test_create_verify_and_inspect(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            artifact = root / "firmware.bin"
            junit = root / "results.xml"
            dut = root / "dut.json"
            output = root / "attestation.json"

            artifact.write_bytes(b"firmware")
            junit.write_text(
                '<testsuite><testcase name="boots"/></testsuite>',
                encoding="utf-8",
            )
            dut.write_text(
                json.dumps({"board": "qemu-test", "target": "cortex-m"}),
                encoding="utf-8",
            )

            self.assertEqual(
                main(
                    [
                        "create",
                        "--artifact",
                        str(artifact),
                        "--junit",
                        str(junit),
                        "--dut",
                        str(dut),
                        "--output",
                        str(output),
                    ]
                ),
                0,
            )
            self.assertTrue(output.is_file())
            self.assertEqual(
                main(
                    [
                        "verify",
                        str(output),
                        "--artifact",
                        str(artifact),
                        "--junit",
                        str(junit),
                        "--dut",
                        str(dut),
                        "--require-result",
                        "PASSED",
                        "--require-board",
                        "qemu-test",
                        "--require-target",
                        "cortex-m",
                        "--require-passed-test",
                        "boots",
                    ]
                ),
                0,
            )
            predicate_output = root / "predicate.json"
            self.assertEqual(
                main(
                    [
                        "export-predicate",
                        str(output),
                        "--output",
                        str(predicate_output),
                    ]
                ),
                0,
            )
            statement = json.loads(output.read_text(encoding="utf-8"))
            predicate = json.loads(predicate_output.read_text(encoding="utf-8"))
            self.assertEqual(predicate, statement["predicate"])
            self.assertNotIn("_type", predicate)
            self.assertEqual(main(["inspect", str(output)]), 0)

    def test_inspect_handles_malformed_untrusted_fields(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            attestation = Path(directory) / "malformed.json"
            attestation.write_text(
                json.dumps(
                    {
                        "subject": [{"name": "firmware.bin", "digest": None}],
                        "predicate": {"passedTests": "not-a-list"},
                    }
                ),
                encoding="utf-8",
            )

            self.assertEqual(main(["inspect", str(attestation)]), 0)


if __name__ == "__main__":
    unittest.main()

