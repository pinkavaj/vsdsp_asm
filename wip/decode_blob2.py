#!/usr/bin/python3

from struct import unpack


data_file='data/eeprom/F0220541.bin'


class BitStream(object):
    def __init__(self, data, offs=0):
        self.data = data
        self.idx = offs
        self.mask = 1

    def getBits(self, size, value=0):
        """Shift valule size bites left and append bites from input."""
        while size:
            value = value << 1;
            if self.mask & self.data[self.idx]:
                value += 1
            self.mask = self.mask << 1
            if self.mask >= 0x100:
                self.mask = 1
                self.idx += 1
            size -= 1
        return value

    def getPrefix(self, size=0):
        """Count amount of consecutive 1 => N, then return size+N following bites."""
        while size < 7:
            val = self.mask & self.data[self.idx]
            self.mask = self.mask << 1
            if self.mask >= 0x100:
                self.mask = 1
                self.idx += 1
            if not val:
                break
            size += 1
        return self.getBits(value=1, size=size)

    def getRawBytes(self, size=1):
        if self.mask != 1:
            raise IndexError("unaligned idx %d mask 0x%02x" % (self.idx, self.mask, ))
        res = self.data[self.idx:self.idx+size]
        self.idx += size
        return res


def decode(data, offs=0):
    rams = { 'X': {}, 'Y': {}, }
    buses = { 0: 'X', 0x8000: 'Y' }
    bitStream = BitStream(data, offs)
    print(' '.join(["%02x" % x for x in data[31:45]]))
    while True:
        prefix_val = bitStream.getRawBytes()[0]
        print("prefix_val 0x%02x" % prefix_val)
        addr = unpack('<H', bitStream.getRawBytes(2))[0]
        prefix_len = bitStream.getRawBytes()[0]
        print("prefix_len 0x%02x" % prefix_len)
        addr, bus = addr & 0x7fff, addr & 0x8000
        ram_ = rams[buses[bus]]
        ram = ram_[addr] = []
        if prefix_len == 0xff:
            rams['start'] = { 0: (addr, ) }
            print("start")
            return rams
        while True:
            val = bitStream.getBits(prefix_len)
            print("val = 0x%x" % val)
            if val == prefix_val:
                size = bitStream.getPrefix()
                print("size: %d" % size)
                if size == 1:
                    t = bitStream.getBits(size=1)
                    if t != 0:
                        t = bitStream.getBits(size=prefix_len)
                        prefix_val, t = t, prefix_val
                        t = bitStream.getBits(size=8-prefix_len, value= t)
                        ram.append(t)
                        continue
                    wtf2 = 1
                else:
                    wtf2 = bitStream.getPrefix()
                print("wtf2: %s" % wtf2)
                if wtf2 == 0xff:
                    print("bitStream.idx %d (0x%x) " % (bitStream.idx, bitStream.idx, ))
                    print("bitStream.mask 0x%x " % bitStream.mask)
                    print("bitStream.data[] 0x%x " % bitStream.data[bitStream.idx])
                    val = 0
                    k = 0
                    while bitStream.mask != 1:
                        val = bitStream.getBits(size=1, value=val)
                        k = k * 2 + 1
                    k = k & 0xfffe
                    if val != k:
                        print("fixme 1 val = 0x%02x, k = 0x%02x" % (val, k, ))
                    break
                offs = bitStream.getBits(value=wtf2-1, size=8) + 1
                print("offs: %s" % offs)
                size += 1
                while size:
                    size -= 1
                    ram.append(ram[-offs])
                continue
            else:
                ram.append(bitStream.getBits(value=val, size=8-prefix_len))
    print("WTF")
    return rams


if __name__ == '__main__':
    data = open(data_file, 'rb').read()
    rams = decode(data, 0x802)
    for k in rams:
        print("%s: " % k)
        for d in rams[k]:
            print("    0x%02x:" % d)
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
