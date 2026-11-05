#!/usr/bin/env python3
"""Emit finite, time-ordered JSONL records to stdout; no network or dashboard."""

import argparse
import json
import math
import sys
import time
from pathlib import Path


def finite_number(value):
    return type(value) in (int, float) and math.isfinite(value)


def check_numbers(value):
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("non-finite number")
    if isinstance(value, dict):
        for child in value.values():
            check_numbers(child)
    elif isinstance(value, list):
        for child in value:
            check_numbers(child)


def load_records(path):
    records = []
    previous = -1.0
    with path.open(encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, 1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
                if not isinstance(record, dict):
                    raise ValueError("record must be a JSON object")
                check_numbers(record)
                timestamp = record.get("t_ms", record.get("source_t_ms"))
                if not finite_number(timestamp) or timestamp < 0:
                    raise ValueError("requires finite nonnegative t_ms or source_t_ms")
                if timestamp < previous:
                    raise ValueError("source time must not decrease")
                previous = timestamp
                records.append((timestamp, record))
            except (ValueError, OverflowError) as exc:
                raise ValueError(f"{path}:{line_number}: {exc}") from exc
    if not records:
        raise ValueError(f"{path}: no records")
    return records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    parser.add_argument("--speed", type=float, default=1.0, help="positive playback multiplier")
    parser.add_argument("--no-wait", action="store_true", help="emit without pacing")
    args = parser.parse_args()
    if not math.isfinite(args.speed) or args.speed <= 0:
        parser.error("--speed must be positive and finite")
    try:
        records = load_records(args.path)
        origin_ms = records[0][0]
        started = time.monotonic()
        for timestamp, record in records:
            if not args.no_wait:
                due = (timestamp - origin_ms) / (1000 * args.speed)
                time.sleep(max(0, due - (time.monotonic() - started)))
            print(json.dumps(record, ensure_ascii=False, allow_nan=False), flush=True)
    except (OSError, ValueError, OverflowError) as exc:
        print(f"replay: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        return 130
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
