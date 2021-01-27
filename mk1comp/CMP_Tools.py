class Symbol:
    #This Class is simply a data holder for each symbol

    def __init__(self,name,symbol_type,scope,value = 0):
        self.Symbol_name = name
        self.Symbol_type = symbol_type
        self.Symbol_scope = scope
        self.Symbol_value = value

class Symbol_table:
 #Insted of having the table be a list of symbols
 #this method will be used so that searching will be simpler

    def __init__(self):
        self.Symbols = {} #We will save the symbols as a dic
        #the keys will be the symbols names

    def Add(self,new_Symbol):
        """You are responcible for creating a new Symbol when done put in table"""
        self.Symbols.update({new_Symbol.Symbol_name:new_Symbol}) #add symbol and key by name

    def Search(self,name):
        """Search the table by symbol name"""
        if (name not in self.Symbols.keys()):
            raise IndexError(name + " not found")
        return self.Symbols[name]            
    
    def remove_scope(self,scope_name):
        clear_list = []
        for s in self.Symbols:
            if self.Symbols[s].Symbol_scope == scope_name:
                clear_list.append(s)
        for s in clear_list:
            self.Symbols.pop(s)
    
    def __iter__(self):
        for s in self.Symbols:
            yield self.Symbols[s]

class CMP_tools:
    
    def string_to_int_list(a_str):
        escape = False
        spc = {"n":"0x000A","b":"0x0008","f":"0x000C","\\":"0x005C"}
        accum = ""
        for chars in a_str[1:-1]: #strip away comments
            if not escape:
                if chars == "\\":
                    escape = True 
                    continue
                accum += "0x00" + hex(ord(chars))[2:] + ','
        if escape:
            if chars in spc.keys():
                accum += spc[chars] + ','
        return accum[:-1]
    
    def char_to_int(a_char):
        if char[0] == '\\':
            spc = {"n":"0x000A","b":"0x0008","f":"0x000C","\\":"0x005C"}
            return spc(char[1])
        return "00" + hex(ord(a_char)[0])

                                   
if __name__ == "__main__":
    
    def test_sym_table():
        
        st = Symbol_table()
        st.Add(Symbol("bar","function","extern",s_type = "double"))
        st.Add(Symbol("x","double","parameter",1))
        st.Add(Symbol("foo","function","global",s_type = "double"))
        st.Add(Symbol("count","int","parameter",1))
        st.Add(Symbol("sum","double","block",1))
        st.Add(Symbol("i","int","for-loop"))
        for s in st.Symbols:
            print_sym(st.Search(s))

    def print_sym(s):
        print("Name:  ",s.Symbol_name)
        print("Type:  ",s.Symbol_type)
        print("Scope: ",s.Symbol_scope)
        if (s.Symbol_value != 0):
            print("Value: ",s.Symbol_value)
        if (s.Symbol_s_type != None):
            print("S_type",s.Symbol_s_type)
        print("")

    def test_to_int_list():
        a_s = input("A string: ")
        print(CMP_tools.string_to_int_list(a_s))
               
    test_to_int_list()
           
    
    
        
         

        
