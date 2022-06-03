class Assembler:

	reg_bank = {
		"$zero": 0, #Armazena a constante 0 e não pode ser escrito
		"$at": 1,   #Assembler Temporário
		"$v0": 2,   #Armazenar retorno de função e avaliação de expressões
		"$v1": 3,   #Armazenar retorno de função e avaliação de expressões
		"$a0": 4,   #Argumento de função
		"$a1": 5,   #Argumento de função
		"$a2": 6,   #Argumento de função 
		"$a3": 7,   #Argumento de função 
		"$t0": 8,   #Temporário
		"$t1": 9,   #Temporário
		"$t2": 10,  #Temporário
		"$t3": 11,  #Temporário
		"$t4": 12,  #Temporário
		"$t5": 13,  #Temporário
		"$t6": 14,  #Temporário
		"$t7": 15,  #Temporário
		"$s0": 16,  #Temporário salvo
		"$s1": 17,  #Temporário salvo
		"$s2": 18,  #Temporário salvo
		"$s3": 19,  #Temporário salvo
		"$s4": 20,  #Temporário salvo
		"$s5": 21,  #Temporário salvo
		"$s6": 22,  #Temporário salvo
		"$s7": 23,  #Temporário salvo
		"$t8": 24,  #Temporário
		"$t9": 25,  #Temporário
		"$k0": 26,  #Reservado para o kernel do SO
		"$k1": 27,  #Reservado para o kernel do SO
		"$gp": 28,  #Global pointer
		"$sp": 29,  #Stack pointer
		"$fp": 30,  #Frame pointer
		"$ra": 31   #Return address
	}

	instructions = {
		"add"	: (0x00, 0x20),
		"sub"	: (0x00, 0x22),
		"and"	: (0x00, 0x24),
		"or"	: (0x00, 0x25),
		"sll"	: (0x00, 0x00),
		"srl"	: (0x00, 0x02),
		"jr"	: (0x00, 0x08),
		"addi"	: (0x08,),
		"beq"	: (0x04,),
		"bne"	: (0x05,),
		"lw"	: (0x23,),
		"sw"	: (0x2B,),
		"j"		: (0x2,)
	}

	r_set = {
		"add", "sub", "and", "or", "sll", "srl", "jr"
	}

	i_set = {
		"addi", "beq", "bne", "lw", "sw"
	}

	j_set = {
		"j"
	}

	tag_set = {
		"beq", "bne", "j"
	}
	
	def __init__(self):
		# creates a file
		self.looking_for_tags = {}
		self.defined_tags = {}
		self.line_number = 0
		self.machine_codes = []

	def assemble_r_type(self, inst: list) -> int:
		machine_code = 0x00000000
		if inst[0] == 'jr':
			return machine_code | self.reg_bank[inst[1]] << 20 # rs
		machine_code |= self.reg_bank[inst[2]] << 20 # rs
		machine_code |= self.reg_bank[inst[1]] << 11 # rd
		machine_code |= self.reg_bank[inst[3]] << 16 # rt
		machine_code |= self.instructions[inst[0]][0] << 26 # opcode
		machine_code |= self.instructions[inst[0]][1] # funct
		return machine_code

	def assemble_i_type(self, inst: list) -> int:
		machine_code = 0x00000000
		machine_code |= self.instructions[inst[0]][0] << 26 # opcode
		machine_code |= self.reg_bank[inst[1]] << 16 # rt
		machine_code |= self.reg_bank[inst[2]] << 21 # rs
		machine_code |= int(inst[3]) & 0xFFFF
		return machine_code

	def assemble_j_type(self, inst: list) -> int:
		machine_code = 0x00000000
		machine_code |= self.instructions[inst[0]][0] << 26
		machine_code |= 26 & int(inst[1])
		return machine_code

	def assemble_instruction(self, inst: list) -> int:
		machine_code = 0x00000000
		opcode = inst[0]
		uses_tag = False
		# Se opcode precisar de uma TAG e a TAG não for definida
		# então adicionamos toda a linha no dicionário de "a procura de TAGs"
		# Quando essa TAG for definida iremos chamar essa função novamente
		if opcode in Assembler.tag_set:
			tag = inst[len(inst)-1]
			if not tag in self.defined_tags:

				# Esse Código é necessário pois mais de uma instrução pode depender
				# da mesma TAG
				if tag in self.looking_for_tags:
					self.looking_for_tags[tag].append((inst, self.line_number))
				else:
					self.looking_for_tags[tag] = [(inst, self.line_number)]
				self.line_number += 1
				return machine_code
			uses_tag = True
			inst[len(inst)-1] = self.defined_tags[tag]

		if opcode in self.r_set:
			machine_code = self.assemble_r_type(inst)
		elif opcode in self.i_set:
			if uses_tag:
				inst[len(inst)-1] -= self.line_number
			machine_code = self.assemble_i_type(inst)
		elif opcode in self.j_set:
			machine_code = self.assemble_j_type(inst)

		self.line_number += 1
		return machine_code

	def assemble_program(self, program: str) -> list:
		program = program.replace('\t', '')
		lines = program.split('\n')
		machine_code = 0
		
		for line in lines:
			if line == '':
				continue
			line_split = line.split(" ", 1)

			# TAG:
			if line_split[0].endswith(':') and len(line_split) == 1:
				tag = line_split[0][0:-1]
				self.defined_tags[tag] = self.line_number
				self.solve_tag_dependency(tag)

			# TAG: opcode arg, arg, arg
			elif line_split[0].endswith(':'):
				tag = line_split[0][0:-1]
				self.defined_tags[tag] = self.line_number

				sp = line_split[1].split(" ", 1)
				opcode = sp[0].lower()

				inst = sp[1].replace(' ', '').split(',')
				inst.insert(0, opcode)
				machine_code = self.assemble_instruction(inst)
				self.machine_codes.append(machine_code)
				self.solve_tag_dependency(tag)

			# opcode arg, arg, arg
			elif line_split[0].lower() in self.instructions:
				inst = line_split[1].replace(' ','').split(',')
				inst.insert(0, line_split[0])
				machine_code = self.assemble_instruction(inst)
				self.machine_codes.append(machine_code)
			
		return self.machine_codes

	def solve_tag_dependency(self, tag: str) -> None:
		prev_line_number = self.line_number
		if tag in self.looking_for_tags:
				for inst, line_number in self.looking_for_tags[tag]:
					self.line_number = line_number
					machine_code = self.assemble_instruction(inst)
					self.machine_codes[self.line_number - 1] =  machine_code
		self.line_number = prev_line_number

	def print_machine_code(self, machine_code: int) -> None:

		opcode = (machine_code & 0b111111_00000_00000_00000_00000_000000) >> 26
		if opcode == 0:
			rs = 	(machine_code & 0b000000_11111_00000_00000_00000_000000) >> 21
			rt = 	(machine_code & 0b000000_00000_11111_00000_00000_000000) >> 16
			rd = 	(machine_code & 0b000000_00000_00000_11111_00000_000000) >> 11
			shamt =	(machine_code & 0b000000_00000_00000_00000_11111_000000) >> 6
			funct =	(machine_code & 0b000000_00000_00000_00000_00000_111111)
			print(f"R: {opcode}, {rs}, {rt}, {rd}, {funct}")
		elif opcode in {8,4,5,0x23,0x2B}:
			rs =	(machine_code & 0b000000_11111_00000_0000000000000000) >> 21
			rt =	(machine_code & 0b000000_00000_11111_0000000000000000) >> 16
			i =		(machine_code & 0b000000_00000_00000_1111111111111111)
			print(f"I: {opcode}, {rs}, {rt}, {i}")
		elif opcode == 2:
			addr = 0b000000_1111111111_1111111111_111111
			print(f"J: {opcode}, {addr}")

asm_1 = """
	addi $t0, $zero, 4
	addi $t1, $zero, 0
LOOP:
	addi $t0, $zero, 1
	bne $t0, $t1, LOOP
"""
# 8, 
asm_2 = """
	beq $t1, $t2, IF
	addi $t0, $t0, 1
	j EXIT
IF: addi $v0, $v0, 2
EXIT:
	jr $ra
"""
# 4, 10, 9, 2
# 8, 9, 0,  0
# 2, 3
# 8, 8, 0,  1
# 0, 2, 0, 0

assembler = Assembler()
exe = assembler.assemble_program(asm_2)
for e in exe:
	assembler.print_machine_code(e)