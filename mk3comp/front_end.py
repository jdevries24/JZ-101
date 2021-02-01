from pycparser import c_parser,c_ast
from middle_end import middle_end
from backend import jz_101_assembler

class front_end:
	#So this comp works in thee stages 
	#the front end preprep this stage removes comments
	#Reads the Macros and controls the overall compile proscess
	#the middle end parses the c_code and generates it 
	#into a assembly file
	#Finaly the back end assembles the assembly code and returns 
	#a hexfile and output table
	
	def __init__(self,file_name):
		self.asm = ""
		self.global_decl = ""
		self.file_name = file_name
		self.main_file = False
		
	def run(self):
		c_code = self.read_c_code()
		c_code = self.pre_process(c_code)
		m = middle_end(c_code)
		self.asm = self.asm + m.run() + self.global_decl
		self.write_assembly()
		b = jz_101_assembler()
		b.run(self.asm)
		self.write_hex(b)
		self.write_secondary_output(b)
		
	def pre_process(self,c_code):
		#this method removes comments and handles macros
		cline = c_code.split('\n')
		p_code = ""
		for line in cline:
			if len(line) == 0:
				p_code += '\n'
				continue
			if ("#ifmain" in line) and not(self.main_file):
				break #stop reading if where not in the main file
			if line[0] == "#":
				self.handle_macro(line)
				p_code += '\n'
				continue
			split_line = line.split('//')#remove the comments from code
			if len(split_line[0]) > 0:
				p_code += split_line[0] + '\n'
			else:
				p_code += '\n'
		return p_code
	
	def handle_macro(self,line): 
		if "#main" in line: #if we are the main file load in the prestart asm instructions and set main to true
			self.asm = "NOP\nINC ,SP,SP,0xFFEF\nJMP ,0,0,@main\n"
			self.main_file = True
			return
		if "#include" in line:
			self.link(line.split(' ')[1]) #call in the linker
			
	def link(self,fname):
		#opens and reads a assembly file throwing global vars on the bottem where they should be
		asm_file = open(fname + '.s','r')
		asm_str = asm_file.read()
		asm_file.close()
		self.asm += asm_str.split("#$global_vars")[0]
		self.global_decl += asm_str.split("#$global_vars")[1]

	def read_c_code(self):
		C_file = open(self.file_name + '.c','r')
		cstring = C_file.read()
		C_file.close()
		return cstring
		
	def write_assembly(self):
		asm_file = open(self.file_name + ".s",'w')
		asm_file.write(self.asm + self.global_decl)
		asm_file.close()
		
	def write_hex(self,assembler):
		hex_file = open(self.file_name + '.h','w')
		hex_file.write(assembler.get_output())
		hex_file.close()
		
	def write_secondary_output(self,assembler):
		so_file = open(self.file_name + '.d','w')
		so_file.write(assembler.get_secondary_output())
		so_file.close()

if __name__ == "__main__":
	base = ""
	input_str = input("Filename: ")
	if input_str[-2:] == ".c":
		input_str = input_str [:-2]
	f = front_end(base + input_str)
	f.run()
	
		