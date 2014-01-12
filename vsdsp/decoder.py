from vsdsp.instruction import Op


class Decoder:
    """Dissassemble instruction(s)."""
    def __init__(self, buf, offs=0):
        """Decode instructions from buffer."""
        self._buf = buf
        self._offs = offs

    def decode(self, n=None):
        asm = []
        if n is None:
            n, r = divmod(len(self._buf), 4)
            if r:
                raise ValueError("Buffer not rounded to multiple of 4.")
        while n > 0:
            op = Op(self._buf[self._offs:self._offs+4])
            self._offs += 4
            n -= 1
            asm.append(op.decode())

        return asm

