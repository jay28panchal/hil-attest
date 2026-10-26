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
                    ]
                ),
                0,
            )
            self.assertEqual(main(["inspect", str(output)]), 0)


if __name__ == "__main__":
    unittest.main()

