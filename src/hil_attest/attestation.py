from __future__ import annotations

import base64
import hashlib
import json
import os
from pathlib import Path
import tempfile
from typing import Any, Iterable

from .junit import parse_junit

STATEMENT_TYPE = "https://in-toto.io/Statement/v1"
PREDICATE_TYPE = "https://in-toto.io/attestation/test-result/v0.1"
JSON_MEDIA_TYPE = "application/json"

_SENSITIVE_DUT_KEYS = {
    "address",
    "device_id",
    "email",
    "imei",
    "ip",
    "ip_address",
    "mac",
    "mac_address",
    "serial",
    "serial_number",
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def _descriptor(path: Path, prefix: str) -> dict[str, Any]:
    return {
        "name": f"{prefix}/{path.name}",
        "digest": {"sha256": sha256_path(path)},
    }


def _artifact_descriptor(path: Path) -> dict[str, Any]:
    return {
        "name": path.name,
        "digest": {"sha256": sha256_path(path)},
    }


def _walk_keys(value: Any, parent: str = "") -> Iterable[str]:
    if isinstance(value, dict):
        for key, child in value.items():
            path = f"{parent}.{key}" if parent else str(key)
            yield path
            yield from _walk_keys(child, path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _walk_keys(child, f"{parent}[{index}]")


def load_dut_metadata(path: Path, allow_sensitive: bool = False) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as stream:
        value = json.load(stream)

    if not isinstance(value, dict):
        raise ValueError("DUT metadata must be a JSON object")

    required = {"board", "target"}
    missing = sorted(required - value.keys())
    if missing:
        raise ValueError(f"DUT metadata is missing: {', '.join(missing)}")

    if not allow_sensitive:
        sensitive: list[str] = []
        for key_path in _walk_keys(value):
            leaf = key_path.rsplit(".", 1)[-1].split("[", 1)[0].lower()
            if leaf in _SENSITIVE_DUT_KEYS and not leaf.endswith("_hash"):
                sensitive.append(key_path)
        if sensitive:
            raise ValueError(
                "DUT metadata contains sensitive identifiers: "
                + ", ".join(sorted(sensitive))
                + ". Store a one-way hash instead or pass "
                "--allow-sensitive-dut-metadata."
            )

    return value


def _embedded_dut_descriptor(path: Path, metadata: dict[str, Any]) -> dict[str, Any]:
    content = canonical_json_bytes(metadata)
    return {
        "name": f"dut/{path.name}",
        "digest": {"sha256": sha256_bytes(content)},
        "mediaType": JSON_MEDIA_TYPE,
        "content": base64.b64encode(content).decode("ascii"),
    }


def _reject_duplicate_names(paths: Iterable[Path], label: str) -> None:
    names: set[str] = set()
    duplicates: set[str] = set()
    for path in paths:
        if path.name in names:
            duplicates.add(path.name)
        names.add(path.name)
    if duplicates:
        raise ValueError(
            f"duplicate {label} basenames: {', '.join(sorted(duplicates))}"
        )


def create_statement(
    *,
    artifacts: list[Path],
    junit: Path,
    dut: Path,
    evidence: list[Path] | None = None,
    run_url: str | None = None,
    allow_sensitive_dut_metadata: bool = False,
) -> dict[str, Any]:
    if not artifacts:
        raise ValueError("at least one artifact is required")

    evidence = evidence or []
    _reject_duplicate_names(artifacts, "artifact")
    _reject_duplicate_names(evidence, "evidence")

    for path in [*artifacts, junit, dut, *evidence]:
        if not path.is_file():
            raise ValueError(f"file does not exist: {path}")

    results = parse_junit(junit)
    dut_metadata = load_dut_metadata(
        dut, allow_sensitive=allow_sensitive_dut_metadata
    )

    configuration = [
        _embedded_dut_descriptor(dut, dut_metadata),
        _descriptor(junit, "junit"),
        *[_descriptor(path, "evidence") for path in evidence],
    ]

    predicate: dict[str, Any] = {
        "result": results.result,
        "configuration": configuration,
        "passedTests": list(results.passed),
        "warnedTests": list(results.warned),
        "failedTests": list(results.failed),
    }
    if run_url:
        predicate["url"] = run_url

    return {
        "_type": STATEMENT_TYPE,
        "subject": [_artifact_descriptor(path) for path in artifacts],
        "predicateType": PREDICATE_TYPE,
        "predicate": predicate,
    }


def _valid_sha256(value: Any) -> bool:
    if not isinstance(value, str) or len(value) != 64:
        return False
    return all(character in "0123456789abcdef" for character in value)


def verify_statement(
    statement: dict[str, Any],
    *,
    artifacts: list[Path] | None = None,
    junit: Path | None = None,
    dut: Path | None = None,
    evidence: list[Path] | None = None,
) -> list[str]:
    issues: list[str] = []
    if statement.get("_type") != STATEMENT_TYPE:
        issues.append("unsupported or missing statement _type")
    if statement.get("predicateType") != PREDICATE_TYPE:
        issues.append("unsupported or missing predicateType")

    subjects = statement.get("subject")
    if not isinstance(subjects, list) or not subjects:
        issues.append("subject must be a non-empty list")
        subjects = []

    subject_by_name: dict[str, str] = {}
    for subject in subjects:
        if not isinstance(subject, dict):
            issues.append("subject entries must be objects")
            continue
        name = subject.get("name")
        digest = subject.get("digest", {}).get("sha256")
        if not isinstance(name, str) or not name:
            issues.append("subject name must be a non-empty string")
        elif name in subject_by_name:
            issues.append(f"duplicate subject name: {name}")
        if not _valid_sha256(digest):
            issues.append(f"invalid SHA-256 for subject: {name!r}")
        elif isinstance(name, str):
            subject_by_name[name] = digest

    predicate = statement.get("predicate")
    if not isinstance(predicate, dict):
        issues.append("predicate must be an object")
        predicate = {}

    result_lists: dict[str, list[str]] = {}
    for field in ("passedTests", "warnedTests", "failedTests"):
        value = predicate.get(field)
        if not isinstance(value, list) or not all(
            isinstance(item, str) for item in value
        ):
            issues.append(f"{field} must be a list of strings")
            value = []
        result_lists[field] = value

    expected_result = (
        "FAILED"
        if result_lists["failedTests"]
        else "WARNED"
        if result_lists["warnedTests"]
        else "PASSED"
    )
    if predicate.get("result") != expected_result:
        issues.append(
            f"result is {predicate.get('result')!r}; expected {expected_result!r}"
        )

    configuration = predicate.get("configuration")
    if not isinstance(configuration, list) or not configuration:
        issues.append("configuration must be a non-empty list")
        configuration = []

    configuration_by_name: dict[str, str] = {}
    for descriptor in configuration:
        if not isinstance(descriptor, dict):
            issues.append("configuration entries must be objects")
            continue
        name = descriptor.get("name")
        digest = descriptor.get("digest", {}).get("sha256")
        if not isinstance(name, str) or not name:
            issues.append("configuration name must be a non-empty string")
        elif name in configuration_by_name:
            issues.append(f"duplicate configuration name: {name}")
        if not _valid_sha256(digest):
            issues.append(f"invalid configuration SHA-256 for {name!r}")
        elif isinstance(name, str):
            configuration_by_name[name] = digest
        content = descriptor.get("content")
        if content is not None:
            try:
                decoded = base64.b64decode(content, validate=True)
            except (ValueError, TypeError):
                issues.append(f"invalid base64 content for {name!r}")
            else:
                if sha256_bytes(decoded) != digest:
                    issues.append(f"embedded content digest mismatch for {name!r}")

    for path in artifacts or []:
        expected = subject_by_name.get(path.name)
        if expected is None:
            issues.append(f"artifact is not listed as a subject: {path.name}")
        elif not path.is_file():
            issues.append(f"artifact does not exist: {path}")
        elif sha256_path(path) != expected:
            issues.append(f"artifact digest mismatch: {path}")

    def verify_configuration_file(path: Path, prefix: str) -> None:
        name = f"{prefix}/{path.name}"
        expected = configuration_by_name.get(name)
        if expected is None:
            issues.append(f"configuration file is not listed: {name}")
        elif not path.is_file():
            issues.append(f"configuration file does not exist: {path}")
        elif sha256_path(path) != expected:
            issues.append(f"configuration digest mismatch: {path}")

    if junit is not None:
        verify_configuration_file(junit, "junit")
    for path in evidence or []:
        verify_configuration_file(path, "evidence")
    if dut is not None:
        name = f"dut/{dut.name}"
        expected = configuration_by_name.get(name)
        if expected is None:
            issues.append(f"DUT metadata is not listed: {name}")
        elif not dut.is_file():
            issues.append(f"DUT metadata does not exist: {dut}")
        else:
            try:
                with dut.open("r", encoding="utf-8") as stream:
                    dut_value = json.load(stream)
            except (OSError, json.JSONDecodeError) as exc:
                issues.append(f"cannot read DUT metadata {dut}: {exc}")
            else:
                if not isinstance(dut_value, dict):
                    issues.append(f"DUT metadata must be a JSON object: {dut}")
                elif sha256_bytes(canonical_json_bytes(dut_value)) != expected:
                    issues.append(f"DUT metadata digest mismatch: {dut}")

    return issues


def write_statement(path: Path, statement: dict[str, Any], *, force: bool) -> None:
    if path.exists() and not force:
        raise ValueError(f"output already exists: {path}; pass --force to replace it")
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(statement, indent=2, sort_keys=True) + "\n"
    temporary_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary:
            temporary.write(payload)
            temporary.flush()
            os.fsync(temporary.fileno())
            temporary_name = temporary.name
        os.replace(temporary_name, path)
    finally:
        if temporary_name is not None:
            temporary_path = Path(temporary_name)
            if temporary_path.exists():
                temporary_path.unlink()


def read_statement(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as stream:
        value = json.load(stream)
    if not isinstance(value, dict):
        raise ValueError("attestation must be a JSON object")
    return value

