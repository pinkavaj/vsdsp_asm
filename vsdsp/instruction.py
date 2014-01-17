# Copyright (c) 2014, whoever
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
# 
#    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
#    ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
#    WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#    DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
#    ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
#    (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
#    LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#    ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#    (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#    SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from struct import unpack


def Todo(str=""):
    """Not implemented warning/error switch."""
    raise NotImplementedError(str)
    print("TODO %s" % str)
    return str


class Arg(object):
    """Extract integer argument value from opcode."""
    def __init__(self, value, offs=None, size=None):
        object.__init__(self)
        if offs is None and size is None:
            if isinstance(value, Arg):
                self.value = value.value
                return
            else:
                self.value = value
                return
        elif isinstance(value, Op):
            self.value = value.val(offs, size)
            return
        raise TypeError('value %s, offs %s, size %s' % (value, offs, size, ))

    def __str__(self):
        return hex(self.value)


class ArgAddrI(Arg):
    """Addressing using index register, optionally with postmodification."""
    def __init__(self, op, offs, size = 4):
        self.reg = op.val(offs + size, 3)
        self.post_mod = op.sval(offs, size)
        Arg.__init__(self, [self.reg, self.post_mod])

    def __str__(self):
        if self.post_mod == -8:
            return Todo("ArgAddrI -8")
        if self.post_mod:
            return '(I%d)%+d' % (self.reg, self.post_mod)
        return '(I%d)' % (self.reg, )


class ArgAddrIJ(ArgAddrI):
    def __init__(self, op):
        self.reg = op.val(0, 3)
        self.post_mod = op.sval(3, 2)
        Arg.__init__(self, [self.reg, self.post_mod])


class ArgAddrIShort(ArgAddrI):
    """Addressing using index register, optionally with postmodification."""
    def __init__(self, op, offs):
        ArgAddrI.__init__(self, op, offs, 1)
        if self.post_mod:
            self.post_mod = -8


class ArgAddrIReg(Arg):
    """Addressing using index register."""
    def __init__(self, op, offs):
        Arg.__init__(self, op, offs, 3)

    def __str__(self):
        return "(I%s)" % self.value


class ArgAddrJ(Arg):
    def __init__(self, op, offs, size):
        Arg.__init__(self, op, offs, size)


class ArgJCond(Arg):
    def __init__(self, op):
        Arg.__init__(self, op, 0, 6)

    def __str__(self):
        return {
                0b000000: '',
                0b000001: 'CS',
                0b000010: 'ES',
                0b000011: 'VS',
                0b000100: 'NS',
                0b000101: 'ZS',
                0b000110: 'XS',
                0b000111: 'YS',
                0b001000: 'LT',
                0b001001: 'LE',
                0b010001: 'CC',
                0b010010: 'EC',
                0b010011: 'VC',
                0b010100: 'NC',
                0b010101: 'ZC',
                0b010110: 'XC',
                0b010111: 'YC',
                0b011000: 'GE',
                0b011001: 'GT',
                }[self.value]


class ArgJmpiMode(ArgAddrIReg):
    def __init__(self, op):
        ArgAddrIReg.__init__(self, op, 0)
        self.mode = op.sval(3, 2)
        if self.mode == -2:
            raise ValueError('-2 is invalid for JMPI mode')

    def __bool__(self):
        return bool(self.mode)

    def __str__(self):
        if self.mode:
            return '%s%+d' % (ArgAddrIReg.__str__(self), self.mode, )
        return ArgAddrIReg.__str__(self)


class ArgConst(Arg):
    def __init__(self, op, offs, size):
        Arg.__init__(self, op, offs, size)


class ArgReg16(Arg):
    def __init__(self, op, offs):
        Arg.__init__(self, op, offs, 3)

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
                }[self.value]


class ArgRegALUOp(Arg):
    def __init__(self, op, offs):
        Arg.__init__(self, op, offs, 4)

    def __str__(self):
        return {
                0x0: "A0",
                0x1: "A1",
                0x2: "B0",
                0x3: "B1",
                0x4: "C0",
                0x5: "C1",
                0x6: "D0",
                0x7: "D1",
                0x8: "NULL",
                0x9: "ONES",
                0xb: "P",
                0xc: "A",
                0xd: "B",
                0xe: "C",
                0xf: "D",
                }[self.value]

    def wide(self):
        return self.value >= 0xb and self.value <= 0xf


class ArgRegFull(Arg):
    def __init__(self, opcode, offs):
        Arg.__init__(self, opcode, offs, 6)

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
                0b111110: "IPR0",
                0b111111: "IPR1",
                }[self.value]

    def nop(self):
        return self.value == 0b100100


class ArgRegLoop(Arg):
    def __init__(self, op):
        Arg.__init__(self, op, 0, 5)

    def __str__(self):
        return {
                0x00: "A0",
                0x01: "A1",
                0x02: "B0",
                0x03: "B1",
                0x04: "C0",
                0x05: "C1",
                0x06: "D0",
                0x07: "D1",
                0x08: 'LR0',
                0x09: 'LR1',
                0x0a: 'MR0',
                0x0b: 'MR1',
                0x0d: 'LC',
                0x0e: 'LS',
                0x0f: 'LE',
                0x10: 'I0',
                0x11: 'I1',
                0x12: 'I2',
                0x13: 'I3',
                0x14: 'I4',
                0x15: 'I5',
                0x16: 'I6',
                0x17: 'I7',
                }[self.value]


class ArgRegWide(Arg):
    def __init__(self, op, offs):
        Arg.__init__(self, op, offs, 3)

    def __str__(self):
        return {
                1: "A",
                3: "B",
                5: "C",
                7: "D",
                }[self.value]


class Asm(object):
    def __init__(self, name, args=[], parallel=None):
        """name - instruction mnemonic
        args - instruction arguments
        parallel - follow up parallel instruction"""
        object.__init__(self)
        if isinstance(name, Asm):
            self.name = name.name
            self.args = name.args
            self.parallel = name.parallel
        else:
            self.name = name
            if isinstance(args, Arg):
                self.args = [args, ]
            elif hasattr(args, '__iter__'):
                self.args = args
            else:
                ValueError("args mus be (iterable object of) instance(s) of Arg")
            self.parallel = parallel

    def __str__(self):
        s = self.name
        if self.args:
            s += "\t" + ", ".join([str(s) for s in self.args])
        if self.parallel:
            s += ";\t" + str(self.parallel)
        return s


class Op(object):
    def __init__(self, opcode):
        object.__init__(self)
        if isinstance(opcode, bytes):
            self.opcode = unpack('<I', opcode[:4])[0]
        elif isinstance(opcode, int):
            self.opcode = opcode
        elif isinstance(opcode, Op):
            self.opcode = opcode.opcode
        else:
            raise ValueError('Op %s' % opcode)

    def decode(self):
        op = self.val(28, 4)
        if (op & 0xe) == 0:
            return _LDC(self)
        if op == 0x2:
            return self._decode_control()
        if op == 0x3:
            return self._decode_double_full_move()
# all this instructions have support parallel move
        if op == 0xf:
            asm = self._decode_singlearg()
        elif op == 0x5 or op == 0x7:
            return Todo("decode %d" % op)
            return self._init_mac(op)
        else:
            asm = self._decode_aritm(op)
        asm.parallel = self._parallel_move()
        if asm.name == 'NOP':
            return AsmOp(asm.parallel, self)
        elif asm.parallel.name == 'NOP':
            asm.parallel = None
        return AsmOp(asm, self)

    def sval(self, offs, size):
        val = self.val(offs, size)
        if val > (1 << (size - 1)):
            return val - (1 << size)
        return val

    def val(self, offs, size):
        return (self.opcode >> offs) & ((1 << size) - 1)

    def _decode_aritm(self, op):
        arg1 = ArgRegALUOp(self, 24)
        arg2 = ArgRegALUOp(self, 20)
        if arg1.wide() or arg2.wide():
            arg3 = ArgRegWide(self, 17)
        else:
            arg3 = ArgReg16(self, 17)
        name = {
                4: 'ADD',
                6: 'SUB',
                8: 'ADDC',
                9: 'SUBC',
                11: 'AND',
                12: 'OR',
                13: 'XOR',
                } [op]
        return Asm(name, (arg1, arg2, arg3, ))

    def _decode_control(self):
        """Class of control instructions (J, CALL, RET, MV_, ...)."""
        subop = self.val(24, 4)
        if subop == 0:
            if self.val(23, 1):
                return _Jcc(Asm('JR', ArgAddrIReg(self.opcode, 6, 3)), self)
            return _Jcc(Asm('JR'), self)
        if subop == 8:
            return _Jcc(Asm('J', ArgAddrJ(self, 6, 18)), self)
        if subop == 9:
            return _Jcc(Asm('CALL', ArgAddrJ(self, 6, 18)), self)
        if subop == 0xa:
            asm = AsmOp('JMPI', ArgAddrJ(self, 6, 18), self)
            post_mod = ArgAddrIJ(self)
            if post_mod.post_mod:
                asm.args.append(post_mod)
            return asm
        if (subop & 0xc) == 0x4:
            args = (ArgAddrJ(self, 6, 20), ArgRegLoop(self), )
            return AsmOp('LOOP', args, self)
        if subop == 0xb:
            argsy= (ArgRegFull(self, 6), ArgRegFull(self, 0), )
            mvy = Asm('MVY', argsy)
            argsx = [ArgRegFull(self, 18), ArgRegFull(self, 12), ]
            return AsmOp('MVX', argsx, mvy, self)

        return Todo("OpControl %s" % hex(opcode))

    def _decode_double_full_move(self):
        mov1 = self._full_move('X', 14)
        mov2 = self._full_move('Y')
        if mov1.name == 'NOP':
            if mov2.name == 'NOP':
                raise Error(WTF)
            return AsmOp(mov2, self)
        if mov2.name != 'NOP':
            mov1.parallel = mov2
        return AsmOp(mov1, self)

    def _full_move(self, bus, offs=0):
        opcode = Op(self.val(offs, 14))
        reg = ArgRegFull(opcode, 0)
        store = opcode.val(13, 1)
        reg_addr = ArgAddrI(opcode, 6)
        if reg.nop() and store == 0 and reg_addr.post_mod == 0:
# check value stored to NOP?
            return Asm('NOP')
        name = { 0: 'LD', 1: 'ST' } [store] + bus
        if store:
            return Asm(name, (reg, reg_addr, ))
        else:
            return Asm(name, (reg_addr, reg, ))

    def _init_mac(self, op):
        Todo("_init_mac %s" % hex(self.opcode))

    def _decode_mul(self):
        _format = {
                0: 'SS',
                1: 'SU',
                2: 'US',
                3: 'UU',
                } [self.val(23, 2)]
        arg1 = ArgReg16(self, 20)
        arg2 = ArgReg16(self, 17)
        return Asm('MUL' + _format, (ArgReg16(self, 20), ArgReg16(self, 17), ))

    def _decode_singlearg(self):
        subop = self.val(24, 4)
        if subop == 0x4:
            return Asm('NOP')
        if (subop & 0x0e) == 0xe:
            return self._decode_mul()
        name = {
                0: 'ABS',
                1: 'ASR',
                2: 'LSR',
                3: 'LSRC',
                5: 'EXP',
                #6: 'SAT',  # check args
                #7: 'RND',
                } [subop]
        arg1 = ArgRegALUOp(self, 20)
        if arg1.wide():
            arg2 = ArgRegWide(self, 17)
        else:
            arg2 = ArgReg16(self, 17)
        return Asm(name, (arg1, arg2, ))

    def _parallel_move(self):
        if self.val(16, 1):
            return self._short_moves()
        else:
            bus = self.val(14, 2)
            if bus == 0:
                return self._full_move('X')
            if bus == 2:
                return self._full_move('Y')
            if bus == 1:
                t = self.val(12, 2)
                if t == 0:
                    return self._reg_to_reg_move('X')
            return Todo("_parallel_move %d" % bus)

    def _reg_to_reg_move(self, bus):
        return Asm('MV' + bus, (ArgRegFull(self, 6), ArgRegFull(self, 0), ))

    def _short_move(self, offs, mov2=None):
        opcode = Op(self.val(offs, 8))
        bus = { 0: 'Y', 8: 'X' } [offs]
        reg_addr = ArgAddrIShort(opcode, 3)
        reg = ArgReg16(opcode, 0)
        if opcode.val(7, 1):
            return Asm('ST' + bus, (reg, reg_addr, ), mov2)
        else:
            return Asm('LD' + bus, (reg_addr, reg, ), mov2)

    def _short_moves(self):
        return self._short_move(8, self._short_move(0))


class AsmOp(Asm, Op):
    """Generic class for instructions withought special requirements."""
    def __init__(self, *args):
        if len(args) == 2:
            Asm.__init__(self, args[0])
            Op.__init__(self, args[1])
            return
        if len(args) == 3:
            Asm.__init__(self, args[0], args[1])
            Op.__init__(self, args[2])
            return
        if len(args) == 4:
            Asm.__init__(self, args[0], args[1], args[2])
            Op.__init__(self, args[3])
            return
        raise ValueError('AsmOp %s' % str(args))


class _Jcc(Asm, Op):
    def __init__(self, asm, op):
        asm.name += str(ArgJCond(op))
        Asm.__init__(self, asm)
        Op.__init__(self, op)


class _LDC(Asm, Op):
    """LDC instruction."""
    def __init__(self, op):
        arg1 = ArgConst(op, 6, 5*4+3)
        arg2 = ArgRegFull(op, 0)
        if arg2.nop():
            Asm.__init__(self, "NOP")
        else:
            Asm.__init__(self, "LDC", (arg1, arg2,))
        Op.__init__(self, op)


