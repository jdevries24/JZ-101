_LICENSE_
For the JZ-101 Design ISA and python assembler. not Licensed. don't expect this to set the world on fire
Logisim is under the GNU public license and you will need to download it sepratly. 

_Intro_
Congrats on your aquasiton of a new JZ-101 Microprocessor. This is a sixteen bit
Microprocessor that is based off of the desing Philosophy of 
RISC(Reduced instruction set computing). Insted of having meany instruction that
are done slowly this processor has a few instructions that It can do quickly.
This processor has been developed in logisim and If you are intrested in developing 
this processor in another platform(VHDL,Python,C,Real life) please contect me!

_Registers_and_architecture_overview_
This processor has 16 registers 13 of which are general purpose. The regesters
are numbered R0 to RF. Registers R1 thought RE can be used for general purpose.
Register R0 is a zero constent. It cannot be saved to and will alway return 0.
Register RE is the stack pointer. As the Call and return instructions use the 
value of the stack pointer for the return address no other register will do.
Register RF is the flag register. Some Aritmitic and the Comparison address effect this register.

The CPU starts out with all values at zero. The First Instruction called needs
To be a Call to the main Program. On inturupt the Processor will jump to the Value 0x2 so ones ISR will need to be programed first thing. The processor has 
only one non inturupt line. The Intupt hardwere is located outside of the device

The stack of the CPU grows downwords and should be inits to the value 0xFFEF.
The very top of the adress space 0xFFF0 to 0xFFFF is reserved for critical 
processor IO. 

_Instruction_set_
The instruction set of this processor is seperated into 3 types on instructions.
Loading and storing, Modifying, and control. Instructions have the parts the source register,the destination register and a poisible oprand. The source register is the reg number that a operation uses as a source. The Dest register is the reg number that a operation saves to. 

Each instruction word is seperated
into two parts bits 15-8 are the opcode. bits 7-4 are the source register. bits 3-0 are the destination register. If needed the next word is a oprand. Depending 
on the operation this could be a address or value. If the instruction is a loading 
or storing operation the Oprand is a signed 15 bit number. on Inc and Dec instructions
the Oprand is simply a unsinged interger and on Jumping and calling instructions
the Oprand is a simple address

for information on coding in JZ-101 Assembly see the Instruction set doc and the 
JZ-101 Assembly docs in the assembler folder

_The JC64_
Included in your JZ-101 is the JC64 Computer. It includes a keyboard a tellytype 
terminal,A inturupt handler,And 64kb of ram. To use the terminal simply store a 
ascii chariture to the adress 0xFFFF(its that easy). 
The keyboard is a buffer that stores all
the inputed chars as ascii charictures. to read the next char read from address 0xFFFE. To clear a char from the Quene simply write to the address 0xFFFE. 
With the inturupt handeler. Read address 0xFFFD to see what line has been raised. 
the mask register can be saved to 0xFFFC
