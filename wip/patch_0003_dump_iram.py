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

# original code
patch_head = (
        (0x00, 0x00, 0x80, 0x0a, ), # LDC     0x200, MR0
        (0x00, 0x00, 0x04, 0x16, ), # LDC     0x10, I6
        (0x00, 0x3f, 0xe9, 0x12, ), # LDC     0xffa4, I2
        (0x00, 0x00, 0x00, 0x00, ), # LDC     0x0, A0
        (0x3a, 0x00, 0x00, 0x24, ), # STX     A0, (I2)
        (0x28, 0x07, 0xdf, 0x40, ), # J 0x1f7d
        (0x00, 0x00, 0x00, 0x24, ), # NOP
# read EEPROM routine
        (0x36, 0x13, 0x00, 0x24, ), # LDX     (I6)+1, NULL
        (0x3e, 0x14, 0xf8, 0x03, ), # STX     I3, (I6)+1;       STY B1, (I6)
        (0x3e, 0x12, 0x38, 0x17, ), # STX     LR0, (I6)+1;      STY I7, (I6)
        (0x29, 0x08, 0x3e, 0x40, ), # CALL    0x20f9
        (0x68, 0x9d, 0xe7, 0xe2, ), # SUB     NULL, ONES, D0;   STX D1, (I6);   STY B0, (I6)
        (0xb8, 0x8c, 0x40, 0xc0, ), # AND     NULL, NULL, D0;   MVX B1, A0
        (0x36, 0xf1, 0xd8, 0x02, ), # LDX     (I6)-1, D1;       LDY (I6), B0
        (0x36, 0xf2, 0x18, 0x17, ), # LDX     (I6)-1, LR0;      LDY (I6), I7
        (0x20, 0x00, 0x00, 0x00, ), # JR
        (0x36, 0xf4, 0xd8, 0x03, ), # LDX     (I6)-1, I3;       LDY (I6), B1
        )

patch_my = (
        (0x00, 0x00, 0x00, 0x24, ), # NOP
        (0x00, 0x00, 0x00, 0x07, ), # LDC     0x0000, D1

        (0x00, 0x00, 0x00, 0x17, ), # LDC     0x0000, I7
        #(0x00, 0x08, 0x00, 0x17, ), # LDC     0x2000, I7

        (0xf4, 0x00, 0x41, 0xd2, ), # MV D1, I2
        (0x29, 0x07, 0xdc, 0xc0, ), # CALL    0x1f73
        (0x00, 0x00, 0x00, 0x24, ), # NOP

        (0xf4, 0x00, 0x45, 0xd2, ), # MV I7, I2
        (0x29, 0x07, 0xdc, 0xc0, ), # CALL    0x1f73
        (0x00, 0x00, 0x00, 0x24, ), # NOP

        (0x00, 0x00, 0x00, 0x07, ), # LDC     0x0000, D1
        (0x29, 0x08, 0x76, 0x40, ), # CALL 0x21d9
        (0x00, 0x00, 0x00, 0x24, ), # NOP


        (0x00, 0x00, 0x00, 0x00, ), # LDC     0x0000, A0
        #(0x00, 0x3f, 0xe9, 0x40, ), # LDC     0xffa5, A0
        (0xf4, 0x00, 0x44, 0x81, ), # MVX     I2, A1
        (0x61, 0x02, 0x00, 0x24, ), # SUB     D1, A1, A1
        (0x00, 0x00, 0x00, 0x24, ), # NOP


        #(0x28, 0x07, 0xdc, 0xc0, ), # J 0x1f73
        #(0x28, 0x07, 0xe0, 0x00, ), # J 0x1f80
        (0x28, 0x07, 0xe0, 0x15, ), # JZC 0x1f80

# jump back and get another word
        (0x00, 0x00, 0x00, 0x24, ), # NOP
        (0x00, 0x00, 0x00, 0x24, ), # NOP
        (0x00, 0x00, 0x00, 0x24, ), # NOP
        (0x00, 0x00, 0x00, 0x24, ), # NOP
        (0x00, 0x00, 0x00, 0x24, ), # NOP
        (0x00, 0x00, 0x00, 0x24, ), # NOP
        (0x00, 0x00, 0x00, 0x24, ), # NOP
        (0x00, 0x00, 0x00, 0x24, ), # NOP
        (0x00, 0x00, 0x00, 0x24, ), # NOP
        (0x00, 0x00, 0x00, 0x24, ), # NOP
        (0x00, 0x00, 0x00, 0x24, ), # NOP
        (0x00, 0x00, 0x00, 0x24, ), # NOP
        (0x00, 0x00, 0x00, 0x24, ), # NOP
        (0x00, 0x00, 0x00, 0x24, ), # NOP
        (0x00, 0x00, 0x00, 0x24, ), # NOP
        (0x00, 0x00, 0x00, 0x24, ), # NOP
        (0x00, 0x00, 0x00, 0x24, ), # NOP
        (0x00, 0x00, 0x00, 0x24, ), # NOP
        (0x00, 0x00, 0x00, 0x24, ), # NOP
        (0x00, 0x00, 0x00, 0x24, ), # NOP
        (0x00, 0x00, 0x00, 0x24, ), # NOP
        (0x00, 0x00, 0x00, 0x24, ), # NOP
        (0x00, 0x00, 0x00, 0x24, ), # NOP
        (0x00, 0x00, 0x00, 0x24, ), # NOP
        (0x28, 0x07, 0xe8, 0x00, ), # J 0x1fa0
        (0x00, 0x00, 0x00, 0x24, ), # NOP
        )

patch_bin = patch_head + patch_my


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
    code = vsdsp.Code.disassemble(data, offs=0, org=0x1f6c)
    codes = vsdsp.Codes()
    codes.append(code)
    print(codes.text())

    if len(sys.argv) == 2:
        eeprom = open(sys.argv[1], 'rb').read()
        eeprom = Eeprom.decode(eeprom)
        for blob in eeprom[0]:
            if blob.addr == 0x5ed8:
                blob.data = data + blob.data[len(data):]
                open(sys.argv[1] + '.patch_0000.bin', 'wb').write(eeprom.blob())
                sys.exit(0)
    raise RuntimeError('szz')

