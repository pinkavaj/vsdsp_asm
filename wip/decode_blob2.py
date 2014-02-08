#!/usr/bin/python3

from struct import unpack


data_file='data/eeprom/F0220541.bin'

exp_result1 = (
        0x00, 0x63, 0x00, 0x6f,  0x00, 0x6e, 0x00, 0x74,
        0x00, 0x72, 0x00, 0x6f,  0x00, 0x6c, 0x00, 0x00,
        0x02, 0x26, 0x02, 0x41,  0x02, 0x3c, )

exp_result2 = (
        0x00, 0x24 ,0x36 ,0x13,  0xb8 ,0x17 ,0x3e ,0x12,
        0x38 ,0x15 ,0x3e ,0x12,  0xb8 ,0x14 ,0x3e ,0x05, )


class BitStream(object):
    def __init__(self, data):
        self.data = data
        self.idx = 0
        self.mask = 1

    def getBits(self, n, value=0):
        """Shift valule n bites left and append bites from input."""
        while n:
            value = value << 1;
            if self.mask & self.data[self.idx]:
                value += 1
            self.mask = self.mask << 1
            if self.mask >= 0x100:
                self.mask = 1
                self.idx += 1
            n -= 1
        return value

    def getPrefix(self, n=0):
        """Count amount of consecutive 1 => N, then return n+N following bites."""
        while n < 7:
            val = self.mask & self.data[self.idx]
            self.mask = self.mask << 1
            if self.mask >= 0x100:
                self.mask = 1
                self.idx += 1
            if not val:
                break
            n += 1
        return self.getBits(value=1, n=n)

    def getRawBytes(self, n=1):
        if self.mask != 1:
            raise IndexError("unaligned idx %d mask 0x%02x" % (self.idx, self.mask, ))
        res = self.data[self.idx:self.idx+n]
        self.idx += n
        return res


def decode(data):
    rams = { 'X': {}, 'Y': {}, }
    rams_idx = { 0: 'X', 0x8000: 'Y' }
    bitStream = BitStream(data)
    print(' '.join(["%02x" % x for x in data[31:45]]))
    while True:
        prefix_val = bitStream.getRawBytes()[0]
        print("prefix_val 0x%02x" % prefix_val)
        addr = unpack('<H', bitStream.getRawBytes(2))[0]
        prefix_len = bitStream.getRawBytes()[0]
        print("prefix_len 0x%02x" % prefix_len)
        ram_ = rams[rams_idx[addr & 0x8000]]
        ram = ram_[addr] = []
        if prefix_len == 0xff:
            rams['start'] = addr
            print("start")
            return rams
        while True:
            val = bitStream.getBits(prefix_len)
            print("val = 0x%x" % val)
            if val == prefix_val:
                size = bitStream.getPrefix()
                print("size: %d" % size)
                if size == 1:
                    t = bitStream.getBits(n=1)
                    if t != 0:
                        t = bitStream.getBits(n=prefix_len)
                        prefix_val, t = t, prefix_val
                        t = bitStream.getBits(n=8-prefix_len, value= t)
                        ram.append(t)
                        continue
                    wtf2 = 1
                else:
                    wtf2 = bitStream.getPrefix()
                print("wtf2: %s" % wtf2)
                if wtf2 == 0xff:
                    print("bitStream.idx %d " % bitStream.idx)
                    print("bitStream.mask 0x%x " % bitStream.mask)
                    print("bitStream.data[] 0x%x " % bitStream.data[bitStream.idx])
                    val = 0
                    k = 0
                    while bitStream.mask != 1:
                        val = bitStream.getBits(n=1, value=val)
                        k = k * 2 + 1
                    k = k & 0xfffe
                    if val != k:
                        print("fixme 1 0x%02x" % val)
                        return rams
                    break
                offs = bitStream.getBits(value=wtf2-1, n=8) + 1
                print("offs: %s" % offs)
                size += 1
                while size:
                    size -= 1
                    ram.append(ram[-offs])
                continue
            else:
                ram.append(bitStream.getBits(value=val, n=8-prefix_len))
    print("WTF")
    return rams


if __name__ == '__main__':
    data = open(data_file, 'rb').read()
    data = data[0x802:]
    rams = decode(data)
    for k in rams:
        print("%s: " % k)
        for d in rams[k]:
            print("    %s:" % d)
            x = ["%02x" % y for y in rams[k][d]]
            idx = 0
            while idx < len(x):
                print("%s " % x[idx], end='')
                idx += 1
                if idx % 4 == 0:
                    print(" ", end='')
                if idx % 16 == 0:
                    print()
            print()
