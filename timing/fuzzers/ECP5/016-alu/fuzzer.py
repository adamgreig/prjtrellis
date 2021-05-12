import cell_fuzzers


def generate_name(name, reg_in, reg_pl, reg_out, bypass):
    onoff = {True: "on", False: "off"}
    name = f'{name}_regin_{onoff[reg_in]}_regpl_{onoff[reg_pl]}'
    name += f'_regout_{onoff[reg_out]}_bypass_{onoff[bypass]}'
    return name


def generate_mult(name, reg_in, reg_pl, reg_out, bypass, clk, cen, rst, a, b, roab, p, ps):
    inregs = ["INPUTA", "INPUTB", "INPUTC"]
    out = ["MULT18X18D #("]
    for reg in inregs + ["PIPELINE", "OUTPUT"]:
        if (reg in inregs and reg_in):
            out.append(f'    .REG_{reg}_CLK("CLK0"),')
        elif reg == "PIPELINE" and reg_pl and not bypass:
            out.append(f'    .REG_{reg}_CLK("CLK0"),')
        elif reg == "OUTPUT" and reg_out and bypass:
            out.append(f'    .REG_{reg}_CLK("CLK0"),')
        else:
            out.append(f'    .REG_{reg}_CLK("NONE"),')
        out.append(f'    .REG_{reg}_CE("CE0"),')
        out.append(f'    .REG_{reg}_RST("RST0"),')
    for x in range(4):
        out.append(f'    .CLK{x}_DIV("ENABLED"),')
    out.append('    .GSR("ENABLED"),')
    out.append('    .RESETMODE("SYNC"),')
    out.append('    .SOURCEB_MODE("B_SHIFT"),')
    if bypass:
        out.append('    .MULT_BYPASS("ENABLED"),')
    else:
        out.append('    .MULT_BYPASS("DISABLED"),')
    out.append('    .HIGHSPEED_CLK("NONE")')
    name = generate_name(name, reg_in, reg_pl, reg_out, bypass)
    out.append(f') mult_{name} (')

    for pname, pval, width in [("A", a, 18), ("B", b, 18), ("P", p, 36)]:
        port = []
        for x in range(width):
            port.append(f'.{pname}{x}({pval}[{x}])')
        out.append("    " + ", ".join(port) + ",")

    for pname, pval, width in [
        ("C", "1'b0", 18), ("SRIA", "1'b0", 18), ("SRIB", "1'b0", 18),
        ("SROA", "", 18), ("SROB", "", 18), ("ROC", "", 18),
    ]:
        port = []
        for x in range(width):
            port.append(f'.{pname}{x}({pval})')
        out.append("    " + ", ".join(port) + ",")

    port = []
    for x in range(18):
        port.append(f'.ROA{x}({roab}[{x}])')
    for x in range(18, 36):
        port.append(f'.ROB{x - 18}({roab}[{x}])')
    out.append("    " + ", ".join(port) + ",")

    out.append('    .SIGNEDA(1\'b1), .SIGNEDB(1\'b1), .SOURCEA(1\'b0), .SOURCEB(1\'b0),')
    out.append(f'    .CE0({cen}), .CE1(1\'b0), .CE2(1\'b0), .CE3(1\'b0),')
    out.append(f'    .CLK0({clk}), .CLK1(1\'b0), .CLK2(1\'b0), .CLK3(1\'b0),')
    out.append(f'    .RST0({rst}), .RST1(1\'b0), .RST2(1\'b0), .RST3(1\'b0),')
    out.append(f'    .SIGNEDP({ps}));')

    return name, "\n".join(out)


def generate_alu(
    reg_in, reg_pl, reg_out, bypass, clk, cen, rst,
    c, ma_roab, mb_roab, ma_p, ma_ps, mb_p, mb_ps, r
):
    out = ["ALU54B #("]
    cregs = ["INPUTCFB", "INPUTC0", "INPUTC1"]
    inregs = ["OPCODEIN_1", "OPCODEIN_0"]
    plregs = ["OPCODEOP0_1", "OPCODEOP0_0"]
    outregs = ["FLAG", "OUTPUT0", "OUTPUT1"]
    for reg in cregs + inregs + plregs + outregs:
        if reg in inregs and reg_in:
            out.append(f'    .REG_{reg}_CLK("CLK0"),')
        elif reg in plregs and reg_pl:
            out.append(f'    .REG_{reg}_CLK("CLK0"),')
        elif reg in outregs and reg_out:
            out.append(f'    .REG_{reg}_CLK("CLK0"),')
        else:
            out.append(f'    .REG_{reg}_CLK("NONE"),')
        out.append(f'    .REG_{reg}_CE("CE0"),')
        out.append(f'    .REG_{reg}_RST("RST0"),')
    if reg_in:
        out.append('    .REG_OPCODEOP1_0_CLK("CLK0"),')
        out.append('    .REG_OPCODEOP1_1_CLK("CLK0"),')
    else:
        out.append('    .REG_OPCODEOP1_0_CLK("NONE"),')
        out.append('    .REG_OPCODEOP1_1_CLK("NONE"),')
    for x in range(4):
        out.append(f'    .CLK{x}_DIV("ENABLED"),')
    out.append('    .LEGACY("DISABLED"),')
    out.append('    .MULT9_MODE("DISABLED"),')
    out.append('    .RNDPAT("0x00000000000000"),')
    out.append('    .MASKPAT("0x00000000000000"),')
    out.append('    .MCPAT("0x00000000000000"),')
    out.append('    .MASK01("0x00000000000000"),')
    out.append('    .MASKPAT_SOURCE("STATIC"),')
    out.append('    .MCPAT_SOURCE("STATIC"),')
    out.append('    .RESETMODE("SYNC"),')
    out.append('    .GSR("ENABLED")')

    name = generate_name("", reg_in, reg_pl, reg_out, bypass)
    out.append(f') alu{name} (')

    for pname, pval in [("A", ma_roab), ("B", mb_roab), ("MA", ma_p), ("MB", mb_p)]:
        port = []
        for x in range(36):
            port.append(f'.{pname}{x}({pval}[{x}])')
        out.append("    " + ", ".join(port) + ",")

    port = []
    for x in range(54):
        port.append(f'.C{x}({c}[{min(x, 35)}])')
    out.append("    " + ", ".join(port) + ",")

    port = []
    for x in range(54):
        port.append(f'.CFB{x}(1\'b0)')
    out.append("    " + ", ".join(port) + ",")

    port = []
    for x in range(36):
        port.append(f'.R{x}({r}[{x}])')
    for x in range(36, 54):
        port.append(f'.R{x}()')
    out.append("    " + ", ".join(port) + ",")

    out.append(f'    .SIGNEDIA({ma_ps}), .SIGNEDIB({mb_ps}),')
    out.append(f'    .CE0({cen}), .CE1(1\'b0), .CE2(1\'b0), .CE3(1\'b0),')
    out.append(f'    .CLK0({clk}), .CLK1(1\'b0), .CLK2(1\'b0), .CLK3(1\'b0),')
    out.append(f'    .RST0({rst}), .RST1(1\'b0), .RST2(1\'b0), .RST3(1\'b0),')

    # Set AMUX and BMUX to A and B inputs when bypassed, or MA and MB when not.
    if bypass:
        op = [0, 1, 0, 1, 1, 1, 0, 0, 0, 1, 0]
    else:
        op = [1, 0, 1, 0, 1, 1, 0, 0, 0, 1, 0]
    port = []
    for x in range(11):
        port.append(f'.OP{x}(1\'b{op[x]})')
    out.append("    " + ", ".join(port) + ");")

    return name, "\n".join(out)


def generate_mac(reg_in, reg_pl, reg_out, bypass):
    out = []

    ma_p = generate_name("ma_p", reg_in, reg_pl, reg_out, bypass)
    mb_p = generate_name("mb_p", reg_in, reg_pl, reg_out, bypass)
    ma_roab = generate_name("ma_roab", reg_in, reg_pl, reg_out, bypass)
    mb_roab = generate_name("mb_roab", reg_in, reg_pl, reg_out, bypass)
    ma_ps = generate_name("ma_ps", reg_in, reg_pl, reg_out, bypass)
    mb_ps = generate_name("mb_ps", reg_in, reg_pl, reg_out, bypass)
    r = generate_name("r", reg_in, reg_pl, reg_out, bypass)

    out.append(f"wire [35:0] {ma_p}, {mb_p}, {ma_roab}, {mb_roab};")
    out.append(f"wire {ma_ps}, {mb_ps};")
    out.append(f"wire [53:0] {r};")

    name_ma, out_ma = generate_mult("a", reg_in, reg_pl, reg_out, bypass,
                                    "CLK", "CEN", "RESET", "AA", "AB",
                                    ma_roab, ma_p, ma_ps)
    name_mb, out_mb = generate_mult("b", reg_in, reg_pl, reg_out, bypass,
                                    "CLK", "CEN", "RESET", "BA", "BB",
                                    mb_roab, mb_p, mb_ps)
    name_alu, out_alu = generate_alu(reg_in, reg_pl, reg_out, bypass,
                                     "CLK", "CEN", "RESET", "C",
                                     ma_roab, mb_roab, ma_p, ma_ps,
                                     mb_p, mb_ps, r)

    out += out_ma, out_mb, out_alu
    return "\n".join(out)


def generate_mod():
    out = [
        "module top(",
        "    input [3:0] sel,",
        "    input [17:0] AA, AB, BA, BB,",
        "    input [35:0] C,",
        "    output [53:0] R_Q,",
        "    input CLK, CEN, RESET",
        ");",
        "wire [54:0] R [0:15];",
        "assign R_Q = R[sel];",
    ]

    for x in range(16):
        bypass = x & 0b1000 == 0b1000
        reg_in = x & 0b0100 == 0b0100
        reg_pl = x & 0b0010 == 0b0010
        reg_out = x & 0b0001 == 0b0001
        out.append(generate_mac(reg_in, reg_pl, reg_out, bypass))
        r = generate_name("r", reg_in, reg_pl, reg_out, bypass)
        out.append(f"assign R[{x}] = {r};")

    return "\n".join(out) + "\nendmodule\n"


def include_cell(name, type):
    return type.startswith("alu_")


def rewrite_cell_pipemode(name, type):
    if type.startswith("alu_"):
        settings = type.split("_")
        regin = "REG" if settings[2] == "on" else "NOREG"
        regpl = "REG" if settings[4] == "on" else "NOREG"
        regout = "REG" if settings[6] == "on" else "NOREG"
        bypass = "ON" if settings[8] == "on" else "OFF"
        return f"ALU54B:IN={regin},PL={regpl},OUT={regout},BYPASS={bypass}"
    else:
        return type


def rewrite_pin(name, type, pin):
    # All DSP pins have the same timings
    if not name.startswith("alu_reg"):
        return pin
    if pin[:2] in ("AA", "AB", "BA", "BB", "MA", "MB") and pin[2:].isdigit():
        return pin[:2]
    if pin[0] in "ABCRP" and pin[1:].isdigit():
        return pin[0]
    else:
        return pin


def main():
    with open("alu.v", "w") as f:
        f.write(generate_mod())

    cell_fuzzers.build_and_add(
        ["alu.v"],
        inc_cell=include_cell,
        rw_cell_func=rewrite_cell_pipemode,
        rw_pin_func=rewrite_pin
    )


if __name__ == "__main__":
    main()
