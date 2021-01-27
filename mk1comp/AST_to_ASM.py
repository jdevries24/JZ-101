from pycparser import c_parser,c_ast
from CMP_Tools import *
from ASM_Rout import *


class AST_to_ASM:

    def __init__(self):
        self.st = Symbol_table()
        self.stat_stack = []
        self.register_pointer = 1
        self.stackpointer_offset = 0
        self.con_flow_point = 0
        self.global_vars = ""
        self.func_name = ""
        self.asm = ""
        

    def v_FileAST(self,n):
        self.stat_stack.append("FileAST")
        for children in n:
            self.v_Node(children)
        self.asm += "#$\n" + self.global_vars + '\n'
        self.stat_stack.pop()

    def v_ArrayDecl(self,n):
        raise NotImplemented

    def v_ArrayRef(self,n):
        #print("ArrayRef")
        self.stat_stack.append("ArrayRef")
        self.register_pointer += 1
        if (n.subscript.__class__.__name__ == "Constant"):
            self.const_arrayRef(n)
            self.stat_stack.pop()
            self.register_pointer -= 1
            return
        base_point_reg = self.register_pointer
        self.v_Node(n.name) #calculate where our base is going to be
        self.register_pointer += 1 
        self.v_Node(n.subscript) #now get the subscript value
        self.asm += "ADD ,"+str(self.register_pointer) + ','  + str(self.register_pointer - 1) + '\n' #load the base and sub together
        self.register_pointer -= 2 #get the reg pointer down were it needs to go
        if (self.stat_stack[-2] == "Store"):
            self.asm += "STR ,"+str(self.register_pointer)+',' + str(self.register_pointer + 1)+',0\n' #save to reg if where loading
        else:
            self.asm += "LDA ,"+str(self.register_pointer + 1)+',' + str(self.register_pointer) + ',0\n'
        self.stat_stack.pop()
        
    def const_arrayRef(self,n):
        self.v_Node(n.name) #get the base
        if(self.stat_stack[-2] == "Store"):
            self.asm += "STR ,"+str(self.register_pointer - 1) + ',' + str(self.register_pointer) + ',' + n.subscript.value + '\n'
        else:
            self.asm += "LDA ,"+str(self.register_pointer) + "," + str(self.register_pointer - 1) + ','+ n.subscript.value + '\n'

    def v_Assignemnt(self,n):
        self.stat_stack.append("Assignment")
        self.v_Node(n.rvalue) #visit the right node to see whats up
        if (n.lvalue.__class__.__name__ == "ID"):
            self.assign_from_ID(n.lvalue)
            self.stat_stack.pop()
            return
        if (n.lvalue.__class__.__name__ == "UnaryOp"):
            self.assign_from_Unary(n.lvalue)
            self.stat_stack.pop()
            return
        if (n.lvalue.__class__.__name__ == "ArrayRef"):
            self.stat_stack.append("Store")
            self.v_ArrayRef(n.lvalue)
            self.stat_stack.pop()
            self.stat_stack.pop()
            return
        if (n.lvalue.__class__.__name__ == "StructRef"):
            self.stat_stack.append("Store")
            self.v_StructRef(n.lvalue)
            self.stat_stack.pop()
            self.stat_stack.pop()
            return
        raise NotImplemented
    
    def assign_from_ID(self,n):
        var = self.g_ID(n)
        #print(n.name)
        #print(var.Symbol_scope)
        #print(var.Symbol_value)
        if (var.Symbol_scope in ("Local","For")):
            self.asm += "STR ,"+str(self.register_pointer) + ',SP,' + str(self.stackpointer_offset - var.Symbol_value) + "\n"
            return
        
        if (var.Symbol_scope in ("Global")):
            self.asm += "INC ,0,"+str(self.register_pointer + 1) + ","+var.Symbol_value + "\n" #load in the symbol value
            self.asm += "STR ," + str(self.register_pointer) + ',' + str(self.register_pointer + 1) + ',0\n'
    
    def assign_from_Unary(self,n):
        if(n.op != "*"):
            raise NotImplemented
        self.register_pointer += 1; #we will need a ptr to store the ptr addr to
        self.v_Node(n.expr) #visit the next node to get a a expr
        self.asm += "STR," + str(self.register_pointer -1) + "," + str(self.register_pointer) + ",0\n" #and store the var to expr value
        self.register_pointer -= 1;
        
    
    def v_BinaryOp(self,n):
        #print("BinaryOp")
        self.stat_stack.append("BinaryOp")
        if (n.op in ("+","-","&&","||","^^")):
            self.v_Node(n.left)
            self.register_pointer += 1
            self.v_Node(n.right)
            self.asm += assembly_r.Arithmitic(n.op,self.register_pointer - 1,self.register_pointer) + "\n"
            self.asm += "MOV ,"+str(self.register_pointer) + "," + str(self.register_pointer -1) + "\n"
            self.register_pointer -= 1
        else:
            self.v_Node(n.left)
            self.register_pointer += 1
            self.v_Node(n.right)
            self.asm += "CMP ,"+str(self.register_pointer - 1) + "," + str(self.register_pointer) + "\n"
            self.asm += "MOV ,FR,"+str(self.register_pointer - 1) + "\n"
            self.register_pointer -= 1
        self.stat_stack.pop()
        

    def v_Break(self,n):
        raise NotImplemented

    def v_Case(self,n):
        raise NotImplemented

    def v_Cast(self,n):
        raise NotImplemented

    def v_Compound(self,n):
        #print("v_Compound")
        self.stat_stack.append("Compound")
        for children in n.block_items:
            self.v_Node(children)
        self.stat_stack.pop()

    def v_CompoundLiteral(self,n):
        raise NotImplemented

    def v_Constant(self,n):
        #print("v_Constant")
        self.stat_stack.append("Constant")
        if (n.value != "0"):
            self.asm += "INC ,0,"+str(self.register_pointer) + ',' + n.value + '\n'
        else:
            self.asm += "MOV ,0,"+str(self.register_pointer) + '\n' #save us a clock cycle
        self.stat_stack.pop()

    def v_Continue(self,n):
        raise NotImplemented

    def v_Decl(self,n):
        #print("v_Decl")
        self.stat_stack.append("Decl")
        if (n.type.__class__.__name__ == "FuncDecl"):
            self.v_FuncDecl(n.type)
            self.stat_stack.pop()
            return
        if (n.type.__class__.__name__ == "TypeDecl"):
            if("Compound" in self.stat_stack):
                self.stackpointer_offset += 1
                self.v_TypeDecl(n.type)
                self.asm += "DEC ,SP,SP,1\n" #declement the pointer after the grunt work is done
                if (n.init != None):
                    self.v_Node(n.init)
                self.asm += "STR ,"+ str(self.register_pointer) + ",SP,0\n" #store our fresh var onto the stack
            if(self.stat_stack[-2] == "FileAST"):
                self.v_TypeDecl(n.type)
                self.global_vars += "." + n.type.declname
                if (n.init != None):
                    if n.init.type == "string":
                        self.global_vars += ",[" + CMP_tools.string_to_int_list(n.init.value) + "]\n"
                    else:
                        self.global_vars += "," +n.init.value + '\n'
                else:
                    self.global_vars += ",0" + '\n'
            if("Struct" in self.stat_stack):
                self.v_TypeDecl(n.type)
        if (n.type.__class__.__name__ not in ("FuncDecl","TypeDecl")):
            self.v_Node(n.type)
            
        self.stat_stack.pop()            
                               
    def v_DecList(self,n):
        for items in n:
            self.v_Decl(items)

    def v_Default(self,n):
        raise NotImplemented

    def v_DoWhile(self,n):
        raise NotImplemented

    def v_EllipsisParam(self,n):
        raise NotImplemented

    def v_Enum(self,n):
        raise NotImplemented

    def v_Enumerator(self,n):
        raise NotImplemented

    def v_ExprList(self,n):
        #print("ExprList")
        if self.stat_stack[-1] == "FuncCall":
            self.stackpointer_offset += len(n.exprs) + 1
            self.asm += "DEC ,SP,SP,"+str(len(n.exprs) + 1) + "\n"
            for i in range(len(n.exprs)):
                self.v_Node(n.exprs[i])
                self.asm += "STR ,"+str(self.register_pointer) + ",SP,"+ str(i+1) + "\n"

    def v_For(self,n):
        #print("For")
        self.stat_stack.append("For")
        con_point = "_"+ self.func_name + "_" + str(self.con_flow_point)
        self.v_Node(n.init) #build the lood
        self.asm += "@TOP"+con_point + "\n"
        self.Bool_Op(n.cond) #lookinto wether we good
        self.con_flow_point += 1 #maybe non lat flow in loop
        self.asm += "@EQ" + con_point + "\n" #may need to jump over a other jump
        self.v_Node(n.stmt) #run all the statements
        self.v_Node(n.next) #and inc our loop
        self.asm += "JMP ,0,0,@TOP"+con_point + '\n' #jump back up to top of loop
        self.asm += "@NE" + con_point + "\n" #exit point for the for loop
        self.stat_stack.pop()
        
        
            

    def v_FuncCall(self,n):
        self.stat_stack.append("FuncCall")
        #print("FuncCall")
        if (n.name.name != "asm"):
            self.save_regs()
            if (n.args != None):
                self.v_ExprList(n.args)
            self.asm += "CAL ,0,0,@" + n.name.name + "\n"
            self.asm += "LDA ,SP,"+str(self.register_pointer) + ",1" + "\n"
            if (n.args != None):
                self.stackpointer_offset -= len(n.args.exprs) + 1
                self.asm += "INC ,SP,SP," + str(len(n.args.exprs) + 1) + '\n' #decress the stack pointer away from parm passing
            self.load_regs()
        else:
            for lines in (n.args.exprs):
                self.asm += lines.value[1:-1] + "\n"
        self.stat_stack.pop()

    def v_FuncDecl(self,n):
        #print("FuncDecl")
        self.stat_stack.append("FuncDecl")
        Func_name = n.type.declname
        Func_return_type = n.type.type.names[0]
        self.func_name = n.type.declname
        self.st.Add(Symbol(Func_name,["Function",Func_return_type],"Global"))
        if (n.args != None):
            self.v_ParmList(n.args)
        self.stat_stack.pop()
        
    def v_FuncDef(self,n):
        #print("FuncDef")
        self.stat_stack.append("FuncDef")
        self.v_Decl(n.decl)
        self.asm += "\n@" + self.func_name + "\n"
        self.v_Compound(n.body)
        for s in []:
            print(s.Symbol_name)
            print(s.Symbol_scope)
            print(s.Symbol_type)
            print(s.Symbol_value,"\n")
        self.st.remove_scope("Parm")
        self.st.remove_scope("Local")
        self.st.remove_scope("For")
        self.stackpointer_offset = 0
        self.con_flow_point = 0
        self.register_pointer = 1
        self.stat_stack.pop()

    def v_Goto(self,n):
        raise NotImplemented("Why?")

    def g_ID(self,n):
        #print("ID")
        self.stat_stack.append("ID")
        var = self.st.Search(n.name)            
        self.stat_stack.pop()
        return var
    
    def v_ID(self,n): 
        #so this method should be load ID but whatever
        var = self.st.Search(n.name)
        if (var.Symbol_scope == "Global"):
            #load it as a global var
            self.asm += "INC ,0,"+str(self.register_pointer + 1) + "," + var.Symbol_value + "\n"
            self.asm += "LDA ,"+str(self.register_pointer + 1) + "," + str(self.register_pointer) + ",0\n"
            return
        #otherwise just get it from the stack
        if (var.Symbol_scope == "Parm"):
            offset = self.stackpointer_offset + 1 + var.Symbol_value
        else:
            offset = self.stackpointer_offset - var.Symbol_value
        self.asm += "LDA ,SP,"+str(self.register_pointer) +  ',' + str(offset) + "\n"
                

    def v_IdentifierType(self,n):
        raise NotImplemented

    def v_If(self,n):
        #print("IF")
        self.stat_stack.append("IF")
        pf_name = "_" + self.func_name + "_" + str(self.con_flow_point) #Save working copy of a con flow point
        self.Bool_Op(n.cond)
        self.con_flow_point += 1 #then up the conflow point 
        self.asm += "@EQ" + pf_name + "\n"
        self.v_Node(n.iftrue) #run the true code
        if (n.iffalse != None):
            self.asm += "JMP ,0,0,@END"+pf_name + "\n"
        self.asm += "@NE" + pf_name + "\n"
        if (n.iffalse != None):
            self.v_Node(n.iffalse)
        self.asm += "@END"+pf_name + "\n" #and the codes end point
        self.stat_stack.pop()

    def Bool_Op(self,n):
        #takes in the condition of a conflow and gens code for it
        pf_name = "_" + self.func_name + "_" + str(self.con_flow_point)
        if ((n.__class__.__name__ == "BinaryOp") and (n.op in ("<",">","==",">=","<=","==","!="))):
            self.v_BinaryOp(n)
            bool_coms = {">":"JMG","<":"JML","==":"JME","<=":"JML",">=":"JMG","!=":"JME"}
            if (n.op in (">","<","==")):
                self.asm += bool_coms[n.op] + ",0,0,@EQ" + pf_name + "\n"
                self.asm += "JMP ,0,0,@NE" + pf_name + "\n"
            if (n.op in (">=","=<","!=")):
                self.asm += bool_coms[n.op] + ",0,0,@NE" + pf_name + "\n"
        else:
            self.v_Node(n) #visit the node 
            self.asm += "CMP ,"+str(self.register_pointer) +",0\n" #compare self to status register
            self.asm += "JME ,0,0,@NE" + pf_name + "\n" #If zero skip the code and take a day off
    def v_InitList(self,n):
        raise NotImplemented

    def v_Label(self,n):
        raise NotImplemented

    def v_NameInitializer(self,n):
        raise NotImplemented

    def v_ParmList(self,n):
        #print("ParmList")
        self.stat_stack.append("ParmList")
        for children in n:
            self.v_TypeDecl(children.type)
            self.stackpointer_offset += 1
        self.stackpointer_offset = 0
        self.stat_stack.pop()

    def v_PtrDecl(self,n):
        raise NotImplemented

    def v_Return(self,n):
        #print("Return")
        self.stat_stack.append("Return")
        self.v_Node(n.expr)
        self.asm += "INC ,SP,SP," + str(self.stackpointer_offset) + "\n" #clober sp back to zero
        self.asm += "STR ,1,SP,1" + '\n' #store the return value to the stack -1
        self.asm += "RTN" + "\n" #and the return command
        self.stat_stack.pop()

    def v_Struct(self,n):
        self.stat_stack.append("Struct")
        ssp = int(self.stackpointer_offset)
        self.stackpointer_offset = 0
        for nodes in n.decls:
            self.v_Decl(nodes)
            self.stackpointer_offset += 1
        self.stackpointer_offset = ssp
        self.stat_stack.pop()
        

    def v_StructRef(self,n):
        self.stat_stack.append("StructRef")
        self.register_pointer += 1
        self.v_Node(n.name)
        offset_var = self.g_ID(n.field)
        if ("Store" not in self.stat_stack):
            self.asm += "LDA ,"+str(self.register_pointer) + ','+str(self.register_pointer - 1) + ',' + str(offset_var.Symbol_value) + '\n'
        else:
            self.asm += "LDA ,"+str(self.register_pointer - 1) + ','+str(self.register_pointer) + ',' + str(offset_var.Symbol_value) + '\n'
        self.register_pointer -= 1
        self.stat_stack.pop()
        

    def v_Switch(self,n):
        raise NotImplemented

    def v_TernaryOp(self,n):
        raise NotImplemented

    def v_TypeDecl(self,n):
        #print("TypeDecl")
        self.stat_stack.append("TypeDecl")
        if (n.type.__class__.__name__ == "IdentifierType"):
            dname = n.declname
            item_type = n.type.names
        if (n.type.__class__.__name__ == "Struct"):
            dname = n.declname
            item_type = ["Struct"]
        if ("Compound" in self.stat_stack):
            if ("For" in self.stat_stack):
                self.st.Add(Symbol(dname,item_type,"For",self.stackpointer_offset))
                self.stat_stack.pop()
                return
            self.st.Add(Symbol(dname,item_type,"Local",self.stackpointer_offset))
            self.stat_stack.pop()
            return
        if ("ParmList" in self.stat_stack):
            self.st.Add(Symbol(dname,item_type,"Parm",self.stackpointer_offset))
            self.stat_stack.pop()
            return
        if ("Struct" in self.stat_stack):
            self.st.Add(Symbol(dname,item_type,"Struct",self.stackpointer_offset))
            self.stat_stack.pop()
            return
        self.st.Add(Symbol(dname,item_type,"Global","."+ dname))
        self.stat_stack.pop()

    def v_Typedef(self,n):
        raise NotImplemented

    def v_Typename(self,n):
        raise NotImplemented

    def v_UnaryOp(self,n):
        self.stat_stack.append("UnaryOp")
        if (n.op == "*"):
            self.register_pointer += 1 #next reg over will be addr
            self.v_Node(n.expr) #do whatever we need to do
            self.asm += "LDA ,"+str(self.register_pointer) + ","+str(self.register_pointer - 1) + ",0\n"
            self.register_pointer -= 1
            self.stat_stack.pop()
            return
        if (n.op == "p++"):
            self.v_ID(n.expr) # get our var into a register
            self.asm += "INC ,"+ str(self.register_pointer) + ","  + str(self.register_pointer) + ",1\n" #and inc by one
            self.assign_from_ID(n.expr)
            self.stat_stack.pop()
            return
        if (n.op == "p--"):
            self.v_ID(n.expr)
            self.asm += "DEC ,"+str(self.register_pointer) + "," + str(self.register_pointer) + ",1\n"
            self.assign_from_ID(n.expr) # and writeback
            self.stat_stack.pop()
            return
        if (n.op == "&"):
            if (n.expr.__class__.__name__ != "ID"):
                raise NotImplemented
            var = self.g_ID(n.expr)
            if var.Symbol_scope in ("Global"):
                self.asm += "INC ,0,"+ str(self.register_pointer) + "," + str(var.Symbol_value) + '\n'
                self.stat_stack.pop()
                return
            if var.Sympol_scope in ("Parm"):
                self.asm += "INC ,SP,"+ str(self.register_pointer) + "," + str(var.Symbol_value + 1 + self.stackpointer_offset) + '\n'
                self.stat_stack.pop()
                return
            if var.Symbol_scope in ("For","Local"):
                self.asm += "INC ,SP," + str(self.register_pointer) + "," + str(self.stackpointer_offset - self.Symbol_value) + '\n'
                self.stat_stack.pop()
            raise NotImplemented

    def v_Union(self,n):
        raise NotImplemented

    def v_While(self,n):
        self.stat_stack.append("While")
        pos_str = "_" + self.func_name + "_" + str(self.con_flow_point)
        self.asm += "@Top" + pos_str + '\n'
        self.Bool_Op(n.cond) #Evaluate
        self.con_flow_point += 1
        self.asm += "@EQ" + pos_str + '\n'
        self.v_Node(n.stmt) #do stuff
        self.asm += "JMP ,0,0,@Top" + pos_str + "\n"
        self.asm += "@NE" + pos_str + '\n'
        self.stat_stack.pop()

    def v_Pragma(self,n):
        raise NotImplemented

    def v_Node(self,n):
            
        children_methods = {"ArrayDecl":self.v_ArrayDecl,"ArrayRef":self.v_ArrayRef,
                        "Assignment":self.v_Assignemnt,"BinaryOp":self.v_BinaryOp,
                        "Break":self.v_Break,"Case":self.v_Case,
                        "Cast":self.v_Cast,"Compound":self.v_Compound,
                        "CompoundLiteral":self.v_CompoundLiteral,"Constant":self.v_Constant,
                        "Continue":self.v_Continue,"Decl":self.v_Decl,
                        "DeclList":self.v_DecList,"Default":self.v_Default,
                        "DoWhile":self.v_DoWhile,"EllipsisParm":self.v_EllipsisParam,
                        "Enum":self.v_Enum,"Enumeratior":self.v_Enumerator,
                        "EnumeratorList":1,
                        "ExprList":self.v_ExprList,"For":self.v_For,
                        "FuncCall":self.v_FuncCall,"FuncDecl":self.v_FuncCall,
                        "FuncDecl":self.v_FuncDecl,"FuncDef":self.v_FuncDef,
                        "Goto":self.v_Goto,"ID":self.v_ID,
                        "IdentifierType":self.v_IdentifierType,"If":self.v_If,
                        "InitList":self.v_InitList,"Label":self.v_Label,
                        "NamedInitializer":self.v_NameInitializer,"ParmList":self.v_ParmList,
                        "PtrDecl":self.v_PtrDecl,"Return":self.v_Return,
                        "Struct":self.v_Struct,"StructRef":self.v_StructRef,
                        "Switch":self.v_Switch,"TernaryOp":self.v_TernaryOp,
                        "TypeDecl":self.v_TypeDecl,"Typedef":self.v_Typedef,
                        "Typename":self.v_Typename,"UnaryOp":self.v_UnaryOp,
                        "Union":self.v_Union,"While":self.v_While,
                        "Pragma":self.v_Pragma}
        type_name = n.__class__.__name__
        children_methods[type_name](n)
    
    def save_regs(self):
        if self.register_pointer == 0:
            return
        #this method is for use in function calls as the callee saves
        self.stackpointer_offset += (self.register_pointer - 1) #ofset the stack by as much as we need
        if (self.register_pointer - 1 == 0):
            return
        self.asm += "DEC ,SP,SP," + str(self.register_pointer -1) + "\n"
        for n in range(1,self.register_pointer):
            self.asm += "STR,"+str(n) + ",SP," + str(n-1) + "\n"
    
    def load_regs(self):
        #this method is for loading back registers after a clober
        if self.register_pointer == 0:
            return
        for n in range(1,self.register_pointer):
            self.asm += "LDA,SP," + str(n) + "," + str(n-1) + "\n"
        self.stackpointer_offset -= (self.register_pointer - 1)
        self.asm += "INC ,SP,SP," + str(self.register_pointer -1) + '\n'

if __name__ == "__main__":
    
    def main_test():
        p = c_parser.CParser()
        f = open("sc.c",'r')
        text = f.read()
        f.close()
        ast = p.parse(text,filename = "<none>")
        v = compiler()
        v.v_FileAST(ast)
        print(v.asm)
        f = open("test_asm.asm",'w')
        f.write(v.asm)
        f.close()
    
    def sec_tests():
        v = visitors()
        v.register_pointer = 5
        v.save_regs()
        v.load_regs()
        print(v.asm)
        

    main_test()
