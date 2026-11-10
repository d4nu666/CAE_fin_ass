"""
cpu.py - shared CPU state, instruction decoding and 32-bit helpers.

Everyone depends on this file, so change it only after telling the group.

Convention: registers ALWAYS hold unsigned 32-bit values (0 .. 2**32-1).
Python ints have no size limit, so:
    * wrap every result you write to a register with u32()
    * use s32() whenever you need the signed interpretation (slt, blt, sra, ...)
"""

MEM_SIZE = 1 << 20          # 1 MB, as required by the assignment
MASK = 0xFFFFFFFF


# ---------------------------------------------------------------- 32-bit helpers

def u32(x: int) -> int:
    """Wrap any Python int to an unsigned 32-bit value."""
    return x & MASK


def s32(x: int) -> int:
    """Interpret a 32-bit value as signed (two's complement)."""
    x &= MASK
    return x - (1 << 32) if x & 0x80000000 else x


def sext(value: int, bits: int) -> int:
    """Sign-extend a `bits`-wide value to a Python int (may be negative)."""
    value &= (1 << bits) - 1
    return value - (1 << bits) if value & (1 << (bits - 1)) else value


# ---------------------------------------------------------------- field extractors

def opcode(inst: int) -> int: return inst & 0x7F
def rd(inst: int) -> int:     return (inst >> 7) & 0x1F
def funct3(inst: int) -> int: return (inst >> 12) & 0x7
def rs1(inst: int) -> int:    return (inst >> 15) & 0x1F
def rs2(inst: int) -> int:    return (inst >> 20) & 0x1F
def funct7(inst: int) -> int: return (inst >> 25) & 0x7F


# ---------------------------------------------------------------- immediates
# All return a sign-extended Python int (may be negative), except imm_u
# which returns the upper-20-bit value already shifted into place (unsigned).

def imm_i(inst: int) -> int:
    """I-type: inst[31:20]"""
    return sext(inst >> 20, 12)


def imm_s(inst: int) -> int:
    """S-type: inst[31:25] | inst[11:7]"""
    return sext(((inst >> 25) << 5) | ((inst >> 7) & 0x1F), 12)


def imm_b(inst: int) -> int:
    """B-type: inst[31] | inst[7] | inst[30:25] | inst[11:8] | 0"""
    imm = (((inst >> 31) & 0x1) << 12) \
        | (((inst >> 7) & 0x1) << 11) \
        | (((inst >> 25) & 0x3F) << 5) \
        | (((inst >> 8) & 0xF) << 1)
    return sext(imm, 13)


def imm_u(inst: int) -> int:
    """U-type: inst[31:12] << 12"""
    return inst & 0xFFFFF000


def imm_j(inst: int) -> int:
    """J-type: inst[31] | inst[19:12] | inst[20] | inst[30:21] | 0"""
    imm = (((inst >> 31) & 0x1) << 20) \
        | (((inst >> 12) & 0xFF) << 12) \
        | (((inst >> 20) & 0x1) << 11) \
        | (((inst >> 21) & 0x3FF) << 1)
    return sext(imm, 21)


# ---------------------------------------------------------------- CPU state

ABI_NAMES = [
    "zero", "ra", "sp", "gp", "tp", "t0", "t1", "t2",
    "s0", "s1", "a0", "a1", "a2", "a3", "a4", "a5",
    "a6", "a7", "s2", "s3", "s4", "s5", "s6", "s7",
    "s8", "s9", "s10", "s11", "t3", "t4", "t5", "t6",
]


class CPU:
    def __init__(self):
        self.pc = 0
        self.reg = [0] * 32               # unsigned 32-bit values
        self.mem = bytearray(MEM_SIZE)    # byte-addressable, little-endian
        self.program_end = 0              # address just past the last instruction
        self.running = True               # set to False by ecall exit

    def write_reg(self, r: int, value: int) -> None:
        """Write a register; wraps to 32 bits and ignores writes to x0."""
        if r != 0:
            self.reg[r] = u32(value)

    def dump(self) -> str:
        """Human-readable register dump (4 registers per line)."""
        lines = []
        for i in range(0, 32, 4):
            cells = [f"x{j:<2} {ABI_NAMES[j]:>4} = 0x{self.reg[j]:08x} ({s32(self.reg[j]):>11})"
                     for j in range(i, i + 4)]
            lines.append("   ".join(cells))
        return "\n".join(lines)
