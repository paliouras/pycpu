import CPU_asm_v3_5 as cpu


class AssemblerFiler(cpu.Assembler):
    def getfromfile(self, filename):
        image = []
        # write your code starting here
        # your code should handle blank lines
        lines = []
        with open(filename, 'r') as f:
            for line in f:
                pline = line.strip().split()
                if pline:
                    lines.append(pline)
                    try:
                        lines[-1][-1] = int(lines[-1][-1])
                    except:
                        print('line: ', line)
        print (lines)
        for i in lines:
            if len(i)>1:
                image.append(self.asm(*i))
            else:
                image.append(i[0])
        # up to here (should be no more than 15 to 20 lines)
        return image
