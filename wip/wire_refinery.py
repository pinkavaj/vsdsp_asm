#!/usr/bin/python3
"""Convert raw bite lines status log into RAM/ROM dump."""

import sys


def event_filter(infile, outfile, op=None):
    """Filter out repetitive sequences of samples.
    Optionally do sample = sample & op."""
    if isinstance(infile, str):
        infile = open(infile, 'rb')
    if isinstance(outfile, str):
        outfile = open(outfile, 'wb')
    if op is None:
        op = 0xff
    else:
        if op[0] == '~':
            op = ~int(op[1:], 0)
        else:
            op = int(op, 0)
    last_b = bytes((infile.read(1)[0] & op, ))
    outfile.write(last_b)
    b = last_b
    while b:
        if b != last_b:
            outfile.write(b)
            last_b = b
        b = infile.read(1)


class Lines:
    """Assign names to hardware wires, create bit mask."""
    def __init__(self, **kwarg):
        for k in kwarg:
            setattr(self, k + '_mask', (1 << kwarg[k]))
            setattr(self, k + '_bit', kwarg[k])


class SPIDecoder(object):
    MSB_FIRST = 0
    LSB_FIRST = 1

    def __init__(self, cpol=0, cpha=0, bit_order=MSB_FIRST, cs_active=0, debug=False):
        self.cpol = bool(cpol)
        self.cpha = bool(cpha)
        self.bit_order = bit_order
        self.cs_active = bool(cs_active)
        self._debug = debug

    def decode(self, infile, outfile, wires):
        if isinstance(infile, str):
            infile = open(infile, 'rb')
        if isinstance(outfile, str):
            outfile = open(outfile, 'w')

        clk_data_stable = (self.cpol == self.cpha)
#  drop possibly incomplete transaction
        b = self._read(infile)
        cnt = 0
        while b is not None and bool(b & wires.cs_mask) is self.cs_active:
            cnt += 1
            b = self._read(infile)
        if cnt:
            self._print('Dropped %d samples' % cnt)

        clk_prev = self.cpol
        while b is not None:
# drop all until CS
            cnt = 0
            while b is not None and bool(b & wires.cs_mask) is not self.cs_active:
                clk_prev = b & wires.clk_mask
                b = self._read(infile)
                cnt += 1
            self._print("no CS for %d samples" % cnt)
# get all data while CS
            cnt = 0
            data = []
            clk_prev = bool(clk_prev)
            while b is not None and bool(b & wires.cs_mask) is self.cs_active:
                clk = bool(b & wires.clk_mask)
                if clk is not clk_prev and clk is clk_data_stable:
                    data.append(b & (wires.miso_mask | wires.mosi_mask))
                clk_prev = clk
                b = self._read(infile)
                cnt += 1
            self._print("CS for %d samples" % cnt)
# convert transaction bites to bytes
            miso_bytes = []
            mosi_bytes = []
            miso_b = 0
            mosi_b = 0
            n = 0
            for d in data:
                if self.bit_order == self.MSB_FIRST:
                    shift = 7 - n
                else:
                    shift = n
                if d & wires.miso_mask:
                    miso_b |= (1 << shift)
                if d & wires.mosi_mask:
                    mosi_b |= (1 << shift)
                n += 1
                if n < 8:
                    continue
                miso_bytes.append(miso_b)
                mosi_bytes.append(mosi_b)
                miso_b = 0
                mosi_b = 0
                n = 0
# write data to output
            miso_bytes = ["%02x" % d for d in miso_bytes]
            mosi_bytes = ["%02x" % d for d in mosi_bytes]

            miso_bytes = ':'.join(miso_bytes)
            mosi_bytes = ':'.join(mosi_bytes)

            outfile.write(mosi_bytes + " " + miso_bytes + "\n")

    def _print(self, *argv, **kwarg):
        if self._debug:
            print(*argv, **kwarg)

    def _read(self, f):
        d = f.read(1)
        if not d:
            return None
        return d[0]


def mem_dump_hack(infile, outfile):
    """Extract memory dump send out trough EEPROM address bytes."""
    if isinstance(infile, str):
        infile = open(infile, 'r')
    if isinstance(outfile, str):
        outfile = open(outfile, 'wb')
    stop_word = '03:08:02:00'
    for line in infile:
        mosi, miso = line.split(' ')
        if mosi == stop_word:
            break
    for line in infile:
        if not line.strip():
            break
        mosi, miso = line.split(' ')
        data = mosi[3:3+5].split(':')
        data = (int(data[1], 16), int(data[0], 16), )
        outfile.write(bytes(data))

def iram_dump_hack(infile, outfile):
    """Extract I-ram send trought EEPROM address bytes."""
    if isinstance(infile, str):
        infile = open(infile, 'r')
    if isinstance(outfile, str):
        outfile = open(outfile, 'wb')
    stop_word = '03:03:72:00:00:00:00:00'
    for line in infile:
        mosi, miso = line.split(' ')
        if mosi == stop_word:
            break
    infile.readline()
    line = infile.readline()
    while line:
        line = infile.readline()
        infile.readline()
        line2 = infile.readline()
        infile.readline()
        if not line2.strip():
            break
        mosi, miso = line.split(' ')
        data1 = mosi[3:3+5].split(':')
        mosi, miso = line2.split(' ')
        data2 = mosi[3:3+5].split(':')
        data = (data1[1], data1[0], data2[1], data2[0], )
        print(''.join(data))
        data = [int(d, 16) for d in data]
        data = bytes(data)
        outfile.write(bytes(data))


if __name__ == '__main__':
    if len(sys.argv) == 1:
        print('[ events | spi | mem_dump_hack | iram_dump_hack ] <INPUT FILE>')
        sys.exit(1)
    cmd = sys.argv[1]
    infile = sys.argv[2]
    if cmd == 'events':
        outfile = infile + '.events'
        op = None
        if len(sys.argv) == 4:
            op = sys.argv[3]
        event_filter(infile, outfile, op)
    elif cmd == 'spi':
        spi = SPIDecoder()
        outfile = infile + '.spi'
        wires = Lines(cs=0, mosi=1, clk=2, miso=3)
        #wires = Lines(cs=5, mosi=3, clk=4, miso=2)
        spi.decode(infile, outfile, wires)
    elif cmd == 'mem_dump_hack':
        outfile = infile + '.mem_dump'
        mem_dump_hack(infile, outfile)
    elif cmd == 'iram_dump_hack':
        outfile = infile + '.iram_dump'
        iram_dump_hack(infile, outfile)
    else:
        raise NotImplementedError('cmd "%s"' % cmd)

