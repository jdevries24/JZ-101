//this is a c file to demostrate the compiler. the resultent assembly program is Example_assembly.s

int global_var_a = 5; //global_varibles are suported as long as they are int type
int global_var_b = 10;
int slow_message = "Hello and welcome to the JZ-101!\n"; //no type checking so this is a_ok!
int fast_message = "Isnt this so much faster then the previous message?"; //at compile time the string will compile down
//to a vector when ascsessed the first char will be what is returned 

struct link_list_node //well were declaring global vars lets show off that yes this supports structs
{
    int value;
    int next_node; //yes int type should be used for everything told you this thing was problematic
};

struct link_list
{
    int first_node;
    int last_node;
};

int for_multi(int x,int y)
{
    int a = 0; //local vars are suported
    for(int i = 0;i < y;i++) // quick note here for scope vars dont have special code and are just
    {                        //treated like a normal stack var. therefor nested fors will screw things up
        a = a + x; //arithmitic assignents might work untested
    }
    return a;
}

int recursion_multi(int x,int y) //good method for showing off how function calls work
{
    if(y) //so if a value is not zero it evaluates as true
    {
        return x + recursion_multi(x,y-1); //strickly speeking a uninary could be used here
    }
    else
    {
        return 0; //strictly speeking you could do without the else but I wanted to show off how this worked
    }
}

int malloc() // just wanted something for memory programs to call for the simulation
{
    return 0;
}

int new_link_list()
{
    int new_list = malloc(); //get a value from the allocator
    new_list->first_node = new_link_list_node(0); //so struct accsess is just sytax shuger for *(struct name + offset of struct var)
    new_list->last_node = new_list->last_node;
    return new_list;
}

int new_link_list_node(int node_value) //should note that struct vars are saved to the global scope so parm cannot be "value"
{
    int new_node = malloc();
    new_node->value = node_value; //node that due to no checking new_node->first_node is also posible
    new_node->next_node = 0; //null word isnt avilable
    return new_node;
}

int assembly_print(int message_pointer)
{
    //this method will print via writen assembly code
    //inline assembly is done by calling the asm method
    //each line of assembly is its own paramiter
    asm("LDA ,SP,2,1 #Load in the address of the message",
        "INC ,0,3,0xFFFF #Load in the address of the terminal",
        "@top_asm_print",
        "LDA ,2,1,0 #load in the next char",
        "CMP ,1,0, #test if the char is null",
        "JME ,0,0,@asm_print_end #Jump to end if null",
        "STR ,1,3,0 #store the car to the screen",
        "INC ,2,2,1 #increment the pointer",
        "JMP ,0,0,@top_asm_print #go back to the top",
        "@asm_print_end",
        "RTN");
}

int compiled_print(int message_pointer)
{   //this method here prints out a message but is compiled more details in the assembly file
    int term_addr = 0xffff; //create a value to act as our address point
    for(int i = 0;message_pointer[i];i++)
    {
        *term_addr = message_pointer[i];//and set it out to the array
    }
    return 0; //return will not be checked for or implicedly added for you!
}

int main()
{
    //the main method lets just have it call our two printing messages
    int string_pointer = &slow_message; //showing how the addr method works 
    compiled_print(string_pointer); //now we can pass it as a pointer
    assembly_print(&fast_message); //we could do it in the parm list. note that this is now a pass by refrance
    recursion_multi(global_var_b,global_var_a); // for showing off recursion multi
    for_multi(5,10);
    asm("HCF"); //and add one more assembly instruction to stop the processor so the thing dosn't run forever
}
        
        
    
        