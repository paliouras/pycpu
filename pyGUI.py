#20171208-vp
import tkinter as tk
import random

# define function decorator to update memory and
# register views. Applied on class GUI methods
def updateviews(func):
    def wrapper(self, event):
        func(self, event)
        self.readvalues()
        self.printmemory()
    return wrapper

class Register():
    def __init__(self, master, name, length=8):
        self.data = tk.StringVar()
        self.bitlength = length
        self.namelabel = tk.Label(master, text=name, font='Consolas 10')
        self.namelabel.pack(side='left', padx=10)
        self.valuelabel = tk.Label(master, textvariable=self.data, font='Consolas 10')
        self.valuelabel.pack(side='left', padx=5)
        

class RegisterDisplayer():
    registers = {}
    def __init__(self, master, name, length = 8 ):
        RegisterDisplayer.registers[name]= Register(master, name, length)
                                           
        
class GUI():
    def __init__(self, r, cpu, startaddress, memory):
        self.r = r
        self.r.title('GUI OO pyCPU')
        self.cpu = cpu
        self.r.wm_geometry('1200x600+50+50')
        self.okfunc = cpu.start
        self.memory = memory
        self.memory.check()
        self.startaddress = startaddress
        self.widgets()
        self.initvalues()
        cpu.setdisplay(self.text)
        cpu.setcommandout(self.comtext)
        cpu.setinfoout(self.infotext)
        self.start_message()
        
    def widgets(self):
        self.regf = tk.Frame(self.r)
        regs = self.cpu.regnames
        regslen = self.cpu.reglens  
        list(map(lambda x : RegisterDisplayer(self.regf, *x),\
            zip(regs, regslen)))
        self.regf.pack()
        self.tf = tk.Frame(self.r)
        self.ptf = tk.Frame(self.tf)
        tk.Label(self.ptf,text='Κύκλοι εντολής').pack()
        self.text = tk.Text(self.ptf, font='Consolas 10', width=80, height=19)
        self.scroll = tk.Scrollbar(self.ptf, command=self.text.yview)
        self.scroll.pack(side='right', fill='y')
        self.text.configure(yscrollcommand=self.scroll.set)
        self.text.pack(side='left', padx=10, pady=5)
        self.ptf.pack(side='left')
        self.mtf = tk.Frame(self.tf)
        tk.Label(self.mtf, text='Περιεχόμενα μνήμης').pack()
        self.memtext = tk.Text(self.mtf, font='Consolas 10', width=20, height=19)
        self.scrollmem = tk.Scrollbar(self.mtf, command=self.memtext.yview)
        self.scrollmem.pack(side='right', fill='both')
        self.memtext.configure(yscrollcommand=self.scrollmem.set)
        self.memtext.pack(side='left', fill='both', padx=10, pady=5)
        self.mtf.pack(side='left')
        self.comtf = tk.Frame(self.tf)
        tk.Label(self.comtf, text='Εντολές').pack()
        self.comtext = tk.Text(self.comtf, font='Consolas 10', width=20, height=19)
        self.comscroll = tk.Scrollbar(self.comtf, command=self.comtext.yview)
        self.comscroll.pack(side='right', fill='both')
        self.comtext.configure(yscrollcommand=self.comscroll.set)
        self.comtext.pack(side='left', fill='both', padx=10, pady=5)
        self.comtf.pack(side='left')
        self.tf.pack()
        self.infof = tk.Frame(self.r)
        self.infotext = tk.Text(self.infof, font='Consolas 10', width=100,  height=4)
        self.infscroll = tk.Scrollbar(self.infof, command=self.infotext.yview)
        self.infscroll.pack(side='right', fill='both')
        self.infotext.configure(yscrollcommand=self.infscroll.set)
        self.infotext.pack(side='left', fill='both', padx=10, pady=10)
        self.infof.pack()
        self.butf = tk.Frame(self.r)
        button = tk.Button(self.butf, text='EXEC PROGRAM')
        button.bind('<Button-1>', self.execall)
        button.pack(side = 'left' )
        button2 = tk.Button(self.butf, text='NEXT INSTRUCTION')
        button2.bind('<Button-1>', self.nextinstruction)
        button2.pack(side = 'left')
        button3 = tk.Button(self.butf, text='NEXT CYCLE')
        button3.bind('<Button-1>', self.nextcycle)
        button3.pack(side = 'left')
        button3 = tk.Button(self.butf, text='RESET')
        button3.bind('<Button-1>', self.reset)
        button3.pack(side = 'left')
        self.butf.pack()

    def start_message(self):
        self.infotext.insert('end','EXEC PROGRAM: εκτέλεση προγράμματος\n')
        self.infotext.insert('end','NEXT INSTRUCTION: εκτέλεση επόμενης εντολής\n')
        self.infotext.insert('end','NEXT CYCLE: εκτέλεση επόμενου βήματος εκτέλεσης\n')
        self.infotext.insert('end','RESET: αρχικοποίηση CPU και επαναφόρτωση μνήμης\n')

    @updateviews
    def nextinstruction(self, event):
        self.cpu.nextinstruction(event)
        
    @updateviews
    def nextcycle(self, event):
        self.cpu.nextcycle(event)
        
    @updateviews
    def execall(self, event):
        self.cpu.execall(self.startaddress, event)
        
    def initvalues(self):
        for i in RegisterDisplayer.registers.keys():
            bits = RegisterDisplayer.registers[i].bitlength
            value = format(0, '0'+str(int(bits/4))+'X') 
            RegisterDisplayer.registers[i].data.set(value)
        
    def setvalues(self, vals = {}):
        for i in RegisterDisplayer.registers.keys():
            bits = RegisterDisplayer.registers[i].bitlength
            value = format(random.randint(0,2**bits-1), '0'+str(int(bits/4))+'X') 
            RegisterDisplayer.registers[i].data.set(value)

    def readvalues(self):
        for i in RegisterDisplayer.registers.keys():
            bits = RegisterDisplayer.registers[i].bitlength
            try:
                value = format(int(self.cpu.regdict[i]), '0'+str(int(bits/4))+'X')
            except:
                value = self.cpu.regdict[i] 
            RegisterDisplayer.registers[i].data.set(value)
            

    def reset(self, event):
        self.text.delete('1.0', 'end')
        self.comtext.delete('1.0', 'end')
        self.infotext.insert('end', 'CPU reset, memory reloaded\n')
        self.infotext.see('end')
        self.cpu.reset()
        self.initvalues()
        self.printmemory()

    def printmemory(self):
        self.memtext.delete('1.0', 'end')
        for i in range(len(self.memory.M)):
            v = self.memory.M[i]
            self.memtext.insert('end',\
                format(i,'04d')+': '+format(v,'04X') + ' ('+str(v)+')\n')
        
 
def main(*args):
    root = tk.Tk()
    a = GUI(root, args[0], args[1], args[2])
    root.mainloop()


if __name__ == '__main__':
    print('requires arguments and/or to be imported')
