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
from eeprom import Eeprom


patch_bin = (
        (0xf4, 0x00, 0x42, 0x01, ),
        (0x00, 0x00, 0x01, 0x40, ),
        (0x40, 0x10, 0x00, 0x24, ),
        (0xf4, 0x00, 0x40, 0x08, ),
        (0x00, 0x00, 0x00, 0x10, ),
        (0x30, 0x00, 0x00, 0x01, ),
        (0x38, 0x10, 0x20, 0x01, ),
        (0x20, 0x00, 0x00, 0x00, ),
        (0x00, 0x00, 0x00, 0x24, ),
        )
"""for (int = 0; ; ++i) { X[i] = X[i]; Y[i] = Y[i]; }"""

def big2little(data):
    """Convert 4B ints from big to little endian (and vice versa)."""
    d = []
    for d_ in data:
        d.append(d_[3])
        d.append(d_[2])
        d.append(d_[1])
        d.append(d_[0])
    return bytes(d)


if __name__ == '__main__':
    data = big2little(patch_bin)
    asms = vsdsp.disassemble(data)
    print("")
    print(".org 0x%x" % 0)
    print(vsdsp.asm2text(asms))

    if len(sys.argv) == 2:
        eeprom = open(sys.argv[1], 'rb').read()
        eeprom = Eeprom.decode(eeprom)
        for blob in eeprom[0]:
            for idx in range(0, len(blob.data)-3, 4):
                if blob.data[idx+3] == 0x29:
                    if len(blob.data) > len(data) + 8:
                        blob.data = blob.data[:idx+8] + data + blob.data[idx+8+len(data):]
                        open(sys.argv[1] + '.patch_0000.bin', 'wb').write(eeprom.blob())
                        sys.exit(0)
    raise RuntimeError('szz')

