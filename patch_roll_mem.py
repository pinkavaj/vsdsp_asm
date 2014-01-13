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

from struct import unpack
import sys
import vsdsp


def build(blocks):
    blob = b''
    for block in blocks:
        pass
    return blob

if __name__ == '__main__':
    # !!! writen at BIG endian
    data = ((0xf4, 0x00, 0x42, 0x01, ),
            (0x00, 0x00, 0x01, 0x40, ),
            (0x40, 0x10, 0x00, 0x24, ),
            (0xf4, 0x00, 0x40, 0x08, ),
            (0x00, 0x00, 0x00, 0x10, ),
            (0x30, 0x00, 0x00, 0x01, ),
            (0x38, 0x10, 0x20, 0x01, ),
            (0x20, 0x00, 0x00, 0x00, ),
            (0x00, 0x00, 0x00, 0x24, ),
            )
# convert to proper endianness
    d = []
    for d_ in data:
        d.append(d_[3])
        d.append(d_[2])
        d.append(d_[1])
        d.append(d_[0])
    data = bytes(d)

    decoder = vsdsp.Decoder(data)
    asms = decoder.decode()
    print("")
    print(".org 0x%x" % 0)
    for asm in asms:
        txt = str(asm).split('\t')
        txt = txt + ['','','', '', '']
        txt = (txt[0].ljust(8) , txt[1].ljust(2*8+2), txt[2].ljust(4), txt[3].ljust(12), txt[4].ljust(4), txt[5].ljust(8) )
        txt = ''.join(txt)

        print('%s\t// op: 0x%08x' % (txt, asm.opcode, ))
        #print('%s' % (str(asm), ))

    if len(sys.argv) == 2:
        open(sys.argv[1], 'wb').write(data)

