from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import xml.etree.ElementTree as ET

MAX_JUNIT_BYTES = 10 * 1024 * 1024


@dataclass(frozen=True)
class TestResults:
    passed: tuple[str, ...]
    warned: tuple[str, ...]
    failed: tuple[str, ...]

    @property
    def result(self) -> str:
        if self.failed:
            return "FAILED"
        if self.warned:
            return "WARNED"
        return "PASSED"


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _case_name(case: ET.Element) -> str:
    name = case.attrib.get("name", "").strip() or "unnamed"
    scope = (
        case.attrib.get("classname", "").strip()
        or case.attrib.get("file", "").strip()
    )
    return f"{scope}::{name}" if scope else name


def _deduplicate(name: str, counts: dict[str, int]) -> str:
    count = counts.get(name, 0) + 1
    counts[name] = count
    return name if count == 1 else f"{name} [{count}]"


def parse_junit(path: Path) -> TestResults:
    size = path.stat().st_size
    if size > MAX_JUNIT_BYTES:
        raise ValueError(
            f"JUnit file is {size} bytes; the limit is {MAX_JUNIT_BYTES}"
        )

    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as exc:
        raise ValueError(f"invalid JUnit XML: {exc}") from exc

    passed: list[str] = []
    warned: list[str] = []
    failed: list[str] = []
    counts: dict[str, int] = {}

    for case in root.iter():
        if _local_name(case.tag) != "testcase":
            continue

        name = _deduplicate(_case_name(case), counts)
        outcomes = {_local_name(child.tag) for child in case}
        if "failure" in outcomes or "error" in outcomes:
            failed.append(name)
        elif "skipped" in outcomes:
            warned.append(name)
        else:
            passed.append(name)

    if not passed and not warned and not failed:
        raise ValueError("JUnit XML contains no testcase elements")

    return TestResults(
        passed=tuple(passed),
        warned=tuple(warned),
        failed=tuple(failed),
    )

