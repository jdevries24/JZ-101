from pycparser import c_parser,c_ast
from AST_to_ASM import *
from ASM import *

class mk1comp:
    
    def __init__(self,C_fname,working_dir = ""):
        self.wd = working_dir
        self.c_fname = working_dir + C_fname
        self.main = False
        self.at_break = False
        self.asm_code = r"""NOP
INC ,0,SP,0xFFEF
JMP ,0,0,@main
""" #init routine for the processor
        self.asm_var = ""
        self.a = assembler()
    
    def c_prep(self,c_str):
        raw_prog = ""
        c_lines = c_str.split('\n')
        for l in c_lines:
            if (not self.main) and (self.at_break):
                return raw_prog
            if (len(l.strip(' ')) == 0):
                raw_prog += '\n' #keep the newline helps with debuging
                continue
            #if l.strip(' ')[0] == '#':
                #self.hand_macro(l) #use seprate method for handling macros
                #continue
            if ('//' in l):
                raw_prog += l.split('//')[0] + '\n'
            else:
                raw_prog += l + '\n'
        return raw_prog
    
    def hand_macro(self,ml):
        m_parts = ml.split(' ') #split on the space
        if m_parts[0] == "#include":
            fn = self.wd +m_parts[1] + ".s" #dont include s Ill know what I mean
            print(fn)
            f = open(fn,'r')
            asm_str = f.read()
            asmp = asm_str.split("#$")
            self.asm_code += asmp[0] #open up and link the two asm codes together
            self.asm_var += asmp[1] #then hold off on adding the 
            f.close()
        if m_parts[0] == "#main":
            self.main = True
            self.asm_code += "NOP\n"
            self.asm_code += "INC ,0,SP,0xffef\n"
            self.asm_code += "JMP ,0,0,@main\n"
        if m_parts[0] == "#break":
            self.at_break = True

    def parse(self,c_code):
        cp = c_parser.CParser()
        AST = cp.parse(c_code)
        return AST
    
    def code_gen(self,AST):
        cmp = AST_to_ASM()
        #AST.show()
        cmp.v_FileAST(AST)
            
        self.asm_code += cmp.asm
        
    def run(self):
        print("Prep")
        c_f = open(self.c_fname + ".c",'r')
        c_c = c_f.read()
        c_f.close()
        c_c = self.c_prep(c_c)
        print("Parsing")
        #print(c_c)
        ast = self.parse(c_c)
        print("Code_Gen")
        self.code_gen(ast)
        asm_f = open(self.c_fname + '.s','w')
        asm_f.write(self.asm_code + self.asm_var)
        asm_f.close()
        print("Assembling")
        self.a.run(self.asm_code + self.asm_var,"OPCODES.txt")
        print("outputting")
        self.a.output_hex_file(self.c_fname + ".h")
        self.a.output_db_table(self.c_fname + ".d")

if __name__ == "__main__":
    f_name = input("C_file: ")
    if (f_name[-2:] == ".c"):
        f_name = f_name[:-2] #just remove the file extention if needed
    c = mk1comp(f_name)
    c.run()
        