from ASM_TOOLS import *

class Assembly_Error(Exception):
    
    pass

class sym:
    #this is a class to represent symbols because reasons 
    
    def __init__(self,name,value):
        self.name = name
        self.value = value

class assembler:

    #Core class of the assembly softwere.The assembler works via 
    #two passes the first pass generates the 
    #symbol table then the secound pass generates the code
    #then that code is converted into a Logisim Hex file
    
    def __init__(self): 
        #instelises the complier as we need a global symbol table and 
        #address counter
        self.address = 0 #count where in the program each ins is used
        self.symbol_table = [] #the symbol table stores symbols ie vars and pointers
        #{symbol_name:[symbol_var,symbol_contents if list]}
        self.lines = [] #we also need to declare a list of lines in the program
        self.data = None
        self.db_table = []
        self.prognums = []
     
    def open_and_prep_asm(self,asm_str):
        self.lines = asm_str.split("\n") #split the string into lines
        
        
    
    def open_and_prep_oprands(self,op_file):
        self.data = READ_OPCODES.run(op_file) #get the codes into data
     
    def first_pass(self):
        #first pass though the code 
        for line in self.lines:
            if ((det_line_type(line) == "Comment") or (len(line) == 0)):
                    continue
            line = line.split("#")[0] #Strip off comment
            line_type = det_line_type(line) 
            #print(line + ":"+line_type)
            #get what type of line where working with
            if (line_type == "Address"):
                line = line.replace(" ","") #remove spaces from a adress
                self.symbol_table.append(sym(line,[int(self.address)]))
                continue      
            if (line_type == "Instruction"):
                line = line.replace(" ","") #remove the space
                self.address += 1 #need to track loc for adresses
                if (line.split(',')[0] in self.data[1]): #list of two oprand ins
                    self.address += 1 #add another adress spot
                continue  
            if (line_type == "Var"):
                dec_name = line.split(',')[0]
                values = line.split(',',1)[1]
                v = read_vec(values)
                #print(v)
                self.symbol_table.append(sym(dec_name,[int(self.address),v]))
                self.address += len(v)
                                         

    def second_pass(self):
        #this method does two things generates the int list for hex and a debug table
        addr = 0
        for line in self.lines:
            #print(line)
            l = line.split('#')[0]
            l = l.replace(" ","")
            if (det_line_type(l) != "Instruction") or (len(l) <= 0):
                self.db_table.append([None,None,line]) #IF its not a instruction just add the line to the debug table
                continue # and go back to the top
            line_data = self.define_operands(l) #get the line data
            ops = self.generate_opcode(line_data) #gen opcodes
            #print(ops)
            self.db_table.append([addr + 0,ops[0],line])
            self.prognums.append(ops[0])
            if (line_data[0] > 1):
                self.db_table.append([addr + 1,ops[1],""])
                self.prognums.append(ops[1])
            addr += line_data[0] 
        for symbol in self.symbol_table:
            if (len(symbol.value) > 1): #if this is a list of some kind
                #print(symbol.value[1])
                self.prognums += symbol.value[1] #add the vector
            
            
        
    
    def generate_opcode(self,data):
        #takes in data of [leng,Ins num,oprand 1,oprand 2,oprand three and returns
        #A list with numbers
        if((data[2] > 15) or (data[3] > 15)):
            print(line)
            raise Assembly_Error("Oprand_out_of_bounds")
            
        opcode = (data[1] << 8) + (data[2] << 4) + (data[3])
        if (data[0] > 1):
            return [opcode,data[4]]
        return [opcode]
        
    
    def define_operands(self,line):
        #this method reads the instruction and comes back with a list like
        #[Length,Opcode,Oprand 1,Oprand 2,Oprand 3]
        segments = line.split(',') #split the line useing ,
        mem = segments[0] #this will be easer then segments[0] all the time
        if (mem not in self.data[0].keys()):
            print(line)
            raise Assembly_Error("Unknown Instruction")
        if (mem in self.data[2]): #this is the no opcode needed box
            return [1,self.data[0][mem],0,0]
        #now that thats out of the way
        retval = [1,0,0,0,0]
        if (len(segments) < 3):
            print(line)
            raise Assembly_Error("Missing opreands")
        retval[1] = self.data[0][mem] #put the opcode into the opcode bin
        retval[2] = self.get_int_code(segments[1]) #first opcode
        retval[3] = self.get_int_code(segments[2]) #second opcode
        if (mem in self.data[1]): #codes with a third oprand
            if(len(segments) < 4):
                print(line)
                raise Assembly_Error("Missing opreands")
            retval[4] = self.get_int_code(segments[3]) #add the final oprand 
            retval[0] += 1
        return retval            
        

    def get_int_code(self,oprand_str):
        #this method generates a interger bassed on the string a oprand takes
        if (oprand_str == None):
            return 0
        op_type = det_lit_type(oprand_str)
        if (op_type in ("Address","Var")):
            Val = self.serch_symbols(oprand_str)
            if (Val == -1):
                print(oprand_str)
                raise Assembly_Error("Cannot Find symbol")
            return Val
        Val = read_int_lit(oprand_str)
        return Val
    
    def serch_symbols(self,name):
        for symb in self.symbol_table:
            if (name == symb.name):
                return symb.value[0]
        return -1 
    
    def output_db_table(self,db_file):
        File_str = "ADDR DATA\n"
        for entity in self.db_table:
            for item in entity:
                File_str = File_str + " "
                if (item == None):
                    File_str = File_str + "    "
                    continue
                if (type(item) == int):
                    File_str = File_str + INC_TO_HEX(item,4)
                    continue
                File_str = File_str + item                
            File_str = File_str + "\n"
        with open(db_file,'w') as f:
            f.write(File_str)
            f.close()

    def output_hex_file(self,hex_file):
        File_str = "v2.0 raw"
        c = 0
        for nums in self.prognums:
            if ((c % 8) == 0 ):
                File_str += '\n' #put in a newline every eight chars for redability
            File_str += (" " + INC_TO_HEX(nums,4))
            c += 1
        f = open(hex_file,'w')
        f.write(File_str)
        f.close()
                
        
    def run(self,ASM_STR,OP_FILE):
        self.open_and_prep_oprands(OP_FILE)
        self.open_and_prep_asm(ASM_STR)
        self.first_pass()
        self.second_pass()
                    
                                    

if __name__ == "__main__":
    r = assembler()
    assembly_file = input("Assembly_file: ")
    assembly_file = read(assembly_file,'r')
    asm = assembly_file.read()
    r.run(asm,"OPCODES.txt")
    hex_output = input("Output hex: ")
    r.output_hex_file(hex_output)
    include_db = input("Include DB table? ")
    if (include_db.lower()[0] == "y"):
        db_table_file = input("db_table_filename: ")
        r.output_db_table(db_table_file)
    
                
                