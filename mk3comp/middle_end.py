class comp_error(Exception):
	
	def __init__(self,message):
		self.message = message
		
from pycparser import c_parser,c_ast

class middle_end:
	
	def __init__(self,c_code):
		#This is the middle end of the compiler
		#It takes in proccesed c code and returns a
		#Assembly program
		c_pars = c_parser.CParser() #open up our c code then parse it
		self.AST = c_pars.parse(c_code)
		self.asm = "" #the assembly code of our program
		self.global_dec = '' #global varible declarations for the end of our code
		self.symbol_table = []
		self.asm = ""
		
	def run(self):
		#moves through the top level of the tree 
		for node in self.AST:
			#if we got a function we generate the code for it
			if node.__class__.__name__ == "FuncDef":
				code_gen = code_generator(list(self.symbol_table)) #make a new code generator
				self.asm += code_gen.run(node) + '\n' #and genate code from a function
			elif node.__class__.__name__ == "Decl":
				#otherwise we read the global varible declaration
				if node.type.__class__.__name__ == "TypeDecl":
					self.read_var(node)
				elif node.type.__class__.__name__ == "ArrayDecl":
					self.read_array(node)
				elif node.type.__class__.__name__ == "Struct":
					self.read_struct(node)
		return self.asm + "#$global_vars\n" + self.global_dec + '\n'
				
	def read_var(self,n):
		#method for reading a global var into the symbol table
		var_name = n.name
		self.symbol_table.append([n.name,"." + n.name,"globe","globe"])
		if n.init != None:
			if n.init.__class__.__name__ == "Constant":
				init_value = n.init.value
			else:
				raise NotImplemented() 
		else:
			init_value = "0"
		self.global_dec += "." + var_name + "," + init_value + "\n"
		
	def read_array(self,n):
		#method for reading a array into the symbol table
		var_name = n.name
		self.symbol_table.append([n.name,"." + n.name,"globe","globe"])
		if (n.type.dim != None):
			num_of_vars = int(n.type.dim.value) #assume dim is a const value
		else:
			num_of_vars = 0
		init_vals = 0
		init_value = ""
		if n.init != None:
			if n.init.__class__.__name__ == "InitList":
				for node in n.init.exprs:
					init_value += node.value + ','
					init_vals += 1
				for i in range(num_of_vars - init_vals):
					init_value += '0' + ','
			if n.init.__class__.__name__ == "Constant":
				if n.init.type == "string":
					init_value = self.string_to_int_list(n.init.value) + ','
				else:
					init_value = n.init.value
					for i in range(num_of_vars - 1):
						init_value += '0' + ','		
		self.global_dec += "." + var_name + ',' + init_value[:-1] + '\n'
		
	def string_to_int_list(self,a_str):
		escape = False
		spc = {"n":"0x000A","b":"0x0008","f":"0x000C","\\":"0x005C"}
		accum = ""
		for chars in a_str[1:-1]: #strip away comments
			if not escape:
				 if chars == "\\":
					  escape = True 
					  continue
				 accum += "0x" + hex(ord(chars))[2:] + ','
		if escape:
			if chars in spc.keys():
				 accum += spc[chars] + ','
		return accum + "00"
		
	def read_struct(self,n):
		#method for reading a table into the symbol table
		struct_offset = 0
		for decs in n.type.decls:
			if decs.type.__class__.__name__ != "ArrayDecl":
				self.symbol_table.append([decs.name,struct_offset,"globe","globe"])
				struct_offset += 1
			else:
				self.symbol_table.append([decs.name,stuct_offset,"globe","globe"])
				struct_offset += int(decl.type.dim.value)
				

class code_generator:

	def __init__(self,s_t):
		self.t_stat_stack = []
		#The symbol table stores the Name,value,scope,storage
		self.symbol_table = s_t #for looking up locations 
		self.register_pointer = 1
		self.sp_offset = 0 #stores how out of line the sp is
		self.stack_top = 0 #stores how much local vars there are
		self.int_var = 0 #
		self.con_flow_point = 0
		self.func_name = ""
		self.asm = ""
		
	def run(self,ctree):
		#this program reads a function and is where the program 
		#is converted from a syntax tree to a assembly program
		#the program starts out by counting the number of varibles
		#in the function and moving the stack pointer. 
		#then the program moves down the stack recursivly generating code
		
		self.v_FuncDef(ctree)
		return self.asm #then return the resultent asembly code

	def search_st(self,name):
		#Method for searching the symbol table 
		for item in self.symbol_table:
			if item[0] == name:
				return item
		raise IndexError("no symbol " + name)
	
	def v_ArrayDecl(self,n):
		#Not going to implemnt arrays in a function. 
		#Will need to build pointers for arrays
		#srsly not writing code for one to thow a array onto the stack
		 raise NotImplemented()

	def v_Assignemnt(self,n):
		#so assignments are quite easy just do the right side of the assignmetn that will 
		#store it in a regester then do math if need be then store it back. 
		if n.op == "=":
			#if the op is simply = then its just do the operation then 
			#store it 
			self.v_Node(n.rvalue)
			self.Store(n.lvalue)
			return
		else:
			self.v_Node(n.lvalue) #store in our var into the first register
			self.register_pointer += 1
			self.v_Node(n.rvalue) #then find what the right side is
			self.register_pointer -= 1
			v_reg = str(self.register_pointer + 1)
			save_reg = str(self.register_pointer)
			oplookup = {"+=":"ADD","-=":"SUB"}
			self.asm += oplookup[n.op] + ',' + v_reg + ',' + save_reg + '\n'
			self.Store(n.lvalue) #then we can store back
		
	def Store(self,n):
		#So storeing a value takes diffrent code then loading it
		#so these methods call the node visitors with the caviate that they
		#store rather then load
		if n.__class__.__name__ == "ID":
			self.v_ID(n,True)
			return
		if n.__class__.__name__ == "UnaryOp":
			self.v_UnaryOp(n,True)
			return
		if n.__class__.__name__ == "ArrayRef":
			self.v_ArrayRef(n,True)
			return
		if n.__class__.__name__ == "StructRef":
			self.v_StructRef(n,True)
			return
		
	
	def v_ID(self,n,Store = False):
		#Each ID has a value associated with it
		#For stack varibles that amount is the vars distence
		#From the stack Top for global vars it is the pointer
		#to its location in global memory
		var = self.search_st(n.name)
		value = str(self.register_pointer)
		if var[3] == "stack":
			offset = str(self.sp_offset + var[1])
			address = "SP"
		if var[3] == "globe": 
			#If we got a global var then the address we are loading and storing from is 
			#the pointer to a address
			offset = '0'
			address = str(self.register_pointer + 1)
			self.asm += "INC ,0,"+address+","+ var[1] + '\n'
		if var[3] == "register":
			address = str(var[1])
			if not Store:
				self.asm += "MOV ,"+ address + "," + value + '\n'
			else:
				self.asm += "MOV ,"+ value + "," + address +'\n'
			return
		if Store:
			self.asm += "STR ,"+ value + "," + address + ',' + offset + '\n'
		else:
			self.asm += "LDA ,"+ address + "," + value + ',' + offset + '\n'
					
	
	def v_ArrayRef(self,n,store = False):
		# A array refrence is a[x] but this is just syntax shurger for
		#*(a + x) so just do that
		add_node = c_ast.BinaryOp("+",n.name,n.subscript)
		ptr_node = c_ast.UnaryOp(op = '*',expr = add_node)
		self.v_UnaryOp(ptr_node,store)
			
	def v_StructRef(self,n,Store = False):
		#Structs are in the same boat as arrays but the x value is a constent
		#that is the offset of the top of the struct so that is the value we should use
		off_var = n.field.name
		off_var = self.search_st(off_var)
		offset = str(off_var[1])
		self.register_pointer += 1
		self.v_Node(n.name)
		self.register_pointer -= 1
		address = str(self.register_pointer + 1)
		value = str(self.register_pointer)
		if Store:
			self.asm += "STR ,"+value+","+address+","+offset + '\n'
		else:
			self.asm += "LDA ,"+address+","+value+","+offset + '\n'
		
	def v_UnaryOp(self,n,Store = False,offset = 0):
		value = str(self.register_pointer)
		if (n.op == "*"): #yes this is cheating this allows one to load and
			#store to a memory address
			self.register_pointer += 1
			offset = str(offset)
			self.v_Node(n.expr)
			self.register_pointer -= 1
			address = str(self.register_pointer + 1)
			if Store:
				self.asm += "STR ,"+value+","+address+","+offset + '\n'
			else:
				self.asm += "LDA ,"+address+","+value+","+offset + '\n'
		if (n.op == "p++"):
			self.v_Node(n.expr)
			self.asm += "INC ,"+value+','+value+',1\n'
			if n.expr.__class__.__name__ == "ID":
				self.v_ID(n.expr,True)#if ID save back
		if n.op == "p--":
			self.v_Node(n.expr)
			self.asm += "DEC ,"+value+','+value+',1\n'
			if n.expr.__class__.__name__ == "ID":
				self.v_ID(n.expr,True)
		if n.op == "&":
			name = n.expr.name
			var = self.search_st(name)
			if var[3] == "stack": #Calculates the value of op and throws it back
				offset = str(self.sp_offset+ var[1])
				self.asm += "INC ,SP,"+value+','+offset+'\n'
			if var[3] == "globe":
				self.asm += "INC ,0,"+value+","+var[1] + '\n'
				
	
	def v_BinaryOp(self,n):
		#This method finds what the left value is then the right value then exucutes a binary op ins
		if (n.op in ("+","-","&&","||","^^")):
			op_look = {"+":"ADD","-":"SUB","&&":"AND","||":"ORR","^^":"XOR"}
			self.v_Node(n.left)
			self.register_pointer += 1
			self.v_Node(n.right)
			self.asm += op_look[n.op] + ',' + str(self.register_pointer - 1) +',' + str(self.register_pointer) + "\n"
			self.asm += "MOV ,"+str(self.register_pointer) + "," + str(self.register_pointer -1) + "\n"
			self.register_pointer -= 1
		else: #if not in the typical bin ops assums its a comparison ins
			self.v_Node(n.left)
			self.register_pointer += 1
			self.v_Node(n.right)
			self.asm += "CMP ,"+str(self.register_pointer - 1) + "," + str(self.register_pointer) + "\n"
			self.asm += "MOV ,FR,"+str(self.register_pointer - 1) + "\n"
			self.register_pointer -= 1        

	def v_Break(self,n):
		raise NotImplemented

	def v_Case(self,n):
		raise NotImplemented

	def v_Cast(self,n):
		raise NotImplemented

	def v_Compound(self,n):
		#Compound is just a list of insturctions so run through it
		for children in n.block_items:
			self.v_Node(children)

	def v_CompoundLiteral(self,n):
		raise NotImplemented

	def v_Constant(self,n):
		#load a value into the register that we need to 
		if (n.value != "0"):
			self.asm += "INC ,0,"+str(self.register_pointer) + ',' + n.value + '\n'
		else:
			self.asm += "MOV ,0,"+str(self.register_pointer) + '\n' #save us a clock cycle

	def v_Continue(self,n):
		raise NotImplemented()

	def v_Decl(self,n):
		#if visited in stack then its safe to say that we have a local var
		var_name = n.name
		if len(n.storage) != 0:
			var_storage = n.storage[0]
		else:
			var_storage = None
		if var_storage == None:
			self.symbol_table.append([var_name,#store a var to the stack with the offset of whatever number of vars we alredy loaded
											  self.int_var,
											  "local",
											  "stack"])
			self.int_var += 1 
		elif var_storage.lower() == "register":
			self.symbol_table.append([var_name,
											  self.register_pointer,
											  "local",
											  "register"])
			self.register_pointer += 1
		if n.init != None:
			#a intiliser is = to imediatly assign so just do a assignment
			assi = c_ast.Assignment('=',c_ast.ID(var_name),n.init)
			self.t_stat_stack.append("Assignment")
			self.v_Assignemnt(assi)
			self.t_stat_stack.pop()
		
								
	def v_DecList(self,n):
		for items in n:
			self.v_Decl(items)

	def v_Default(self,n):
		raise NotImplemented()

	def v_DoWhile(self,n):
		raise NotImplemented()

	def v_EllipsisParam(self,n):
		raise NotImplemented()

	def v_Enum(self,n):
		raise NotImplemented()

	def v_Enumerator(self,n):
		raise NotImplemented()

	def v_For(self,n):
		#Set where our control point is then run the comparisons 
		#then run the next code
		con_point = "_" + self.func_name + "_" + str(self.con_flow_point)
		self.v_Node(n.init)
		self.asm += "@Top" + con_point + '\n'
		self.Bool_Op(n.cond)
		self.con_flow_point += 1
		self.asm += "@EQ" + con_point + '\n'
		self.v_Node(n.stmt)
		self.v_Node(n.next)
		self.asm += "JMP ,0,0,@Top" + con_point + '\n'
		self.asm += "@END"+con_point + "\n@NE" + con_point + '\n'

	def v_FuncCall(self,n):
		#this method is complex it needs to save all the registers currently at use onto the stack
		#then it needs to load the parameters onto the stack 
		#then call the function and load its return value into the next register
		if (n.name.name != "asm"):
			clobberd_regs = self.register_pointer - 1 # rp - 1 is number of registers curently in use
			if (n.args) != None:
				args_amount = len(n.args.exprs) 
			else:
				args_amount = 1 #we need one location of one for returning values
			self.asm += "DEC ,SP,SP,"+str(clobberd_regs + args_amount + 1) + '\n' #offset the stack by the number of save points we need
			self.sp_offset += clobberd_regs + args_amount + 1
			self.save_regs(clobberd_regs,args_amount)
			if (n.args != None):
				self.v_ExprList(n.args)
			self.asm += "CAL ,0,0,@"+n.name.name + '\n' #Call the function
			self.asm += "LDA ,SP,"+str(self.register_pointer) + ",1\n" #then store the result in the next avalible register
			self.load_regs(clobberd_regs,args_amount)
			self.asm += "INC ,SP,SP, "+str(clobberd_regs + args_amount + 1) + '\n'
			self.sp_offset -= clobberd_regs + args_amount + 1
		else:
			for lines in n.args.exprs:
				self.asm += lines.value[1:-1] + '\n'
		
				
	def v_ExprList(self,n):
		#load in our expresions for a function call 
		exp_num = 1
		for exp in n.exprs:
			self.v_Node(exp)
			self.asm += "STR ,"+str(self.register_pointer) + ",SP,"+str(exp_num) + '\n'
			exp_num += 1

	def save_regs(self,clob_regs,args_ammount):
		for i in range(1,clob_regs + 1):
			self.asm += "STR ,"+str(i) + ",SP," + str(args_ammount + i) + '\n' #store our clobberd regs just beyond where are args go
	
	def load_regs(self,clob_regs,args_ammount):
		for i in range(1,clob_regs + 1):
			self.asm += "LDA ,SP,"+str(i) + "," + str(args_ammount + i) + '\n'
		
	def v_FuncDecl(self,n):
		#this is assemble func compound
		raise NotImplemented()
		
	def v_FuncDef(self,n):
		#fist read howmeany vars we have and inc the SP by that amount
		#THen read in the offset of our paramiters
		#then read the function before decmenting our sp and returning
		self.func_name = n.decl.name #read our function name
		#then count how mean varible declarations are in the program
		self.stack_top = self.CLV(n.body)
		self.sp_offset = 0
		self.register_pointer = 1
		if (n.decl.type.args != None):
			self.v_Node(n.decl.type.args,"ParamList") #store our paramiters 
		self.sp_offset = 0
		self.asm += "@" + self.func_name +'\n'#add name of function
		if self.stack_top != 0:
			self.asm += "DEC ,SP,SP,"+str(self.stack_top) + "\n"
		self.v_Node(n.body,"Compound")
		if self.stack_top != 0:
			self.asm += "INC ,SP,SP,"+str(self.stack_top) + '\n'
		self.asm += "RTN" + '\n'
		
		
	def CLV(self,n,decl_count = 0):
		#count the local vars in our function
		for node in n:
			if node.__class__.__name__ == "Decl":
				decl_count += 1
			decl_count = self.CLV(node,decl_count)
		return decl_count
		
		
	def v_Goto(self,n):
		self.asm += "JMP ,0,0,@" + n.name + '\n'

	def v_IdentifierType(self,n):
		raise NotImplemented()

	def v_If(self,n):
		#sets up the address flow of a if else statemnts 
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

	def Bool_Op(self,n):
		#While,For,If all need to set up the control flow points for there
		#blocks rather than each class doing this work just have one class
		#write the compare jump statemnts
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
		self.asm += "@" + n.name+"\n"
		
	def v_NameInitializer(self,n):
		raise NotImplemented

	def v_ParmList(self,n):
		#Loads the parameters and there offset into the symbol table
		parm_num = 1 + self.stack_top #track where each peramiter offset 
		#above local vars and the return address
		for nodes in n:
			#so parms are past all the local vars and return adress
			#loc in in sequental order
			parm_name = nodes.name
			self.symbol_table.append([parm_name,parm_num,"parm","stack"])
			parm_num += 1
						
         
	def v_PtrDecl(self,n):
		raise NotImplemented()

	def v_Return(self,n):
		#Exacutes a statement then moves the result of the statement onto the
		#stack return point 
		if n.expr == None:
			self.asm += "MOV ,0,"+str(self.register_pointer) + '\n'
		else:
			self.v_Node(n.expr)
		if self.stack_top > 0:
			self.asm += "INC ,SP,SP," + str(self.stack_top) + "\n" #clober sp back to zero
		self.asm += "STR ,"+str(self.register_pointer) + ",SP,1" + '\n' #store the return value to the stack -1
		self.asm += "RTN" + "\n" #and the return command

	def v_Struct(self,n):
		raise NotImplemented()
		
	def v_Switch(self,n):
		raise NotImplemented()

	def v_TernaryOp(self,n):
		raise NotImplemented()

	def v_TypeDecl(self,n):
		raise NotImplemented()

	def v_Typedef(self,n):
		raise NotImplemented()

	def v_Typename(self,n):
		raise NotImplemented()

	def v_Union(self,n):
		raise NotImplemented()

	def v_While(self,n):
		pos_str = "_" + self.func_name + "_" + str(self.con_flow_point)
		self.asm += "@Top" + pos_str + '\n'
		self.Bool_Op(n.cond) #Evaluate
		self.con_flow_point += 1
		self.asm += "@EQ" + pos_str + '\n'
		self.v_Node(n.stmt) #do stuff
		self.asm += "JMP ,0,0,@Top" + pos_str + "\n"
		self.asm += "@NE" + pos_str + '\n'

	def v_Pragma(self,n):
		raise NotImplemented

	def v_Node(self,n,expected_name = None):
		#send_all_nodes_through_here
		#for finding and exucuting a node of unknown type
			
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
						"NamedInitializer":self.v_NameInitializer,"ParamList":self.v_ParmList,
						"PtrDecl":self.v_PtrDecl,"Return":self.v_Return,
						"Struct":self.v_Struct,"StructRef":self.v_StructRef,
						"Switch":self.v_Switch,"TernaryOp":self.v_TernaryOp,
						"TypeDecl":self.v_TypeDecl,"Typedef":self.v_Typedef,
						"Typename":self.v_Typename,"UnaryOp":self.v_UnaryOp,
						"Union":self.v_Union,"While":self.v_While,
						"Pragma":self.v_Pragma}
		
		type_name = n.__class__.__name__
		self.t_stat_stack.append(type_name)
		#print(self.t_stat_stack)
		if(expected_name != None) and (type_name != expected_name):
			raise TypeError("expecting:" + expected_name + " got " + type_name)
		children_methods[type_name](n)
		self.t_stat_stack.pop()
