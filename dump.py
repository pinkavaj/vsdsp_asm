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
    data = data[5]
    d = []

    i = 0
    while i < len(data):
        d.append(data[i+0])
        d.append(data[i+1])
        d.append(data[i+2])
        d.append(data[i+3])
        i += 4
    #dump(d, 0)
    d = bytes(d)
    decoder = vsdsp.Decoder(d)
    asms = decoder.decode()
    print("data len: %d" % len(d))
    for asm in asms:
        print('%s #\t\top: 0x%08x' % (str(asm), asm.opcode, ))

