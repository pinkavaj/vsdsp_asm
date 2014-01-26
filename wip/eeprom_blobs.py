#!/usr/bin/python3

import argparse
import json
from struct import pack, unpack
import sys


class Block(object):
    """Base class for EEPROM block with fixed size and offset."""
    # must be set in child class
    size = None
    name = None
    offs = None

    """Top building block of firmware blob."""
    def __init__(self, data):
        super().__init__()
        if isinstance(data, bytes):
            self.data = data[self.offs:self.offs+self.size]
            self._decode()
            return
        self.text = data
        self._encode()

    def __le__(self, other):
        return self.offs < other.offs

    def __repr__(self):
        text = self.text
        if hasattr(text, '__iter__'):
            t = ''
            for i in text:
                t += '            %s\n' % str(i)
            text = '[\n' + t + '        ]'
        return '{ "offs": 0x%04x, "name": "%s",\n        "text": %s,\n    },' % \
                    (self.offs, self.name, text )

    def _decode(self):
        raise NotImplementedError('Override with block specific routine')

    def _encode(self):
        raise NotImplementedError('Override with block specific routine')

    def blob(self):
        raise NotImplementedError('Override with block specific routine')


class Block1(Block):
    """Binary patch blob. Contains moustly firmware and possibly data."""
    name = "binary patch"
    offs = 0
    size = 0x800

    class Firmware(object):
        def __init__(self, blob, offs):
            super().__init__()
            self._type, nbytes, addr = unpack('<BHH', blob[offs:offs+5])
            self.addr = addr
            self.data = blob[offs+5:offs+5+nbytes]
            if self._type == 1:
                self.name = "firmware"
                self.size = nbytes + 5
            elif self._type == 3:
                self.name = "exec"
                self.size = Block1.size - offs
                if sum(blob[offs+5:Block1.size]) != 0 or nbytes != 0:
                    raise NotImplementedError(
                            'Nonzero padding or %d != 0  or %d != 0' % \
                                    (nbytes, addr, ))
            else:
                raise NotImplementedError('type %d' % self._type)

        def __getitem__(self, idx):
            return getattr(self, idx)

        def __repr__(self):
            return '{ "name": "%s", "addr": 0x%04x, "data": %s, },' % \
                    (self.name, self.addr, self.data, )

        def blob(self, offs):
            blob = pack('<BHH', self._type, len(self.data), self.addr) + self.data
            if self._type == 3:
                n = Block1.size - offs - 5 - len(self.data)
                blob += b'\x00' * n
            return blob

    def __iter__(self):
        return self.text.__iter__()

    def _decode(self):
        idx = 0
        self.text = []
        while True:
            text = Block1.Firmware(self.data, idx)
            idx += text.size
            self.text.append(text)
            if text._type == 3:
                self.size = idx
                self.data = self.data[0:idx]
                break

    def blob(self):
        data = b''
        for d in self.text:
            data += d.blob(len(data))
        return data


class Block2(Block):
    """TODO: decode other blocks."""
    name = "TODO"
    offs = 0x800
    size = 32*1024 - offs

    def _decode(self):
        self.text = 'TODO'

    def blob(self):
        return self.data


class Eeprom(object):
    block_codecs = (
            Block1,
            Block2,
            )

    def __init__(self, **argv):
        super().__init__()
        if len(argv) != 1:
            raise ValueError('expected block list or block list :)')
        self.blocks = argv['blocks']

    def __iter__(self):
        return self.blocks.__iter__()

    def __getitem__(self, idx):
        return self.blocks[idx]

    def __repr__(self):
        s = '[\n'
        for block in self.blocks:
            s += '    %s\n' % block
        s += ']\n'
        return s

    def blob(self):
        """Return serialized EEPROM data."""
        blob = b''
        for block in self.blocks:
            blob += block.blob()
        return blob

    @staticmethod
    def decode(blob):
        """Convert binary EEPROM BLOB into readable form."""
        return Eeprom(blocks=[b(blob) for b in Eeprom.block_codecs])

    @staticmethod
    def encode(text):
        """Create Eeprom content from JSON EEPROM dump format."""
        if len(text) != len(Eeprom.block_codecs):
            raise ValueError('%d != %d' % (len(text), len(Eeprom.block_codecs), ))
        return Eeprom(blocks=[Eeprom.block_codecs[i](text[i]) for i in range(0, len(text))])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            description='Decode/encode Vaisala radiosondes EEPROM content.')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-d', '--decode', action='store_true')
    group.add_argument('-e', '--encode', action='store_false')
    parser.add_argument('--test', action='store_true')
    parser.add_argument('-o', '--output', metavar='FILE', default='-',
                               help='Output file name, use - for stdout.')
    parser.add_argument('input', nargs='?',  default='-', help='input file name')
    args = parser.parse_args()

    if args.decode:
        ifile = sys.stdin if args.input == '-' else open(args.input, 'rb')
        eeprom = Eeprom.decode(ifile.read())
        if args.test:
            mode = 'wb'
            data = eeprom.blob()
        else:
            mode = 'w'
            data = str(eeprom)
    else:
        ifile = sys.stdin if args.input == '-' else open(args.input, 'r')
        eeprom = Eeprom.encode(text)
        mode = 'wb'
        data = eeprom.blob()

    ofile = sys.stdout if args.output == '-' else open(args.output, mode)
    ofile.write(data)
    ofile.close()

