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


class Blob2Codec(dict):
    bus_names = { -1: '"start"', 0: '"X"', 1: '"Y"' }

    def __init__(self, blob=None, rams=None, offs=0, ram_size = 2**17):
        if (blob is None and rams is None) or \
                (blob is not None and rams is not None):
            raise KeyError("Require one of: blob, rams")
        if rams:
            raise NotImplementedError()

        self._decompress(blob, offs, ram_size)
        for bus in self:
            if bus == -1:
                continue
            self[bus] = self._strip(bus)

    def __repr__(self):
        s = ''
        for bus in self:
            ram = self[bus]
            if bus == -1:
                ram_s = ' 0x%04x' % ram
            else:
                ram_s = ' {\n'
                for addr in ram:
                    chunk = ["0x%02x," % x for x in ram[addr]]
                    idx = 0
                    chunk_s = '        0x%04x: [' % addr
                    while idx < len(chunk):
                        if idx % 16 == 0:
                            chunk_s = '%s\n            ' % chunk_s
                        if idx % 4 == 0:
                            chunk_s += ' '
                        chunk_s += chunk[idx]
                        idx += 1
                    ram_s += '%s\n        ],\n' % (chunk_s, )
                ram_s += '\n    }'
            s = '%s\n    %s: %s,\n' % (s, Blob2Codec.bus_names[bus], ram_s, )
        return '{\n%s\n},' %s

    def compress(self):
        raise NotImplementedError()

    def _decompress(self, data, offs=0, ram_size = 2**17):
        # RAMs are acessed by byte for decompression, not by word -> 2* 65kW = 128kB
        ram_x = ['.', ] * ram_size # I-RAM is usually mapped here
        ram_y = ['.', ] * ram_size
        self[0] = ram_x
        self[0x8000] = ram_y
        bitStream = BitStream(data, offs)
        while True:
            prefix_val, addr, prefix_len = unpack('<BHB', bitStream.getRawBytes(4))
            addr, bus = addr & 0x7fff, addr & 0x8000
            if prefix_len == 0xff:
                self[-1] = addr
                self[1] = self.pop(0x8000)
                self.eof_offs = bitStream.idx
                return
            ram = self[bus]
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

    def _strip(self, bus):
        """Remove unused bytes from decompressed blob2 memory image.
        returns dict with chunks { addr: blob, ...}"""
        chunks = {}
        idx = 0
        ram = self[bus]
        while idx < len(self[bus]):
            while idx < len(ram) and ram[idx] == '.':
                idx += 1
            if idx == len(ram):
                break
            chunk = []
            chunks[idx] = chunk
            while idx < len(ram) and ram[idx] != '.':
                chunk.append(ram[idx])
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
    rams = Blob2Codec(blob=data, offs=0x802)
    print('end_offset: %d [0x%04x]' % (rams.eof_offs, rams.eof_offs, ))
    print(repr(rams))

