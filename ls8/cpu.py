"""CPU functionality."""

import sys

HLT = 0b00000001
LDI = 0b10000010
PRN = 0b01000111
MUL = 0b10100010
ADD = 0b10100000
POP = 0b01000110
PUSH = 0b01000101
CALL = 0b01010000
RET = 0b00010001
CMP = 0b10100111
JMP = 0b01010100
JEQ = 0b01010101
JNE = 0b01010110



stack_pointer = 7

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.reg = [0] * 8
        self.pc = 0
        self.ram = [0] * 256
        self.fl = 0
        self.branchtable = {}
        self.branchtable[HLT] = self.hlt
        self.branchtable[LDI] = self.ldi
        self.branchtable[PRN] = self.prn
        self.branchtable[MUL] = self.mul
        self.branchtable[ADD] = self.add
        self.branchtable[POP] = self.pop
        self.branchtable[PUSH] = self.push
        self.branchtable[CALL] = self.call
        self.branchtable[RET] = self.ret
        self.branchtable[CMP] = self.cmp
        self.branchtable[JMP] = self.jmp
        self.branchtable[JEQ] = self.jeq
        self.branchtable[JNE] = self.jne 


        self.reg[stack_pointer] = 0xf4

        self.halted = False

    def load(self):
        """Load a program into memory."""

        if len(sys.argv) != 2:
            print("usage: comp.py [filename]")
            sys.exit(1)

        progname = sys.argv[1]

        address = 0

        # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010, # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111, # PRN R0
        #     0b00000000,
        #     0b00000001, # HLT
        # ]

        # for instruction in program:
        #     self.ram[address] = instruction
        #     address += 1

        with open(progname) as f:
            for line in f:
                line = line.split("#")[0]
                line = line.strip()

                if line == "":
                    continue

                val = int(line, 2)

                self.ram[address] = val
                address += 1


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]

        elif op == "CMP":
            if self.reg[reg_a] > self.reg[reg_b]:
                self.fl = 0b00000010
            if self.reg[reg_a] < self.reg[reg_b]:
                self.fl = 0b00000100
            if self.reg[reg_a] == self.reg[reg_b]:
                self.fl = 0b00000001

        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def ram_read(self, mar):
        return self.ram[mar]
    
    def ram_write(self, mdr, mar):
        self.ram[mar] = mdr
    
    def ldi(self):
        reg_num = self.ram_read(self.pc + 1)
        value = self.ram_read(self.pc + 2)

        self.reg[reg_num] = value

    def prn(self):
        reg_num = self.ram_read(self.pc + 1)
        print(self.reg[reg_num])

    def mul(self):
        num1 = self.ram_read(self.pc + 1)
        num2 = self.ram_read(self.pc + 2)
        
        self.alu("MUL", num1, num2)

    def add(self):
        num1 = self.ram_read(self.pc + 1)
        num2 = self.ram_read(self.pc + 2)
        
        self.alu("ADD", num1, num2)

    def hlt(self):
        self.halted = True

    def pop(self):
        value = self.ram[self.reg[stack_pointer]]
        reg_num = self.ram_read(self.pc + 1)
        self.reg[reg_num] = value
        self.reg[stack_pointer] += 1

    def push(self):
        self.reg[stack_pointer] -= 1
        reg_num = self.ram_read(self.pc + 1)
        value = self.reg[reg_num]
        self.ram[self.reg[stack_pointer]] = value

    def call(self):
        ret_address = self.pc + 2
        self.reg[stack_pointer] -= 1
        self.ram[self.reg[stack_pointer]] = ret_address

        reg_num = self.ram_read(self.pc + 1)
        self.pc = self.reg[reg_num]

    def ret(self):
        self.pc = self.ram[self.reg[stack_pointer]]
        self.reg[stack_pointer] += 1

    def cmp(self):
        num1 = self.ram_read(self.pc + 1)
        num2 = self.ram_read(self.pc + 2)
        self.alu("CMP", num1, num2)

    def jmp(self):
        reg_num = self.ram_read(self.pc + 1)
        self.pc = self.reg[reg_num]

    def jeq(self):
        reg_num = self.ram_read(self.pc + 1)

        if self.fl == 0b00000001:
            self.pc = self.reg[reg_num]
        else:
            self.pc += 2

    def jne(self):
        reg_num = self.ram_read(self.pc + 1)
        
        if self.fl != 0b00000001:
            self.pc = self.reg[reg_num]
        else:
            self.pc += 2

    def run(self):
        """Run the CPU."""
        # halted = False

        # while not halted:
        #     instruction = self.ram[self.pc]

        #     if instruction == 0b10000010:
        #         reg_num = self.ram_read(self.pc + 1)
        #         value = self.ram_read(self.pc + 2)

        #         self.reg[reg_num] = value

        #         self.pc += 3

        #     elif instruction == 0b01000111:
        #         reg_num = self.ram_read(self.pc + 1)
        #         print(self.reg[reg_num])

        #         self.pc += 2

        #     elif instruction == 0b00000001:
        #         halted = True

        #         self.pc += 1

        #     else:
        #         print(f"Unknown instructions at index {self.pc}")
        #         sys.exit(1) 

        while self.halted != True:
            ir = self.ram[self.pc]
            op_count = ir >> 6
            ir_length = op_count + 1
            
            self.branchtable[ir]()

            if ir == 0 or None:
                print(f"wut is goin on {self.pc}")
                sys.exit(1)

            if ir != 80 and ir != 17 and ir != 84 and ir != 85 and ir != 86:
                self.pc += ir_length
