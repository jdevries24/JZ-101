class Assembly_Error(Exception):
    
    def __init__(self,message,line):
        print(line)
        self.message = message
        

class jz_101_assembler:

	def __init__(self):
		self.symbol_table = {}
		self.values = [] #[ADDRESS,VALUE,LINE]
		#store the instructions as one big diconary
		self.INS = {"NOP":0x00,"LDA":0xA0,"STR":0xB0,"MOV":0xC0,
						"INC":0x37,"DEC":0x38,"ADD":0x30,"SUB":0x31,
						"LSL":0x32,"LSR":0x33,"AND":0x34,"ORR":0x35,
						"XOR":0x36,"ADC":0x39,"SDC":0x3A,"ROL":0x3B,
						"ROR":0x3C,"CMP":0x3F,"JMP":0x45,"CAL":0x55,
						"RTN":0x65,"JME":0x43,"JML":0x42,"JMG":0x44,
						"JMC":0x41,"CIN":0xEE,"RIN":0xE0,"HTI":0xE2,
						"HCF":0xFF}
		#To Word instructions
		self.TWINS = ("LDA","STR","INC","DEC",
		  "JMP","CAL","JMP","JME",
		  "JML","JMG","JMC")
		self.NOINS = ("NOP","RTN","HTI","HCF")

	def split_comma(self,astr):
	#So Ive had issues with split so insted lets make our own method
		parts = []
		accum = ""
		for char in astr:
			if char != ',':
				accum += char
			else:
				if len(accum) == 0:
					parts.append('0')
				else:
					parts.append(accum)
					accum = ""
		if len(accum) != 0:
			return parts + [accum]
		return parts + ['0']

	def get_int(self,uSTR):
		#method to return a integer from a string of 
		#unknown types
		if uSTR.isdigit():
			return int(uSTR)
		if ("0x" in uSTR):
			return int(uSTR,16)
		if ("0b" in uSTR):
			return int(uSTR,2)
		lookup = {"R0":0,"R1":1,"R2":2,"R3":3,
		"R4":4,"R5":5,"R6":6,"R7":7,
		"R8":8,"R9":9,"RA":10,"RB":11,
		"RC":12,"RD":13,"SP":14,"FR":15}
		if uSTR in lookup.keys():
			return lookup[uSTR]
		raise Assembly_Error("Unknown Type",uSTR)

	def get_val(self,Parm):
		if Parm in self.symbol_table.keys():
			return self.symbol_table[Parm]
		try:
			return self.get_int(Parm)
		except Assembly_Error:
			raise Assembly_Error("unknown value",Parm)

	def int_to_hexstr(self,a_int):
		if(a_int == None):
			return "    "
		hstr = hex(a_int)[2:] #con to hex
		for i in range(4 - len(hstr)):
			hstr = "0" + hstr #add zeros as needed
		return hstr

	def prep(self,asm_str):
		#strip off spaces and comments
		lines = asm_str.split('\n')
		accum = ""
		for line in lines:
			m_accum = ""
			for char in line:
				if char not in (' ','#'):
					m_accum += char
				else:
					if char == ' ':
						continue
					if char == '#':
						break
			if len(m_accum) != 0:
				accum += m_accum + '\n'
		return accum[:-2]

	def first_pass(self,asm_str):
	#first pass gathering data about symbols
		lines = asm_str.split('\n') #newline still the spliter
		addr = 0 #well need to parse our string
		for line in lines:
			if line[0] == "@":#Address declaration
				self.symbol_table.update({line:addr})
				continue
			if line[0] == ".":#var declaration
				ID = self.split_comma(line)[0]
				self.symbol_table.update({ID:addr})     #load into symtable
				addr += len(self.split_comma(line)) - 1 #inc addr by amount needed
				continue
			ins = self.split_comma(line)[0]
			if ins in self.TWINS:
				addr += 2
			else:
				addr += 1

	def secound_pass(self,asm_str):
		lines = asm_str.split('\n')
		addr = 0
		for line in lines:
			if line[0] == "@":
				self.values.append([None,None,line]) #no need to load nones
				continue
			if line[0] == ".":
				self.values.append([None,None,line])
				self.read_var(line)
				addr += len(self.split_comma(line)) - 1
				continue
			self.read_ins(line,addr)
			ID = self.split_comma(line)[0]
			if ID in self.TWINS:
				addr += 1
			addr += 1

	def read_ins(self,line,addr):
		sections = self.split_comma(line)
		if sections[0] not in self.INS.keys():
			raise Assembly_Error("unknown ins",line)
		if sections[0] in self.NOINS:
			opcode = self.INS[sections[0]] << 8 #Just need the opcode
			self.values.append([addr,opcode,line])
			return
		if len(sections) < 3:
			raise Assembly_Error("not enoght parms",line)
		opcode = self.INS[sections[0]] << 8 #get the opcode
		p1 = self.get_val(sections[1]) << 4 #getoprand 1
		p2 = self.get_val(sections[2])
		opcode += p1 + p2
		self.values.append([addr,opcode,line])
		if sections[0] not in self.TWINS:
			return
		if len(sections) < 4:
			raise Assembly_Error("not enogh porms",line)
		#simply addr + 1,the value result,and empty string
		self.values.append([addr + 1,self.get_val(sections[3]),""]) 

	def read_var(self,line):
		sections = self.split_comma(line)[1:] #get everthing but init
		for sec in sections:
			self.values.append([None,self.get_val(sec),None]) #append values

	def run(self,asm_str):
		#take in a string of assembly code as assemble it
		asm_str = self.prep(asm_str)
		self.first_pass(asm_str)
		self.secound_pass(asm_str)

	def get_output(self):
		accum = "v2.0 raw"
		i = 0
		for val in self.values:
			if(val[1] == None):
				continue
			if ((i % 8) == 0):
				accum += '\n'
			accum += self.int_to_hexstr(val[1]) + " "
			i += 1
		return accum

	def get_secondary_output(self):
		#returns values as a secondary_output
		accum = ""
		for val in self.values:
			if (val[2] == None):
				continue #if no string then where a value boring!
			accum += self.int_to_hexstr(val[0]) + ' ' 
			accum += self.int_to_hexstr(val[1]) + ' ' 
			accum += val[2] + '\n'
		return accum
            
              
                
        
    