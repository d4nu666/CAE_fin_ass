# CAE_fin_ass – RISC-V RV32I Instruction Set Simulator

02155 Computer Architecture and Engineering – Final Assignment, Group 22.

A Python simulator for the RISC-V base integer instruction set (RV32I). It loads a
binary program at address 0, executes it, and writes out the registers x0–x31.
Only the Python 3 standard library is used – no packages to install.

## Quick start

```bash
python3 isasim.py tests/task1/addpos.bin        # run a program, print registers
python3 isasim.py tests/task1/addpos.bin -v     # print registers after every instruction
python3 run_tests.py                            # run all tests
python3 run_tests.py task1 -v                   # only task1, show which registers differ
```

`isasim.py` writes a binary dump (`<program>.out.res`, or `-o file`): x0–x31,
4 bytes each, little-endian – the same 128-byte format as the provided `.res` files.

## Project layout

| File | What | Owner |
|---|---|---|
| `cpu.py` | CPU state, field extractors, immediates (`imm_i/s/b/u/j`), `u32`/`s32`/`sext` | shared – **done** |
| `isasim.py` | command line, program loading, fetch/dispatch loop, output | shared – **done** |
| `run_tests.py` | runs every `tests/**/*.bin`, compares with `.res` | shared – **done** |
| `alu.py` | R-type, I-type ALU, `lui`, `auipc` | **Person A** |
| `control.py` | branches, `jal`, `jalr`, `ecall` | **Person B** |
| `memory.py` | `lb lh lw lbu lhu`, `sb sh sw`, memory bounds | **Person C** |
| `tests/` | provided test programs (`.s` source, `.bin` input, `.res` expected) | – |

Every instruction handler has the signature `handler(cpu, inst) -> next_pc`.
Each module exports `HANDLERS = {opcode: handler}` and `isasim.py` merges them.
Unimplemented instructions raise `NotImplementedError`, so a test tells you exactly what is missing.

### Rules everyone follows

- Registers always hold **unsigned 32-bit** values. Write them with `cpu.write_reg(rd, value)`
  (wraps to 32 bits, ignores x0). Python ints never overflow, so this matters.
- Use `s32(x)` when you need the signed value (`slt`, `blt`, `bge`, `sra`, …).
- Immediates from `imm_*()` are already sign-extended Python ints.
- Don't change `cpu.py` / `isasim.py` without telling the group.

## Division of work

| | Person A | Person B | Person C |
|---|---|---|---|
| Code | `alu.py` | `control.py` | `memory.py`, integration |
| Instructions | `add sub sll slt sltu xor srl sra or and`, `addi slti sltiu xori ori andi slli srli srai`, `lui auipc` | `beq bne blt bge bltu bgeu`, `jal jalr`, `ecall` (exit on a7=10, optional Ripes print calls) | `lb lh lw lbu lhu`, `sb sh sw` |
| Tests | `tests/task1` | `tests/task2` | `tests/task3`, `tests/task4`, extra per-instruction tests |
| Report | Introduction, 3.1–3.2, Appendix A | Design, 3.3–3.4 | 3.5, Testing, Discussion |

Suggested order: A first (B's and C's tests need `addi`/`li`/`slli` etc. – `addi` already works),
B and C in parallel, then merge and run everything.

Extra per-instruction tests:
<https://github.com/TheAIBot/RISC-V_Sim/tree/master/RISC-V_Sim/InstructionTests>

## Git workflow

```bash
git checkout -b alu          # or control / memory
# ... work, run python3 run_tests.py ...
git add -A && git commit -m "alu: add R-type instructions"
git push -u origin alu       # open a pull request into main
```

Keep `main` always runnable. Pull `main` into your branch often.

## Hand-in checklist

- [ ] `python3 run_tests.py` → all tests pass on Ubuntu
- [ ] Report (Overleaf) finished, front page from assignment 1
- [ ] Zip of the source code (this repo without `.git`)
- [ ] Demo to the TA – everyone can explain every part
