"""
memory.py - loads and stores.                            OWNER: Person C

    0x03  loads  : lb lh lw lbu lhu      (address = rs1 + imm_i)
    0x23  stores : sb sh sw              (address = rs1 + imm_s)

Every handler has the signature  handler(cpu, inst) -> next_pc

Remember:
    * memory is little-endian: use int.from_bytes(..., "little") / value.to_bytes(n, "little")
    * lb/lh sign-extend (sext(value, 8/16)), lbu/lhu zero-extend
    * stores write only the low 1/2/4 bytes of rs2
    * wrap the address with u32() and check it is inside cpu.mem
"""

from cpu import funct3, rd, rs1, rs2, imm_i, imm_s, sext, u32


def check_addr(cpu, addr, size):
    if addr + size > len(cpu.mem):
        raise RuntimeError(f"memory access out of bounds: 0x{addr:08x} ({size} bytes) at pc=0x{cpu.pc:08x}")


def read_mem(cpu, addr, size):
    """Return `size` bytes at `addr` as an unsigned int."""
    check_addr(cpu, addr, size)
    return int.from_bytes(cpu.mem[addr:addr + size], "little")


def write_mem(cpu, addr, size, value):
    """Store the low `size` bytes of `value` at `addr`."""
    check_addr(cpu, addr, size)
    cpu.mem[addr:addr + size] = (value & ((1 << (8 * size)) - 1)).to_bytes(size, "little")


def exec_load(cpu, inst):
    addr = u32(cpu.reg[rs1(inst)] + imm_i(inst))
    f3 = funct3(inst)

    # TODO(C): lb(0) lh(1) lw(2) lbu(4) lhu(5)
    raise NotImplementedError(f"load funct3={f3}")

    return cpu.pc + 4


def exec_store(cpu, inst):
    addr = u32(cpu.reg[rs1(inst)] + imm_s(inst))
    value = cpu.reg[rs2(inst)]
    f3 = funct3(inst)

    # TODO(C): sb(0) sh(1) sw(2)
    raise NotImplementedError(f"store funct3={f3}")

    return cpu.pc + 4


HANDLERS = {
    0x03: exec_load,
    0x23: exec_store,
}
