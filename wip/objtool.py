# extracts blob from .o file and put it into EEPROM image

import sys
import vsdsp
from struct import unpack
from eeprom_blobs import Eeprom


def objdump(obj):
    obj_params = unpack('<IIIIIIII', obj[0x5C:0x5C + 4*8])
    print("%s" % str(obj_params))
    offs, offs, size, start, _, _, _, _ = obj_params
    if offs != 0x1f6c:
        raise ValueError("asdfasd")
    return obj[start:start+size]


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("<OBJ FILE> <SOURCE EEPROM IMAGE>")
        sys.exit(1)
    obj = open(sys.argv[1], 'rb').read()

    eeprom_file = sys.argv[2]
    eeprom = open(eeprom_file, 'rb').read()
    eeprom = Eeprom.decode(eeprom)
    for blob in eeprom[0]:
        if blob.addr == 0x5ed8:
            blob.data = objdump(obj)
            open(eeprom_file + '.patched.bin', 'wb').write(eeprom.blob())
            break

    code = vsdsp.Code.disassemble(blob.data, offs=0, org=0x1f6c)
    codes = vsdsp.Codes()
    codes.append(code)
    print(codes.text())

