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

from vsdsp.instruction import Op, ArgAddrJ


class Code(list):
    """Block of instruction code."""
    def __init__(self, org):
        list.__init__(self)
        self.org = org

    @staticmethod
    def assemble(buf):
        raise NotImplementedError('Instruction assembling not supported.')

    @staticmethod
    def disassemble(buf, offs=0, offs_end=None, org=None):
        """Dissassemble instruction(s) into code."""
        code = Code(org)
        if offs_end is None or offs_end > len(buf) - 3:
            offs_end = len(buf) - 3
        while offs < offs_end:
            op = Op(buf[offs:offs+4])
            code.append(op.decode())
            offs += 4
        return code

    def text(self, labels={}, opcode=False):
        text = ''
        if self.org is not None:
            text += '.org 0x%x\n' % self.org
        addr = self.org
        for asm in self:
            if addr in labels:
                text += '%s:\n' % labels[addr]
            txt = str(asm).split('\t')
            txt = txt + ['','','', '', '']
            txt = (txt[0].ljust(8),
                    txt[1].ljust(2*8+2),
                    txt[2].ljust(4),
                    txt[3].ljust(12),
                    txt[4].ljust(4),
                    txt[5].ljust(8),
                    )
            txt = ''.join(txt)
            if opcode:
                text += '%s\t// op: 0x%08x\n' % (txt, asm.opcode, )
            else:
                text += '%s\n' % (txt, )
            if addr is not None:
                addr += 1
        return text


class Codes(list):
    #def __init__(self):
    #    list.__init__(self)

    def _update_labels(self):
        """Update list of jump/call destionation addresses."""
        self.labels = {}
        for code in self:
            for asm in code:
                for a in asm.args:
                    if isinstance(a, ArgAddrJ):
                        self.labels[a.value] = '_0x%04x' % a.value
                if asm.name == 'LDC':
                    if str(asm.args[1]) == 'LR0':
                        value = asm.args[0].value
                        self.labels[value] = '_0x%04x' % value

    def text(self, opcode=False):
        self._update_labels()
        self.sort(key=lambda code: code.org)
        text = '\n'.join([code.text(labels=self.labels, opcode=opcode) for code in self])
        return text

