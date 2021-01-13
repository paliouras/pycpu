# Use OO-PyCPU and gui interface
#   Emulates the steps of assembling machine code,
#   loading machine code to memory, and code execution
#   by the CPU
# 20171210 vp
import pyGUI as gui
import CPU_asm_v3_5 as cpu
import extendcpu as ext    # modify extendcpu.py

# instantiate an Assembler
myassembler = cpu.Assembler()
# 
# Properly define class AssemblerFiler so that the
# code below works.
extassembler = ext.AssemblerFiler()
programImage2 = extassembler.getfromfile('assembly.txt')

# Use an Assembler instance to generate machine code
# written explicitly for clarity
referenceprogramImage = \
        [myassembler.asm('load', 6),  #    D0 = M[6]
         myassembler.asm('subi', 1),  # 1: D0 = D0 - 1 
         myassembler.asm('jmp_Z', 4), #    if D0 == 0 goto 4
         myassembler.asm('jmp', 1),   #    goto 1  
         myassembler.asm('store', 6), # 4: M[6] = D0
         myassembler.asm('halt', 0),  #    halt
         2] # number of iterations at M[6]

# check if reference programImage2 is correctly read and translated
# remove following ling for programme images other than reference
assert (referenceprogramImage == programImage2)

# load machine code to memory
cpu.Memory.load(programImage2)

# instantiate a CPU
mycpu = cpu.CPU()

# start interactive emulation
gui.main(mycpu, 0, cpu.Memory)



