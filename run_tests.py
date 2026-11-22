#!/usr/bin/env python3
"""
run_tests.py - run every tests/**/*.bin through the simulator and compare
the register dump with the expected .res file.

Usage:
    python3 run_tests.py              # all tests
    python3 run_tests.py task1        # only tests whose path contains "task1"
    python3 run_tests.py -v           # show register differences for failing tests
"""

import struct
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SIM = ROOT / "isasim.py"
TIMEOUT = 30  # seconds per test


def regs(data: bytes):
    return struct.unpack("<32I", data[:128].ljust(128, b"\0"))


def run_one(binfile: Path, verbose: bool) -> bool:
    expected_file = binfile.with_suffix(".res")
    if not expected_file.exists():
        print(f"  SKIP  {binfile.relative_to(ROOT)} (no .res)")
        return True

    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "out.res"
        try:
            proc = subprocess.run(
                [sys.executable, str(SIM), str(binfile), "-q", "-o", str(out)]
                + (["--venus"] if "extra" in binfile.parts else []),
                capture_output=True, text=True, timeout=TIMEOUT,
            )
        except subprocess.TimeoutExpired:
            print(f"  FAIL  {binfile.relative_to(ROOT)} (timeout)")
            return False

        if proc.returncode != 0 or not out.exists():
            last = (proc.stderr.strip().splitlines() or ["no output"])[-1]
            print(f"  FAIL  {binfile.relative_to(ROOT)} (crash: {last})")
            return False

        got, exp = out.read_bytes(), expected_file.read_bytes()

    if got == exp:
        print(f"  ok    {binfile.relative_to(ROOT)}")
        return True

    print(f"  FAIL  {binfile.relative_to(ROOT)}")
    if verbose:
        for i, (g, e) in enumerate(zip(regs(got), regs(exp))):
            if g != e:
                print(f"          x{i:<2} got 0x{g:08x}  expected 0x{e:08x}")
    return False


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    verbose = "-v" in sys.argv
    tests = sorted((ROOT / "tests").rglob("*.bin"))
    if args:
        tests = [t for t in tests if any(a in str(t) for a in args)]

    passed = sum(run_one(t, verbose) for t in tests)
    print(f"\n{passed}/{len(tests)} passed")
    sys.exit(0 if passed == len(tests) else 1)


if __name__ == "__main__":
    main()
