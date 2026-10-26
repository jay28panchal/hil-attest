from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from . import __version__
from .attestation import (
    create_statement,
    evaluate_policy,
    read_statement,
    verify_statement,
    write_statement,
)


def _path(value: str) -> Path:
    return Path(value).expanduser()


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="hil-attest",
        description=(
            "Create and verify in-toto test-result statements for embedded "
            "hardware-in-the-loop runs."
        ),
    )
    parser.add_argument("--version", action="version", version=__version__)
    commands = parser.add_subparsers(dest="command", required=True)

    create = commands.add_parser("create", help="create an attestation statement")
    create.add_argument(
        "--artifact",
        action="append",
        required=True,
        type=_path,
        help="tested firmware artifact; repeat for BIN, HEX, ELF, or image files",
    )
    create.add_argument("--junit", required=True, type=_path)
    create.add_argument("--dut", required=True, type=_path)
    create.add_argument("--evidence", action="append", default=[], type=_path)
    create.add_argument("--run-url")
    create.add_argument("--output", required=True, type=_path)
    create.add_argument("--force", action="store_true")
    create.add_argument(
        "--allow-sensitive-dut-metadata",
        action="store_true",
        help="allow raw device identifiers in embedded DUT metadata",
    )

    verify = commands.add_parser("verify", help="validate structure and digests")
    verify.add_argument("attestation", type=_path)
    verify.add_argument(
        "--artifact",
        action="append",
        default=[],
        type=_path,
        help="recompute a subject digest; repeat as needed",
    )
    verify.add_argument("--junit", type=_path)
    verify.add_argument("--dut", type=_path)
    verify.add_argument(
        "--evidence",
        action="append",
        default=[],
        type=_path,
        help="recompute an evidence digest; repeat as needed",
    )
    verify.add_argument(
        "--require-result",
        choices=("PASSED", "WARNED", "FAILED"),
        help="require this overall test result",
    )
    verify.add_argument("--require-board", help="require this embedded DUT board")
    verify.add_argument("--require-target", help="require this embedded DUT target")
    verify.add_argument(
        "--require-passed-test",
        action="append",
        default=[],
        help="require a named test to appear in passedTests; repeat as needed",
    )

    export = commands.add_parser(
        "export-predicate",
        help="export the predicate for a signing or publication tool",
    )
    export.add_argument("attestation", type=_path)
    export.add_argument("--output", required=True, type=_path)
    export.add_argument("--force", action="store_true")

    inspect = commands.add_parser("inspect", help="print a compact summary")
    inspect.add_argument("attestation", type=_path)
    return parser


def _create(args: argparse.Namespace) -> int:
    statement = create_statement(
        artifacts=args.artifact,
        junit=args.junit,
        dut=args.dut,
        evidence=args.evidence,
        run_url=args.run_url,
        allow_sensitive_dut_metadata=args.allow_sensitive_dut_metadata,
    )
    write_statement(args.output, statement, force=args.force)
    print(f"wrote {args.output}")
    print(f"result: {statement['predicate']['result']}")
    return 0


def _verify(args: argparse.Namespace) -> int:
    statement = read_statement(args.attestation)
    issues = verify_statement(
        statement,
        artifacts=args.artifact,
        junit=args.junit,
        dut=args.dut,
        evidence=args.evidence,
    )
    if not issues:
        issues.extend(
            evaluate_policy(
                statement,
                required_result=args.require_result,
                required_board=args.require_board,
                required_target=args.require_target,
                required_passed_tests=args.require_passed_test,
            )
        )
    if issues:
        print("invalid attestation:", file=sys.stderr)
        for issue in issues:
            print(f"- {issue}", file=sys.stderr)
        return 1
    print("valid attestation")
    return 0


def _export_predicate(args: argparse.Namespace) -> int:
    statement = read_statement(args.attestation)
    issues = verify_statement(statement)
    if issues:
        raise ValueError(
            "cannot export predicate from invalid attestation: " + "; ".join(issues)
        )
    predicate = statement["predicate"]
    write_statement(args.output, predicate, force=args.force)
    print(f"wrote {args.output}")
    return 0


def _inspect(args: argparse.Namespace) -> int:
    statement = read_statement(args.attestation)
    predicate = statement.get("predicate", {})
    if not isinstance(predicate, dict):
        predicate = {}
    subjects = statement.get("subject", [])
    if not isinstance(subjects, list):
        subjects = []

    def sha256(subject: dict) -> str | None:
        digest = subject.get("digest")
        return digest.get("sha256") if isinstance(digest, dict) else None

    def count_tests(field: str) -> int:
        value = predicate.get(field, [])
        return len(value) if isinstance(value, list) else 0

    summary = {
        "result": predicate.get("result"),
        "subjects": [
            {
                "name": subject.get("name"),
                "sha256": sha256(subject),
            }
            for subject in subjects
            if isinstance(subject, dict)
        ],
        "passed": count_tests("passedTests"),
        "warned": count_tests("warnedTests"),
        "failed": count_tests("failedTests"),
        "run_url": predicate.get("url"),
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "create":
            return _create(args)
        if args.command == "verify":
            return _verify(args)
        if args.command == "export-predicate":
            return _export_predicate(args)
        if args.command == "inspect":
            return _inspect(args)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.exit(2, f"error: {exc}\n")
    parser.error(f"unknown command: {args.command}")
    return 2

