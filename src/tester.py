from sys import argv

from assembler import Assembler

compiled_file = open("/home/victor/python/assembler/bin/exemplo.bin", "rb")
assembly_file = open("/home/victor/python/assembler/asm/exemplo.asm", "r")

compiled_program = compiled_file.read()
assembly_program = assembly_file.read()

nInst = len(compiled_program)//4

asm = Assembler()
program = asm.assemble_program(assembly_program)

p = assembly_program.split('\n')

print("instruction                   compiled_code       our_assembler\n")
for i in range(nInst):
	inst = int.from_bytes(compiled_program[i*4:i*4+4], byteorder='little')
	print(f"{p[i]}{' '*(30-len(p[i]))}", end="")
	print(f"{hex(inst)}{' '*(20-len(hex(inst)))}{hex(program[i])}")