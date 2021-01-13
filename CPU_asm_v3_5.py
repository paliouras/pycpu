# OO - pyCPU
# ==========================================================================
# Version 3.5 tkinter 
#   2017 by VP
#           extension of OO model
#           provides classes Assembler, Memory, CPU
#           interface to GUI front-end
#           changes to halt instruction for consistency
# Version 3.0 translated to OO model
#   2010 - 2017 extensive modifications by VP
# Class CPU reuses code from the following:
#           Version 1.0 Beta ( 16-bit operation limits are NOT enforced)
#============================================================================
#   Copyright (c) Stefanos Kaxiras & associates, 2009
#===========================================================================
# Instruction set:
# ==========================================================================
# Single Accumulator (Δ0) Machine, 16-bit words, 4096 word memory
# (12-bit addresses)
# 16 bit instructions :
#     4 bit opcode - 12 bit address or immediate data
#     16 possible instructions 13 are defined; 3 are class projects
# ==========================================================================
# Registers
# D0 // accumulator D0, Δ0
# IP  // Instruction Pointer, Απαριθμητής Προγράμματος
# IR  // Instruction Register, ΚΕ
# IR_Opcode // opcode part of IR, ΚΕ(opcode)
# IR_Address // address part of IR, ΚΕ(διεύθυνση)
# MAR // Memory Address Register, ΚΔΜ
# MDR // Memory Data Register, ΚΑΜ
# ALU_OUT // ALU output operand
# 
# -----------------
# ALU output:
# FLAG_Z // ZERO
# FLAG_N // NEGATIVE
# FLAG_C // CARRY
# FLAG_O // OVERFLOW
# -----------------
# Control signals:
# memory_operation = [read, write] // 
# alu_operation = [add, subtract, ..]
#
# ==========================================================================
#
#
# ==========================================================================
# Instructions:
# 0000 load address // load D0 with data from MEM[address]
# 0001 store address // store D0 to MEM[address]
# 0010 add address // D0 = D0 + MEM[address]
# 0011 sub address // D0 = D0 - MEM[address] two's complement operation
# 0100 loadd data // D0 = immediate data from instruction
# 0101 halt
# 0110 addd data // D0 = D0 + immediate data from instruction
# 0111 subd data // D0 = D0 - immediate data from instruction
# 1000 jmp address // Unconditional jump
# 1001 jmp_N address // jump if last generated ALU result is negative
# 1010 jmp_Z address // jump if zero
# 1011 jmp_O address // jump if Overflow
# 1100 jmp_C address // jump if Carry
# 1101 reserved
# 1110 reserved
# 1111 reserved
# ==========================================================================
# DISPLAY Interface
# PyCPU is connected to a 6-digit, 7-segment display that can 
# (by default) display a single memory location.
# The display interface uses seg7.py by Les Smithson.
# Before the display can be used, it must be switched on ('seg7.switch_on()')
# Use 'seg7.display(memory_location)' to display a memory location.
# This can be done at the beginning and end of a program or inside the main
# CPU loop for a continuous tracing of the memory location.
# Additional digits and/or simultaneous display of multiple memory locations
# requires modifications of the seg7.py source.
# ==========================================================================
# ==========================================================================

#import other modules
from datetime import *

#

class Memory():
    copyM = []
    M = []
    size = 1024
    def __init__(self, M=[]):
        Memory.M = M[:]
        if len(Memory.M)<Memory.size:
            Memory.M = Memory.M + (Memory.size-len(Memory.M))*[0]
        Memory.copyM = Memory.M[:]

    @staticmethod
    def load(M):
        Memory.M = M[:]
        if len(Memory.M)<Memory.size:
            Memory.M = Memory.M + (Memory.size-len(Memory.M))*[0]
        Memory.copyM = Memory.M[:]

    @staticmethod
    def check():
        if -1 in Memory.M:
            print('Uknown instructions')
            exit()
        return

class Assembler:
    '''Derive opcodes from instruction mnemonic and argument'''
    instr = [ 'load',       # 0
          'store',      # 1
          'add',        # 2
          'sub',        # 3
          'loadi',      # 4
          'halt',       # 5
          'addi',       # 6
          'subi',       # 7
          'jmp',        # 8
          'jmp_N',      # 9
          'jmp_Z',      # 10
          'jmp_O',      # 11
          'jmp_C',      # 12
          'reserved1',  # 13
          'reserved2',  # 14 
          'reserved3'   # 15
          ]
    def __init__(self):
        pass
    def asm (self, mnemonic, argument=0):
        try:
            word = (Assembler.instr.index(mnemonic) << 12) + ( argument & 0xFFF )
        except:
            word = -1
        return word
    
class Register():
    def __init__(self):
        self.state = 0
    def reset(self):
        self.state = 0
    def read(self):
        return self.state
    def write(self, x):
        self.state = x
    def __str__(self):
        return str(self.state)
    
class StatusFlag(Register):
    def __init__(self):
        self.state = False
    def reset(self):
        self.state = False
    def set(self):
        self.state = True
        
class CPU():
    def __init__ (self):
        # Symbolic control signals
        self.memory_operation = 'nop'    # 'read', 'write', 'ir_data'
        self.alu_operation = 'nop'       # 'add', 'sub'
        self.control_operation = 'nop'   # 'jump', 'jump_Z', 'jump_N', 'jump_O', 'jump_C'
        # registers
        self.D0 = Register()
        self.MAR = Register()
        self.MDR = Register()
        self.IP = Register()
        self.IR = Register()
        #status Flags
        self.FLAG_N = StatusFlag()
        self.FLAG_Z = StatusFlag()
        self.FLAG_O = StatusFlag() 
        self.FLAG_C = StatusFlag()
        #signals
        self.IR_OPCODE = 0
        self.IR_ADDRESS = 0
        self.ALU_OUT = 0
        # Helper variables
        self.run = True
        self.trace_on = True
        self.step_by_step = False
        self.nextinstructionmode = False
        self.inHLTcycle = False
        self.nextcyclemode = False
        self.regnames =['IP', 'IR', 'D0', 'MAR', 'MDR', 'ALU_OUT',\
                                    'Z_FLAG', 'N_FLAG', 'O_FLAG', \
                                    'C_FLAG']
        self.reglens = [16, 16, 8, 16, 16, 8, 1, 1, 1, 1]
        self.cycles = [self.FETCH, 
            self.DECODE,
            self.READ_OP,
            self.EXECUTE,
            self.WRITE_BACK]
        self.cyclenames = ['FETCH', 'DECODE', 'READ_OP', 'EXECUTE', 'WRITE_BACK']
        self.currentcycle = 0

    # Helper functions
    def setdisplay(self, where):
        self.display = where

    def setcommandout(self, where):
        self.dispcommand = where

    def setinfoout(self, where):
        self.dispinfo = where
    
    def reset(self):
        Memory.M = Memory.copyM[:]
        self.__init__()
    
    def TRACE (self, tag):
        if self.trace_on == True :
            if tag == 'header' :
                if GUImode == False:
                    if self.step_by_step == True: raw_input('Press ENTER to continue...')
                    print ( '           IP      IR       D0     MAR       MDR     ALU_OUT      Z N O C')
                else:
                    if self.step_by_step == True:
                            raw_input('Press ENTER to continue...')
                    self.display.insert('end',\
                                        '           IP      IR       D0     MAR       MDR     ALU_OUT      Z N O C\n')
            else :
                if GUImode == False :
                    print ('%-10s %2d %7d %8d %7d %9d %11d      %c %c %c %c' % \
                       (tag, self.IP.read(), self.IR.read(), self.D0.read(), \
                        self.MAR.read(), self.MDR.read(), self.ALU_OUT, \
                        str(self.FLAG_Z.read())[0],
                        str(self.FLAG_N.read())[0],
                        str(self.FLAG_O.read())[0],
                        str(self.FLAG_C.read())[0]))
                else:
                    self.display.insert ('end','%-10s %2d %7d %8d %7d %9d %11d      %c %c %c %c\n' % \
                       (tag, self.IP.read(), self.IR.read(), self.D0.read(), \
                        self.MAR.read(), self.MDR.read(), self.ALU_OUT, \
                        str(self.FLAG_Z.read())[0],
                        str(self.FLAG_N.read())[0],
                        str(self.FLAG_O.read())[0],
                        str(self.FLAG_C.read())[0]))
                    self.regvalues = [\
                        self.IP.read(), self.IR.read(), self.D0.read(), \
                        self.MAR.read(), self.MDR.read(), self.ALU_OUT, \
                        str(self.FLAG_Z.read())[0],
                        str(self.FLAG_N.read())[0],
                        str(self.FLAG_O.read())[0],
                        str(self.FLAG_C.read())[0]]
                    self.regdict = {}
                    for i in self.regnames:
                        self.regdict[i] = self.regvalues[self.regnames.index(i)]
                    self.display.see('end')
                
    def SETFLAGS(self):
    # Set the FLAGS according to the ALU output 
        if self.ALU_OUT == 0 :                               # Z
            self.FLAG_Z.write(True)
        else :
            self.FLAG_Z.write(False)
        if self.ALU_OUT < 0 :                                # N
            self.FLAG_N.write(True)
        else :
            self.FLAG_N.write(False)
        if (self.ALU_OUT < -32768 ) | (self.ALU_OUT > 32767) :    # O (APPROXIMATION ONLY)
            self.FLAG_O.write(True)
        else :
            self.FLAG_O.write(False)
        if self.ALU_OUT > 65535 :                            # C (APPROXIMATION ONLY)
            self.FLAG_C.write(True)
        else :
            self.FLAG_C.write(False)
#===========================================================#
#    CPU Functions                                          #
#===========================================================#
#===========================================================#
# Fetch the next instruction                                #
#===========================================================#
    def FETCH (self):
        self.MAR.write(self.IP.read())
        self.IP.write(self.IP.read() + 1)
        self.MDR.write(Memory.M[self.MAR.read()])
        self.TRACE('header')
        self.TRACE('FETCH  ')

#===========================================================#
# Decode the instruction; generate control signals          #
#===========================================================#    
    def DECODE (self):
        self.IR.write(self.MDR.read())
        self.IR_OPCODE = self.IR.read() >> 12 # 4 MSB bits
        self.IR_OPCODE_name = Assembler.instr [self.IR_OPCODE]
        self.IR_ADDRESS = self.IR.read() & 0xFFF # 12 LSB bits
        if GUImode==True:
            self.dispcommand.insert('end',\
                self.IR_OPCODE_name+' '+str(self.IR_ADDRESS)+'\n')
            self.dispcommand.see('end')
        
        # Move OPCODE to the control unit
        self.alu_operation = 'nop'
        self.memory_operation = 'nop'
        self.control_operation = 'nop'
        if   self.IR_OPCODE_name == 'load' :
            self.memory_operation = 'read'
            self.alu_operation = 'pass_data'
        elif self.IR_OPCODE_name == 'store' :
            self.memory_operation = 'write'
            self.alu_operation = 'pass_data'
        elif self.IR_OPCODE_name == 'add' :
            self.memory_operation = 'read'
            self.alu_operation = 'add'
        elif self.IR_OPCODE_name == 'sub' :
            self.memory_operation = 'read'
            self.alu_operation = 'sub'    
        elif self.IR_OPCODE_name == 'loadi' :
            self.memory_operation = 'ir_data'
            self.alu_operation = 'pass_data'
        elif self.IR_OPCODE_name == 'halt' :
            self.memory_operation = 'nop'
            self.alu_operation = 'nop'
            self.control_operation = 'nop'
            self.run = False # the HALT instruction is 'executed' here
            self.inHLTcycle = True
        elif self.IR_OPCODE_name == 'addi' :
            self.memory_operation = 'ir_data'
            self.alu_operation = 'add'
        elif self.IR_OPCODE_name == 'subi' :
            self.memory_operation = 'ir_data'
            self.alu_operation = 'sub'
        elif self.IR_OPCODE_name == 'jmp' :
            self.control_operation = 'jump'
        elif self.IR_OPCODE_name == 'jmp_N' :
            self.control_operation = 'jump_N'
        elif self.IR_OPCODE_name == 'jmp_Z' :
            self.control_operation = 'jump_Z'
        elif self.IR_OPCODE_name == 'jmp_O' :
            self.control_operation = 'jump_O'
        elif self.IR_OPCODE_name == 'jmp_C' :
            self.control_operation = 'jump_C'
        elif self.IR_OPCODE_name == 'reserved1' :
            self.memory_operation = 'nop'
            self.alu_operation = 'nop'
            self.control_operation = 'nop'
        elif self.IR_OPCODE_name == 'reserved2' :
            self.memory_operation = 'nop'
            self.alu_operation = 'nop'
            self.control_operation = 'nop'
        elif self.IR_OPCODE_name == 'reserved3' :
            self.memory_operation = 'nop'
            self.alu_operation = 'nop'
            self.control_operation = 'nop'
        else :
            print ('No Such Instruction')
        self.TRACE('DECODE ')


#===========================================================#
# Read the operand of the instruction                       #
#===========================================================#    
    def READ_OP (self):
        if  self.memory_operation == 'read' :
            self.MAR.write(self.IR_ADDRESS)
            self.MDR.write(Memory.M[self.MAR.read()])
        elif self.memory_operation == 'write' :
            self.MAR.write(self.IR_ADDRESS)
            self.MDR.write(self.D0.read())
            Memory.M[self.MAR.read()] = self.MDR.read()
        elif self.memory_operation == 'ir_data' :
            self.MDR.write(self.IR_ADDRESS)
        elif self.memory_operation == 'nop' :
            self.MDR.write(self.MDR.read()) # do nothing !
        else :
            print ('No such Memory Operation')
        self.TRACE('READ_OP') 

#===========================================================#
# Execute the ALU operation; set the flags                  #
#===========================================================#
    def EXECUTE(self):
        # Execute the ALU operation
        if self.alu_operation == 'add':
            self.ALU_OUT = self.D0.read() + self.MDR.read()
            self.SETFLAGS()
        elif self.alu_operation == 'sub':
            # ALU_OUT = D0 - MDR
            self.ALU_OUT = self.D0.read() + (~self.MDR.read() + 1)  # TWO'S COMPLEMENT SUBTRACTION
            self.SETFLAGS()
        elif self.alu_operation == 'pass_data':
            self.ALU_OUT = self.MDR.read()
            self.SETFLAGS()
        elif self.alu_operation == 'nop':
            self.ALU_OUT = self.ALU_OUT  # do nothing !
            # no flags are set here
        else:
            print ('No such ALU operation')
        self.TRACE('EXECUTE')
    


#===========================================================#
# Write back the ALU result; change IP if this was a jump   #
#===========================================================#    
    def WRITE_BACK (self):
        self.inHLTcycle = False
        # write back the result of the ALU to D0
        self.D0.write(self.ALU_OUT)
        # if this was a form of the jump instruction then change IP accordingly
        if self.control_operation == 'jump' :
            self.IP.write(self.IR_ADDRESS)
        elif self.control_operation == 'jump_N' :
            if self.FLAG_N.read() :
                self.IP.write(IR_ADDRESS)
        elif self.control_operation == 'jump_Z' :
            if self.FLAG_Z.read() :
                self.IP.write(self.IR_ADDRESS)
        elif self.control_operation == 'jump_O' :
            if self.FLAG_O.read() :
                self.IP.write(self.IR_ADDRESS)
        elif self.control_operation == 'jump_C' :
            if self.FLAG_C.read() :
                self.IP.write(self.IR_ADDRESS)
        elif self.control_operation == 'nop' :
            self.IP.write(self.IP.read()) # do nothing
        else :
            print ('Bad control command')
        self.TRACE('WRITE_BACK') 



#===========================================================#
# MAIN CPU LOOP                                             #
#===========================================================#    
    def start (self, start_address):
        if GUImode == False: print ('PyCPU(c): started '+ str(datetime.today()))
        self.IP.write(start_address)
        if GUImode == False:
            while self.run:
                self.FETCH()
                self.DECODE()
                self.READ_OP()
                self.EXECUTE()
                self.WRITE_BACK()
                input()
        else:
            pass

    def execall(self, start_address, event):
        if self.currentcycle>0:
            self.dispinfo.insert('end','Cannot execute remainder of programm, complete cycles for current instruction first\n')
            self.dispinfo.see('end')
            return
        if not self.nextinstructionmode and not self.nextcyclemode:
            self.IP.write(start_address)
        while self.run:
            self.FETCH()
            self.DECODE()
            self.READ_OP()
            self.EXECUTE()
            self.WRITE_BACK()
        self.dispinfo.insert('end','Program terminated\n')
        self.dispinfo.see('end')

    def nextcycle(self, event):
        self.nextcyclemode = True
        if self.run or self.inHLTcycle:
            self.cycles[self.currentcycle]()
            self.dispinfo.insert('end',self.cyclenames[self.currentcycle]+' cycle executed\n')
            self.currentcycle = (self.currentcycle + 1) %  len(self.cycles)
        else:
            self.dispinfo.insert('end','Program terminated\n')
        self.dispinfo.see('end')


    def nextinstruction(self, event):
        self.nextinstructionmode = True
        if self.currentcycle>0:
            self.dispinfo.insert('end','Cannot execute next instruction, complete cycles of current instruction first\n')
            self.dispinfo.see('end')
            return
        if self.run:
            self.FETCH()
            self.DECODE()
            self.READ_OP()
            self.EXECUTE()
            self.WRITE_BACK()
            self.dispinfo.insert('end','Instruction executed\n')
        if not self.run:
            self.dispinfo.insert('end','Program terminated\n')
        self.dispinfo.see('end')

#===========================================================#    
if __name__ == '__main__':
    GUImode = False
    myassembler = Assembler()

    Memory.load([myassembler.asm('load',6), # D0 = M[6]
         myassembler.asm('subi',1),         #1:D0 = D0 - 1 
         myassembler.asm('jmp_Z',4),        #  if D0 == 0 goto 4
         myassembler.asm('jmp',1),          #  goto 1  
         myassembler.asm('store',6),        #4:M[6] = D0
         myassembler.asm('halt',0),         #  halt
         2])

    mycpu = CPU()
    mycpu.start(0)
else:
    print('started in GUI mode')
    GUImode = True




