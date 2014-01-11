from struct import unpack


class Arg:
    def __init__(self, code, offs, size):
        self._value = (code >> offs) & ((1 << size) - 1)

    def __str__(self):
        return hex(self._value)


class ArgConst(Arg):
    def __init__(self, code, offs, size):
        Arg.__init__(self, code, offs, size)


class ArgReg16(Arg):
    def __init__(self, code, offs):
        Arg.__init__(self, code, offs, 3)

    def __str__(self):
        return {
                0: "A0",
                1: "A1",
                2: "B0",
                3: "B1",
                4: "C0",
                5: "C1",
                6: "D0",
                7: "D1",
                }[self._value]


class ArgRegExt(Arg):
    def __init__(self, code, offs):
        Arg.__init__(self, code, offs, 3)

    def __str__(self):
        return {
                0: "Reserver",
                1: "A",
                2: "Reserver",
                3: "B",
                4: "Reserver",
                5: "C",
                6: "Reserver",
                7: "D",
                }[self._value]


class ArgRegALUOp(Arg):
    def __init__(self, code, offs):
        Arg.__init__(self, code, offs, 4)

    def __str__(self):
        return {
                0: "A0",
                1: "A1",
                2: "B0",
                3: "B1",
                4: "C0",
                5: "C1",
                6: "D0",
                7: "D1",
                8: "NULL",
                9: "ONES",
                10: "Reserver",
                11: "P",
                12: "A",
                13: "B",
                14: "C",
                15: "D",
                }[self._value]


class ArgRegFull(Arg):
    def __init__(self, code, offs):
        Arg.__init__(self, code, offs, 6)

    def __str__(self):
        return {
                0b000000: "A0",
                0b000001: "A1",
                0b000010: "B0",
                0b000011: "B1",
                0b000100: "C0",
                0b000101: "C1",
                0b000110: "D0",
                0b000111: "D1",
                0b001000: "LR0",
                0b001001: "LR1",
                0b001010: "MR0",
                0b001011: "MR1",
                0b001100: "NULL",
                0b001101: "LC",
                0b001110: "LS",
                0b001111: "LE",
                0b010000: "I0",
                0b010001: "I1",
                0b010010: "I2",
                0b010011: "I3",
                0b010100: "I4",
                0b010101: "I5",
                0b010110: "I6",
                0b010111: "I7",
                0b011000: "I8",
                0b011001: "I9",
                0b011010: "I10",
                0b011011: "I11",
                0b011100: "I12",
                0b011101: "I13",
                0b011110: "I14",
                0b011111: "I15",
                0b100000: "A2",
                0b100001: "B2",
                0b100010: "C2",
                0b100011: "D2",
                0b100100: "NOP",
                0b100101: "Reserver",
                0b100110: "Reserver",
                0b100111: "Reserver",
                0b101000: "Reserver",
                0b101001: "Reserver",
                0b101010: "Reserver",
                0b101011: "Reserver",
                0b101100: "Reserver",
                0b101101: "Reserver",
                0b101110: "Reserver",
                0b101111: "Reserver",
                0b110000: "Reserver",
                0b110001: "Reserver",
                0b110010: "Reserver",
                0b110011: "Reserver",
                0b110100: "Reserver",
                0b110101: "Reserver",
                0b110110: "Reserver",
                0b110111: "Reserver",
                0b111000: "Reserver",
                0b111001: "Reserver",
                0b111010: "Reserver",
                0b111011: "Reserver",
                0b111100: "Reserver",
                0b111101: "Reserver",
                0b111110: "IPR0",
                0b111111: "IPR1",
                }[self._value]


class Instruction:
    def __init__(self, name, op, args, parallel=None):
        """name - instruction mnemonic
        opcode - instruction opcode prefix
        mask - number of bits in opcode (3-8)
        parallel - if True, instruction is 16 and is followed by another instruction"""
        self.name = name
        self.op = op
        self.args = args
        self.parallel = parallel

    def __str__(self):
        s = self.name
        if self.args:
            s += "\t" + self._str_args()
        if self.parallel is not None:
            s += ";\t" + str(self.parallel)
        return s

    def _str_args(self):
        return ", ".join([str(s) for s in self.args])


class OpLDC(Instruction):
    def __init__(self, code):
        self.code = code
        args = (
                ArgConst(code, 6, 5*4+3),
                ArgRegFull(code, 0),
                )
        Instruction.__init__(self, "LDC", 0, args)


class OpSingle(Instruction):
    def __init__(self, code):
        self.code = code
        pass


class OpParallel(Instruction):
    def __init__(self, code):
        self.code = code
        pass


class Decoder:
    def __init__(self, buf, offs=0):
        """Decode instructions from buffer."""
        self._buf = buf
        self._offs = offs

    def decode(self, n=None):
        instr = []
        if n is None:
            n = divmod(len(self._buf), 4)[0]
        while n:
            code = unpack('<I', self._buf[self._offs:self._offs+4])[0]
            self._offs += 4
            n -= 1
            op = code & 0xd0000000
            if op == 0:
                instr.append(OpLDC(code))
                continue
            if op == 1:
                instr.append(OpSingle(code))
                continue
            instr.append(OpParallel(code))

        return instr


