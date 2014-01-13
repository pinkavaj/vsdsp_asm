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

from eeprom_H4443759 import blocks, TYPE_BIN
from struct import unpack
import vsdsp


if __name__ == '__main__':
    for block in blocks:
        if block['type'] != TYPE_BIN:
            continue
        if block['addr'] >= 0x8000:
            continue
        data = block['data']
        decoder = vsdsp.Decoder(data)
        asms = decoder.decode()
        print("")
        print(".org 0x%x" % block['addr'])
        for asm in asms:
            txt = str(asm).split('\t')
            txt = txt + ['','','', '', '']
            txt = (txt[0].ljust(8) , txt[1].ljust(2*8+2), txt[2].ljust(4), txt[3].ljust(12), txt[4].ljust(4), txt[5].ljust(8) )
            txt = ''.join(txt)

            print('%s\t// op: 0x%08x' % (txt, asm.opcode, ))
            #print('%s' % (str(asm), ))

