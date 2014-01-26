#!/usr/bin/python3

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

from eeprom_blobs import Eeprom
from struct import unpack
import vsdsp
import sys


if __name__ == '__main__':
    eeprom = open(sys.argv[1], 'rb').read()
    eeprom = Eeprom.decode(eeprom)

    codes = vsdsp.Codes()
    _exec = None
    sect_data = []
    for block in eeprom[0]:
        if block['name'] == 'exec':
            _exec = block['addr']
            continue
        if block['name'] != 'firmware':
            continue
        if block['addr'] >= 0x8000:
            sect_data.append(block)
            continue
        data = block['data']
        org = divmod(block['addr'] - 0x2000, 2)[0]
        code = vsdsp.Code.disassemble(data, org=org)
        codes.append(code)

    for d in sect_data:
        print('.sect data_x, _0x%x' % d['addr'])
        print('.org 0x%04x' % d['addr'])
        d = d['data']
        d = unpack('>' + 'H' * int(len(d) / 2), d)
        d = ', '.join(['0x%04x' % i for i in d])
        print('.uword %s' % d)
        print()

    print('.sect code, bool_loader')
    if _exec is not None:
        print('.start 0x%04x\n' % _exec)
    print(codes.text(opcode=True))

