#This File Holds Routines for returning assembly statements 
#For Certen BIN OPS

class assembly_r: #short for assembly routines
    
    def Load_From_Stack(Stackpos,RegNUM):
        return "LDA ,SP,"+ str(RegNUM) + "," + str(Stackpos)
    
    def Store_To_Stack(Stackpos,RegNUM):
        return "STR ," + str(RegNUM) + ",SP,"+ str(Stackpos)
    
    def Call(Routine_Name):
        return "CAL ,0,0,@"+str(Routine_Name)
    
    def Arithmitic(Math_type,Source_Reg,Dest_Reg):
        mems = {"+":"ADD","-":"SUB","||":"ORR","&&":"AND","^^":"XOR"}
        return mems[Math_type] + " ," + str(Source_Reg) + "," + str(Dest_Reg)
    
    def Jump(Location):
        return "JMP ,0,0,@"+str(Location)
    
    def Comp_And_Branch(Condition,Reg1,Reg2,Location):
        mems = {"<":"JML",">":"JMG","==":"JME","!=":"JME"}
        if (Condition != "!="):
            return "CMP ,"+str(Reg1) + "," + str(Reg2) + "\n" + mems[Condition] +",0,0,@"+str(Location)
        return_stm = "CMP ,"+str(Reg1) + "," + str(Reg2) + "\n"
        return_stm += "JME ,0,0,@NE"+str(Location) + "\nJMP,0,0,@"+str(Location) + "\n@NE"+str(Location)
        return return_stm
    
    def Load_From_Memory(Source_Reg,Dest_Reg,Offset = 0):
        return "LDA ,"+str(Source_Reg) + "," + str(Dest_Reg) + "," + str(Offset)
    
    def Store_To_Memory(Source_Reg,Dest_Reg,Offset = 0):
        return "STR ,"+str(Source_Reg) + "," + str(Dest_Reg) + "," + str(Offset)
    
    def Load_Constent(Dest_Reg,Constent):
        if (type(Constent) == int):
            return "INC ,0,"+str(Dest_Reg) + "," + str(Constent)
        return "INC ,0,"+str(Dest_Reg) + ","+Constent
    
    def INC(Dest_Reg,Amount):
        return "INC ,"+str(Dest_Reg) + "," + str(Dest_Reg) + "," + str(Amount)
    
    def DEC(Dest_Reg,Amount):
        return "INC ,"+str(Dest_Reg) + "," + str(Dest_Reg) + "," + str(Amount)
    
if __name__ == "__main__":
    
    ar = assembly_r
    print(ar.Call("Print"))
    print(ar.Load_From_Memory(1,5))
    print(ar.Store_To_Memory(5,1))

        