def HEX_TO_INC(A_HEX):
    #convert hex number into a int
    return int(A_HEX,16)

def INC_TO_HEX(A_INT,LEN = 1):
    #print(A_INT)
    #converts a interger into a hex number with a length LEN
    if (A_INT < 0):
        A_INT = (A_INT * -1) + 0x8000 #if negitive sign and posify
    A_INT = hex(A_INT)[2:] #slice of the 0x part
    for i in range(LEN - len(A_INT)):
        A_INT = "0" + A_INT #slap the 0s we need
    return A_INT #otherwise return nomal it can be longer

def BIN_TO_INC(A_BIN):
    return int(A_BIN,2)

def strip_comments(CODE_LINE):
    # this method goes though a line of code and removes any thing passed a #
    if ("#" not in CODE_LINE):
        return CODE_LINE #no need to strip if there is no such thing as a #
    return CODE_LINE.split("#")[0] #otherwise return the half before a comment

def det_line_type(CODE_LINE):
    #method takes in a line of code and looks at first char 
    #to determan what line type it is
    lookup = {".":"Var","@":"Address","#":"Comment"}
    try:
        return lookup[CODE_LINE[0]] #try to lookup to see if the start is known
    except:
        return "Instruction"

def read_int_lit(CODE_LINE):
    lit_type = det_lit_type(CODE_LINE)
    if (lit_type == "Int"):
        return int(CODE_LINE)
    if (lit_type == "Binary"):
        return BIN_TO_INC(CODE_LINE)
    if (lit_type == "Char"):
        special_chars = {r"\0":0,r"\b":8,r"\n":10,r"\r":13}
        if (CODE_LINE[1:3] in special_chars.keys()):
            return special_chars[CODE_LINE[1:3]]
        return ord(CODE_LINE[1])
    if (lit_type == "Hex"):
        return HEX_TO_INC(CODE_LINE)
    if (lit_type == "Register"):
        reg_lookup = {"SP":14,"FR":15}
        if (CODE_LINE in reg_lookup.keys()):
            return reg_lookup[CODE_LINE]
        return HEX_TO_INC(CODE_LINE[1])

def read_vec(CODE_LINE):
    line_type = det_lit_type(CODE_LINE)
    VALS = []
    if (line_type == "String"):
        for chars in CODE_LINE:
            CODE_LINE = CODE_LINE[1:-1]
            VALS.append(ord(chars)) #If this is a string then each char is a value
    elif (line_type != "Vector"):
        VALS.append(read_int_lit(CODE_LINE))
    else:
        CODE_LINE = CODE_LINE[1:-1]
        CODE_LINE = CODE_LINE.split(',') #otherwise we are dealing with a vector
        for item in CODE_LINE:
            VALS.append(read_int_lit(item)) #bleep it only intergers in the code line no reason for vars or addresses to be in a vector
    #print(VALS)
    return VALS            
    

def det_lit_type(CODE_SEG):
    lookup = {"'":"Char","@":"Address","\"":"String","[":"Vector",".":"Var"}
    if (CODE_SEG[0] in lookup.keys()):
        return lookup[CODE_SEG[0]]
    
    lookup = {"0b":"Binary","0x":"Hex"}
    if (CODE_SEG[0:2] in lookup.keys()):
        return lookup[CODE_SEG[0:2]]
    
    if CODE_SEG.isdigit() or ((CODE_SEG[0] == '-') and CODE_SEG[1:].isdigit()):
        return "Int"
    if (CODE_SEG in ("SP","FR","R0","R1",
                    "R2","R3","R4","R5",
                    "R6","R7","R8","R9",
                    "RA","RB","RC","RD",
                    "RE","RF")):
        return "Register"
    return "Unknown"

def read_var_dec(VAR_DATA):
    var_type = det_lit_type(VAR_DATA)
    if var_type in ("String","Vector"):
        return read_vec(VAR_DATA)
    return read_int_lit(VAR_DATA)
                    
class READ_OPCODES:
    #This method takes in a sheet of opcodes and returns a 2d array with 0 being a directory of Mems with opcodes 1 being opcodes that take a 3rd oprand and 3 being operation with no oprands
    
    def strip_sheet_comments(Opcode_string):
        #method strips all lines with "#" in them and return a full stream
        lines = Opcode_string.split("\n")
        accum = "" 
        for line in lines:
            if (line.find("#") == -1): #if there isnt a #
                accum = accum + line + '\n'
        return accum[:-1] #return minus final newline   
    
    def read_file(fname):
        #takes in a file and returns a list of MEMS and opcodes 3 op instructions and 0 oprand instructions
        f = open(fname)
        fstr = f.read()
        f.close()
        fstr = READ_OPCODES.strip_sheet_comments(fstr)
        fstr = fstr.split("/")
        return fstr
    
    def gen_dir(Mems_and_opcodes):
        #method takes in mems and opcodes and returns a directory of mems and 
        #associated opcodes
        mAcs = Mems_and_opcodes.split("\n")[:-1] #mAC mems AND opcodes
        new_dic = {}
        for mAc in mAcs:
            s = mAc.split(":")
            new_dic.update({s[0]:int(s[1],16)})
        return new_dic
    
    def run(fname):
        #method that does the magic
        parts = READ_OPCODES.read_file(fname)
        opcode_dir = READ_OPCODES.gen_dir(parts[0])
        three_op_ins = parts[1][1:-1].split('\n')
        zero_op_ins = parts[2][:-1].split('\n')
        return [opcode_dir,three_op_ins,zero_op_ins]
            

if __name__ == "__main__":
    def test_con():
        for i in range(10,20):
            k = INC_TO_HEX(i,2)
            print(k)
            print(HEX_TO_INC(k))
    def test_strip_comment():
        print(strip_comments("TESTING #this shouldent be here!"))
    
    def test_READ_OPCODES():
        for i in range(3):
            print(READ_OPCODES.run("OPCODES.txt")[i])
            print('\n')
    def test_det_line_type():
        print(det_line_type(".Var"))
        print(det_line_type("@address"))
        print(det_line_type("#Comment"))
        print(det_line_type("ins instruction"))
        
    def test_det_lit_type():
        test_vals = ("'c'","@Address",".var","\"string\"","[1,2,3,3]","0b1001","0x45","1234")
        for test in test_vals:
            print(det_lit_type(test))
    tester = "'a'"     
    print(INC_TO_HEX(255,1))     
    
              