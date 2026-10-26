from pathlib import Path
import tempfile
import unittest

from hil_attest.junit import parse_junit


class ParseJunitTests(unittest.TestCase):
    def test_parses_nested_suites_and_outcomes(self) -> None:
        xml = """<?xml version="1.0"?>
<testsuites>
  <testsuite name="suite-a">
    <testcase classname="boot" name="starts"/>
    <testcase classname="radio" name="connects"><skipped/></testcase>
  </testsuite>
  <testsuite name="suite-b">
    <testcase classname="uart" name="echo"><failure>bad data</failure></testcase>
  </testsuite>
</testsuites>
"""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "results.xml"
            path.write_text(xml, encoding="utf-8")
            results = parse_junit(path)

        self.assertEqual(results.passed, ("boot::starts",))
        self.assertEqual(results.warned, ("radio::connects",))
        self.assertEqual(results.failed, ("uart::echo",))
        self.assertEqual(results.result, "FAILED")

    def test_rejects_empty_report(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "results.xml"
            path.write_text("<testsuite/>", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "no testcase"):
                parse_junit(path)

    def test_preserves_duplicate_test_names(self) -> None:
        xml = """<testsuite>
  <testcase classname="device" name="boots"/>
  <testcase classname="device" name="boots"/>
</testsuite>"""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "results.xml"
            path.write_text(xml, encoding="utf-8")
            results = parse_junit(path)

        self.assertEqual(results.passed, ("device::boots", "device::boots [2]"))


if __name__ == "__main__":
    unittest.main()

