from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from . import __version__
from .attestation import (
    create_statement,
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
    if issues:
        print("invalid attestation:", file=sys.stderr)
        for issue in issues:
            print(f"- {issue}", file=sys.stderr)
        return 1
    print("valid attestation")
    return 0


def _inspect(args: argparse.Namespace) -> int:
    statement = read_statement(args.attestation)
    predicate = statement.get("predicate", {})
    summary = {
        "result": predicate.get("result"),
        "subjects": [
            {
                "name": subject.get("name"),
                "sha256": subject.get("digest", {}).get("sha256"),
            }
            for subject in statement.get("subject", [])
            if isinstance(subject, dict)
        ],
        "passed": len(predicate.get("passedTests", [])),
        "warned": len(predicate.get("warnedTests", [])),
        "failed": len(predicate.get("failedTests", [])),
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
        if args.command == "inspect":
            return _inspect(args)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.exit(2, f"error: {exc}\n")
    parser.error(f"unknown command: {args.command}")
    return 2

