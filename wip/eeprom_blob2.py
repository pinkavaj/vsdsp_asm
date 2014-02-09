#!/usr/bin/python3

from struct import unpack


class BitStream(object):
    def __init__(self, data, offs=0):
        self.data = data
        self.idx = offs
        self.mask = 1

    def getBits(self, size, value=0):
        """Transfer 'size' bytes from input strem to 'value'."""
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

    def getPrefix(self):
        """Returns value defined by prefix of consecutive 1s."""
        size = 0
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
        """Get raw byte from input bite stream."""
        if self.mask != 1:
            raise IndexError("unaligned mask 0x%02x for idx 0x%0x" % (self.mask, self.idx, ))
        res = self.data[self.idx:self.idx+size]
        self.idx += size
        return res


def decompress(data, offs=0, ram_size = 2**17):
# RAMs are acessed by byte for decompression, not by word -> 2* 65kW = 128kB
    ram_x = ['.', ] * ram_size # I-RAM is usually mapped here
    ram_y = ['.', ] * ram_size
    rams = { 0: ram_x, 0x8000: ram_y, }
    bitStream = BitStream(data, offs)
    while True:
        prefix_val, addr, prefix_len = unpack('<BHB', bitStream.getRawBytes(4))
        addr, bus = addr & 0x7fff, addr & 0x8000
        if prefix_len == 0xff:
            rams[-1] = addr
            rams[1] = rams[0x8000]
            rams.pop(0x8000)
            return (rams, bitStream.idx, )
        ram = rams[bus]
        while True:
            val = bitStream.getBits(prefix_len)
            if val == prefix_val:
                size = bitStream.getPrefix()
                if size == 1:
                    val = bitStream.getBits(size=1)
                    if val != 0:
                        val = bitStream.getBits(size=prefix_len)
                        prefix_val, val = val, prefix_val
                        val = bitStream.getBits(size=8-prefix_len, value=val)
                        ram[addr] = val
                        addr += 1
                        continue
                    val = 1
                else:
                    val = bitStream.getPrefix()
                    if val == 0xff:
                        if bitStream.mask != 1:
                            bitStream.mask = 1
                            bitStream.idx += 1
                        break
                offs = bitStream.getBits(value=val-1, size=8) + 1
                size += 1
                while size:
                    size -= 1
                    ram[addr] = ram[addr-offs]
                    addr += 1
                continue
            else:
                ram[addr] = bitStream.getBits(value=val, size=8-prefix_len)
                addr += 1


def strip(blob2):
    """Remove unused bytes from decompressed blob2 memory image.
    returns dict with chunks { addr: blob, ...}"""
    chunks = {}
    idx = 0
    while idx < len(blob2):
        while idx < len(blob2) and blob2[idx] == '.':
            idx += 1
        if idx == len(blob2):
            break
        chunk = []
        chunks[idx] = chunk
        while idx < len(blob2) and blob2[idx] != '.':
            chunk.append(blob2[idx])
            idx += 1
    for addr in chunks:
        chunks[addr] = bytes(chunks[addr])
    return chunks


if __name__ == '__main__':
    import sys

    if len(sys.argv) != 2:
        print("%s <EEPROM IMAGE FILE>" % sys.argv[0])
        sys.exit(1)
    file_name = sys.argv[1]
    data = open(file_name, 'rb').read()
    rams, eof_offs = decompress(data, 0x802)
    print('end offset: %d [0x%04x]' % (eof_offs, eof_offs, ))
    for bus in rams:
        ram = rams[bus]
        if bus == -1:
            print("start: 0x%04x" % ram)
            print()
            continue
        bus = { 0: 'X', 1: 'Y' }[bus]
        ram = strip(ram)
        for addr in ram:
            print('%s: 0x%04x [0x%04x]' % (bus, addr, addr // 2, ))
            chunk = ["%02x " % x for x in ram[addr]]
            idx = 0
            s = ''
            while idx < len(chunk):
                s += chunk[idx]
                idx_ = idx + 1
                if idx_ % 4 == 0:
                    s += ' '
                if idx_ % 16 == 0:
                    print(s.strip())
                    s = ''
                idx = idx_
            if s:
                print(s)
            print()

