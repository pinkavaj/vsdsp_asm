
.sect code, main
.org 0x1f6c

LDC     0x200, MR0
LDC     0x10, I6
LDC     0xffa4, I2
LDC     0x0, A0
STX     A0, (I2)
J init
NOP

read_eeprom:
// read EEPROM routine
LDX     (I6)+1, NULL
STX     I7, (I6)+1;       STY B1, (I6)
STX     LR0, (I6)+1;      STY I7, (I6)
CALL    0x20f9
SUB     NULL, ONES, D0;   STX D1, (I6);   STY B0, (I6)
AND     NULL, NULL, D0;   MVX B1, A0
LDX     (I6)-1, D1;       LDY (I6), B0
LDX     (I6)-1, LR0;      LDY (I6), I7
JR
LDX     (I6)-1, I7;       LDY (I6), B1

init:
LDC 0xffff, I7

dump_loop:

LDC 0xbeef, I2
CALL read_eeprom
NOP

MV I7, I2
CALL read_eeprom
NOP

LDX (I7), D1
MV D1, I2
CALL read_eeprom
NOP

LDC 0x0, D0
STX D0, (I7)
NOP
NOP
LDX (I7), C0
NOP
NOP
MV C0, I2
CALL read_eeprom
NOP

LDC 0xffff, D0
STX D0, (I7)
NOP
NOP
LDX (I7), I2
NOP
NOP
CALL read_eeprom
NOP

STX D1, (I7)-1
NOP

LDC 0xfe00, A0
MV I7, A1
SUB A0, A1, A1
NOP
JZC dump_loop
NOP

end:
NOP
J end
NOP

.end
