from data import data
from struct import unpack
import vsdsp


def dump(buf, offs):
    i = 4
    while i < len(buf):
        op = unpack('<I', d[i-4:i])[0]
        print("0b%032s" % bin(op)[2:])
        i += 4

if __name__ == '__main__':
    d = data[2]
    #dump(d, 0)
    decoder = vsdsp.Decoder(d)
    asms = decoder.decode()
    for asm in asms:
        print(str(asm))

