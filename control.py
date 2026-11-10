"""
control.py - control flow and environment calls.         OWNER: Person B

    0x63  branches : beq bne blt bge bltu bgeu
    0x6F  jal
    0x67  jalr
    0x73  ecall

Every handler has the signature  handler(cpu, inst) -> next_pc

Remember:
    * blt/bge compare s32() values, bltu/bgeu compare the raw (unsigned) values
    * branch target = pc + imm_b(inst); not taken -> pc + 4
    * jal : rd = pc + 4, next pc = pc + imm_j(inst)
    * jalr: compute target = (rs1 + imm_i) & ~1 BEFORE writing rd (rd may equal rs1)
    * ecall: a7 (x17) == 10 -> exit (cpu.running = False)
             optional Ripes calls: 1 print int (a0), 4 print string (a0 = address),
             11 print char (a0), 93 exit
      see https://github.com/mortbopet/Ripes/blob/master/docs/ecalls.md
"""

from cpu import funct3, rd, rs1, rs2, imm_b, imm_i, imm_j, s32, u32

A0, A7 = 10, 17


def exec_branch(cpu, inst):
    a = cpu.reg[rs1(inst)]
    b = cpu.reg[rs2(inst)]
    f3 = funct3(inst)

    # TODO(B): decide `taken` for beq(0) bne(1) blt(4) bge(5) bltu(6) bgeu(7)
    raise NotImplementedError(f"branch funct3={f3}")

    return cpu.pc + imm_b(inst) if taken else cpu.pc + 4


def exec_jal(cpu, inst):
    # TODO(B)
    raise NotImplementedError("jal")


def exec_jalr(cpu, inst):
    # TODO(B)
    raise NotImplementedError("jalr")


def exec_ecall(cpu, inst):
    # TODO(B): at least a7 == 10 -> cpu.running = False
    raise NotImplementedError(f"ecall a7={cpu.reg[A7]}")


HANDLERS = {
    0x63: exec_branch,
    0x6F: exec_jal,
    0x67: exec_jalr,
    0x73: exec_ecall,
}
