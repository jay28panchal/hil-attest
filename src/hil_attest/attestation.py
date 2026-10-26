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
    "deviceid",
    "email",
    "imei",
    "ip",
    "ipaddress",
    "mac",
    "macaddress",
    "serial",
    "serialnumber",
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
            normalized = "".join(
                character for character in leaf if character.isalnum()
            )
            if normalized in _SENSITIVE_DUT_KEYS and not normalized.endswith("hash"):
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
    subject_names: set[str] = set()
    for subject in subjects:
        if not isinstance(subject, dict):
            issues.append("subject entries must be objects")
            continue
        name = subject.get("name")
        digest_set = subject.get("digest")
        if not isinstance(digest_set, dict):
            issues.append("subject digest must be an object")
            digest = None
        else:
            digest = digest_set.get("sha256")
        if not isinstance(name, str) or not name:
            issues.append("subject name must be a non-empty string")
        else:
            if name in subject_names:
                issues.append(f"duplicate subject name: {name}")
            subject_names.add(name)
        if not _valid_sha256(digest):
            issues.append(f"invalid SHA-256 for subject: {name!r}")
        elif isinstance(name, str) and name not in subject_by_name:
            subject_by_name[name] = digest

    predicate = statement.get("predicate")
    if not isinstance(predicate, dict):
        issues.append("predicate must be an object")
        predicate = {}

    result_lists: dict[str, list[str]] = {}
    for field in ("passedTests", "warnedTests", "failedTests"):
        value = predicate.get(field, [])
        if field in predicate and (
            not isinstance(value, list)
            or not all(isinstance(item, str) for item in value)
        ):
            issues.append(f"{field} must be a list of strings")
            value = []
        result_lists[field] = value

    result = predicate.get("result")
    if result not in {"PASSED", "WARNED", "FAILED"}:
        issues.append("result must be PASSED, WARNED, or FAILED")
    elif result_lists["failedTests"] and result != "FAILED":
        issues.append("result must be FAILED when failedTests is non-empty")
    elif result_lists["warnedTests"] and result == "PASSED":
        issues.append("result cannot be PASSED when warnedTests is non-empty")

    configuration = predicate.get("configuration")
    if not isinstance(configuration, list):
        issues.append("configuration must be a list")
        configuration = []

    configuration_by_name: dict[str, str] = {}
    configuration_names: set[str] = set()
    for descriptor in configuration:
        if not isinstance(descriptor, dict):
            issues.append("configuration entries must be objects")
            continue
        name = descriptor.get("name")
        digest_set = descriptor.get("digest")
        if not isinstance(digest_set, dict):
            issues.append(f"configuration digest must be an object for {name!r}")
            digest = None
        else:
            digest = digest_set.get("sha256")
        if not isinstance(name, str) or not name:
            issues.append("configuration name must be a non-empty string")
        else:
            if name in configuration_names:
                issues.append(f"duplicate configuration name: {name}")
            configuration_names.add(name)
        if not _valid_sha256(digest):
            issues.append(f"invalid configuration SHA-256 for {name!r}")
        elif isinstance(name, str) and name not in configuration_by_name:
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


def evaluate_policy(
    statement: dict[str, Any],
    *,
    required_result: str | None = None,
    required_board: str | None = None,
    required_target: str | None = None,
    required_passed_tests: list[str] | None = None,
) -> list[str]:
    issues: list[str] = []
    predicate = statement.get("predicate")
    if not isinstance(predicate, dict):
        return ["cannot evaluate policy without a predicate object"]

    if required_result is not None and predicate.get("result") != required_result:
        issues.append(
            f"policy requires result {required_result!r}; "
            f"found {predicate.get('result')!r}"
        )

    passed_tests = predicate.get("passedTests", [])
    passed_names = (
        set(passed_tests)
        if isinstance(passed_tests, list)
        and all(isinstance(item, str) for item in passed_tests)
        else set()
    )
    for test_name in required_passed_tests or []:
        if test_name not in passed_names:
            issues.append(f"policy requires a passing test: {test_name}")

    if required_board is None and required_target is None:
        return issues

    configuration = predicate.get("configuration")
    descriptors = configuration if isinstance(configuration, list) else []
    dut_descriptors = [
        descriptor
        for descriptor in descriptors
        if isinstance(descriptor, dict)
        and isinstance(descriptor.get("name"), str)
        and descriptor["name"].startswith("dut/")
    ]
    if len(dut_descriptors) != 1:
        issues.append("policy requires exactly one embedded DUT descriptor")
        return issues

    content = dut_descriptors[0].get("content")
    try:
        decoded = base64.b64decode(content, validate=True)
        metadata = json.loads(decoded)
    except (ValueError, TypeError, json.JSONDecodeError):
        issues.append("policy cannot decode embedded DUT metadata")
        return issues
    if not isinstance(metadata, dict):
        issues.append("policy requires DUT metadata to be an object")
        return issues

    for field, required in (
        ("board", required_board),
        ("target", required_target),
    ):
        if required is not None and metadata.get(field) != required:
            issues.append(
                f"policy requires DUT {field} {required!r}; "
                f"found {metadata.get(field)!r}"
            )
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

