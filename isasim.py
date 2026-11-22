#!/usr/bin/env python3
"""
isasim.py - RISC-V RV32I instruction set simulator (02155 final assignment).

Usage:
    python3 isasim.py program.bin              # run, print registers, write program.out.res
    python3 isasim.py program.bin -v           # also print registers after every instruction
    python3 isasim.py program.bin -o out.res   # choose where the binary register dump goes

The binary dump contains x0..x31, 4 bytes each, little-endian (128 bytes),
the same format as the provided .res files.
"""

import argparse
import struct
import sys
from pathlib import Path

from cpu import CPU, opcode, u32
import alu
import control
import memory

# opcode -> handler(cpu, inst) -> next_pc
# Each module exports a HANDLERS dict; together they cover RV32I.
DISPATCH = {}
for module in (alu, control, memory):
    DISPATCH.update(module.HANDLERS)


def load_program(cpu: CPU, path: str) -> None:
    data = Path(path).read_bytes()
    if len(data) > len(cpu.mem):
        sys.exit(f"error: program ({len(data)} bytes) does not fit in memory")
    cpu.mem[0:len(data)] = data
    cpu.program_end = len(data)


def fetch(cpu: CPU) -> int:
    return int.from_bytes(cpu.mem[cpu.pc:cpu.pc + 4], "little")


def step(cpu: CPU) -> None:
    inst = fetch(cpu)
    handler = DISPATCH.get(opcode(inst))
    if handler is None:
        raise RuntimeError(f"unknown instruction 0x{inst:08x} (opcode 0x{opcode(inst):02x}) at pc=0x{cpu.pc:08x}")
    next_pc = handler(cpu, inst)
    cpu.reg[0] = 0                  # x0 is always zero
    cpu.pc = u32(next_pc)


def run(cpu: CPU, verbose: bool = False, max_steps: int = 10_000_000) -> int:
    steps = 0
    while cpu.running and 0 <= cpu.pc < cpu.program_end:
        pc = cpu.pc
        inst = fetch(cpu)
        step(cpu)
        steps += 1
        if verbose:
            print(f"--- step {steps}: pc=0x{pc:08x} inst=0x{inst:08x}")
            print(cpu.dump())
        if steps >= max_steps:
            print(f"warning: stopped after {max_steps} steps (infinite loop?)", file=sys.stderr)
            break
    return steps


def main() -> None:
    ap = argparse.ArgumentParser(description="RISC-V RV32I instruction set simulator")
    ap.add_argument("program", help="binary file with RISC-V instructions")
    ap.add_argument("-o", "--output", help="binary register dump (default: <program>.out.res)")
    ap.add_argument("-v", "--verbose", action="store_true", help="print registers after every instruction")
    ap.add_argument("-q", "--quiet", action="store_true", help="do not print the final registers")
    ap.add_argument("--max-steps", type=int, default=10_000_000)
    ap.add_argument("--venus", action="store_true", help="Venus ecall convention: code in a0, argument in a1")
    args = ap.parse_args()

    cpu = CPU()
    cpu.venus = args.venus
    load_program(cpu, args.program)
    steps = run(cpu, args.verbose, args.max_steps)

    if not args.quiet:
        print(f"=== finished after {steps} instructions, pc=0x{cpu.pc:08x}")
        print(cpu.dump())

    out = args.output or str(Path(args.program).with_suffix(".out.res"))
    Path(out).write_bytes(struct.pack("<32I", *cpu.reg))


if __name__ == "__main__":
    main()
