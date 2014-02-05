
EEPROM_FILE=data/eeprom/F0220541.bin
ASM_FILE=src/boot_0001_search_io_ports.s
OBJ_FILE=$(ASM_FILE:%.s=%.o)
ASM_BIN=wine /home/pinky/.wine/drive_c/Program\ Files\ \(x86\)/VSIDE/bin/vsa.exe
MKEEPROM_BIN=python wip/objtool.py

all: 0001


0001:
	$(ASM_BIN) $(ASM_FILE)
	$(MKEEPROM_BIN) $(OBJ_FILE) $(EEPROM_FILE)
	python2 ../meteosonda/tools/buspirate_eeprom_rw.py write $(EEPROM_FILE).patched.bin $$((0x130)) 256
