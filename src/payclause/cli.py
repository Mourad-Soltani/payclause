"""Command line for PayClause.

Signature: Mourad.Soltani
"""

from __future__ import annotations

import argparse
import json
import sys

from payclause import __version__
from payclause.engine import ClauseError, build_schedule, health


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="payclause", description="Turn a payment clause into a chase calendar.")
    parser.add_argument("command", choices=("health", "schedule", "version"))
    parser.add_argument("--input", help="Path to a clause JSON file")
    args = parser.parse_args(argv)

    if args.command == "version":
        print(__version__)
        return 0
    if args.command == "health":
        print(json.dumps(health()))
        return 0
    if not args.input:
        print("schedule requires --input", file=sys.stderr)
        return 2
    try:
        with open(args.input, encoding="utf-8") as handle:
            document = json.load(handle)
        print(json.dumps(build_schedule(document), indent=2))
        return 0
    except (OSError, json.JSONDecodeError, ClauseError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
