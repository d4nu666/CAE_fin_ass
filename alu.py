"""
alu.py - arithmetic and logic instructions.             OWNER: Person A

    0x33  R-type : add sub sll slt sltu xor srl sra or and
    0x13  I-type : addi slti sltiu xori ori andi slli srli srai
    0x37  lui
    0x17  auipc

Every handler has the signature  handler(cpu, inst) -> next_pc
and normally returns cpu.pc + 4.

Remember:
    * write results with cpu.write_reg(rd, value) - it wraps to 32 bits
    * signed compare / arithmetic shift need s32(); unsigned compare uses the raw value
    * shift amount = low 5 bits (rs2 value & 0x1F, or imm & 0x1F)
    * sub/sra and srai are told apart from add/srl/srli by funct7 == 0x20
"""

from cpu import funct3, funct7, rd, rs1, rs2, imm_i, imm_u, s32, u32


def exec_r_type(cpu, inst):
    a = cpu.reg[rs1(inst)]
    b = cpu.reg[rs2(inst)]
    f3, f7 = funct3(inst), funct7(inst)

    # TODO(A): add sub sll slt sltu xor srl sra or and
    raise NotImplementedError(f"R-type funct3={f3} funct7=0x{f7:02x}")

    return cpu.pc + 4


def exec_i_type(cpu, inst):
    a = cpu.reg[rs1(inst)]
    imm = imm_i(inst)
    f3 = funct3(inst)

    if f3 == 0x0:       # addi
        cpu.write_reg(rd(inst), a + imm)

    elif f3 == 0x4:     # xori
        cpu.write_reg(rd(inst), a ^ imm)

    elif f3 == 0x6:     # ori
        cpu.write_reg(rd(inst), a | imm)

    elif f3 == 0x7:     # andi
        cpu.write_reg(rd(inst), a & imm)

    elif f3 == 0x1:     # slli
        if funct7(inst) != 0x00:
            raise NotImplementedError("Invalid slli encoding")

        shamt = (inst >> 20) & 0x1F
        cpu.write_reg(rd(inst), a << shamt)

    elif f3 == 0x5:     # srli or srai
        shamt = (inst >> 20) & 0x1F
        f7 = funct7(inst)

        if f7 == 0x00:       # srli
            cpu.write_reg(rd(inst), a >> shamt)

        elif f7 == 0x20:     # srai
            cpu.write_reg(rd(inst), s32(a) >> shamt)

        else:
            raise NotImplementedError("Invalid right-shift encoding") 

    elif f3 == 0x2:     # slti
        result = 1 if s32(a) < imm else 0
        cpu.write_reg(rd(inst), result)

    elif f3 == 0x3:     # sltiu
        result = 1 if a < u32(imm) else 0
        cpu.write_reg(rd(inst), result)    
        
    else:
        # Unsupported encoding
        raise NotImplementedError(f"I-type funct3={f3}")

    return cpu.pc + 4


def exec_lui(cpu, inst):
    # TODO(A): rd = imm_u
    raise NotImplementedError("lui")


def exec_auipc(cpu, inst):
    # TODO(A): rd = pc + imm_u
    raise NotImplementedError("auipc")


HANDLERS = {
    0x33: exec_r_type,
    0x13: exec_i_type,
    0x37: exec_lui,
    0x17: exec_auipc,
}
