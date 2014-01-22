.org 0x0

goto 0x10000    // WTF? reset????


.org 0x1000

I2 = 0x7FF
A0 = Y[I2]
if (A0 == 0x1) goto _0x1019
if (A0 == 0x2) goto _0x1013
I0 = 0xffc0
A1 = X[I0]
A0 = A1 & 0x2000
if (A0 == 0) goto _0x1019

_0x1013:
A0 = 0
Y[I2] = A0
I0 = 0x800
I1 = 0x802
goto _0x1f6c

_0x1019:
A0 = 0
Y[I2] = A0
I0 = 0x5000
I1 = 0x5002
goto _0x1f6c


.org 0x1f6c

_0x1f6c:
MR0 = 0x200
I6 = 0x10
I2 = 0xffa4
A0 = 0
X[I2] = A0
I2 = I1
goto _0x1fc4

_0x1f73:
I6++
X[I6++] = I3, Y[I6] = B1
X[I6++] = LR0, Y[I6] = I7
D0 = 1, X[I6] = D1, Y[I6] = B0
_0x20f9(__I7__ addr, __D0__ ???)
DO=0, A0 = B1
D1 = X[I6--], BO = Y[I6]
LR0 = X[I6--], I7 = Y[I6]
I3 = X[I6--], B1 = Y[I6]
JR


_0x1fc4:
_0x1f73()
C1 = A0
_0x1f73()
C0 = A0
_0x1f73()
A1 = 0x100
P = A1 * A0 // UU
A = P
A0 += C0
A0 *= 2
I4 = 0x21d9
I5 = 0x21d6
if (CC) goto _0x1fd4
I4 = 0x22af
I5 = 0x22ac

_0x1fd4:
A0 >>= 1
I3 = A0
_0x1f73()
A1 = 0xff
A0 &= A1
A1 = A0 - A1
LR0 = I3
D0 = 0
if (ZS) JR

_0x1fdd:
A0 = 0, A1 = C0
_0x1fac()
A1 = C1 - A0
A1 = 0x8
if (ZC) goto _0x1ffc
_0x1f9b()
A0 -= 1, B0 = A0
B1 = 0
if (ZC) goto _0x1fbd
A0 = 0
A1 = 1
_0x1fac()
if (ZC) goto _0x1ff8

_0x1fed:
A0 = B1
A1 = 0x8
_0x1fac()
A0 -= 1, B1 = I3
A0 = B1 - A0
I1 = A0
LC = B0
while(LC) {
A0 = I1
_0x1f7d()
I++
}
goto _0x1fdd

_0x1ff8:
A0 = 0, A1 = C0
_0x1fac()
A0 = C1, C1 = A0
A1 = 0x8
_0x1fac()

_0x1ffc:
A1 = A1 - C0
_0x1fac()
LR0 = 0x1fdd
goto _0x1f89

_0x1ffd:
A1 = A1 - C0
LR0 = 0x1fdd
goto _0x1f89

