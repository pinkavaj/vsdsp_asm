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
# finish previous CALL
        (0xb8, 0x8c, 0x40, 0xc0, ),
        (0x36, 0xf1, 0xd8, 0x02, ),
        (0x36, 0xf2, 0x18, 0x17, ),
        (0x36, 0xf4, 0xd8, 0x03, ),

        (0x00, 0x02, 0x00, 0x12, ), # LDC     0x0800, I2
        (0x00, 0x00, 0x00, 0x86, ), # LDC     0x0002, D0

        (0x29, 0x08, 0x3e, 0x40, ), # CALL 0x20f9
        (0x00, 0x00, 0x00, 0x24, ), # NOP

        (0xf4, 0x00, 0x40, 0xd2, ), # MV B1, I2
        (0x00, 0x00, 0x00, 0x46, ), # LDC     0x0001, D0
        (0x29, 0x08, 0x3e, 0x40, ), # CALL 0x20f9
        (0x00, 0x00, 0x00, 0x24, ), # NOP

        (0xf4, 0x00, 0x40, 0xd2, ), # MV B1, I2
        (0x00, 0x00, 0x00, 0x46, ), # LDC     0x0001, D0
        (0x29, 0x08, 0x3e, 0x40, ), # CALL 0x20f9
        (0x00, 0x00, 0x00, 0x24, ), # NOP

        (0xf4, 0x00, 0x40, 0xd2, ), # MV B1, I2
        (0x00, 0x00, 0x00, 0x46, ), # LDC     0x0001, D0
        (0x29, 0x08, 0x3e, 0x40, ), # CALL 0x20f9
        (0x00, 0x00, 0x00, 0x24, ), # NOP

        (0xf4, 0x00, 0x40, 0xd2, ), # MV B1, I2
        (0x00, 0x00, 0x00, 0x46, ), # LDC     0x0001, D0
        (0x29, 0x08, 0x3e, 0x40, ), # CALL 0x20f9
        (0x00, 0x00, 0x00, 0x24, ), # NOP

        (0xf4, 0x00, 0x40, 0xd2, ), # MV B1, I2
        (0x00, 0x00, 0x00, 0x46, ), # LDC     0x0001, D0
        (0x29, 0x08, 0x3e, 0x40, ), # CALL 0x20f9
        (0x00, 0x00, 0x00, 0x24, ), # NOP

        (0xf4, 0x00, 0x40, 0xd2, ), # MV B1, I2
        (0x00, 0x00, 0x00, 0x46, ), # LDC     0x0001, D0
        (0x29, 0x08, 0x3e, 0x40, ), # CALL 0x20f9
        (0x00, 0x00, 0x00, 0x24, ), # NOP

        (0xf4, 0x00, 0x40, 0xd2, ), # MV B1, I2
        (0x00, 0x00, 0x00, 0x46, ), # LDC     0x0001, D0
        (0x29, 0x08, 0x3e, 0x40, ), # CALL 0x20f9
        (0x00, 0x00, 0x00, 0x24, ), # NOP

        (0xf4, 0x00, 0x40, 0xd2, ), # MV B1, I2
        (0x00, 0x00, 0x00, 0x46, ), # LDC     0x0001, D0
        (0x29, 0x08, 0x3e, 0x40, ), # CALL 0x20f9
        (0x00, 0x00, 0x00, 0x24, ), # NOP

        #(0x28, 0x07, 0xdc, 0xc0, ), # J 0x1f73
        #(0x29, 0x07, 0xdf, 0x40, ), # J 0x1f7d

# jump back and get another word
        (0x00, 0x00, 0x00, 0x24, ), # NOP
        (0x00, 0x00, 0x00, 0x24, ), # NOP
        (0x28, 0x07, 0xe8, 0x00, ), # J 0x1fa0
        (0x00, 0x00, 0x00, 0x24, ), # NOP
        )

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
    code = vsdsp.Code.disassemble(data, 0)
    codes = vsdsp.Codes()
    codes.append(code)
    print(codes.text())

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

