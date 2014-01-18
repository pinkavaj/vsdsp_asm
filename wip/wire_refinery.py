#!/usr/bin/python3
"""Convert raw bite lines status log into RAM/ROM dump."""

import sys


def event_filter(infile, outfile):
    if isinstance(infile, str):
        infile = open(infile, 'rb')
    if isinstance(outfile, str):
        outfile = open(outfile, 'wb')
    last_b = infile.read(1)
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

if __name__ == '__main__':
    cmd = sys.argv[1]
    infile = sys.argv[2]
    if cmd == 'events':
        outfile = infile + '.events'
        event_filter(infile, outfile)
    elif cmd == 'spi':
        spi = SPIDecoder()
        outfile = infile + '.spi'
        wires = Lines(cs=0, mosi=1, clk=2, miso=3)
        spi.decode(infile, outfile, wires)
    else:
        raise NotImplementedError('cmd %s' % cmd)

