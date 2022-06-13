from sys import argv

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
		"j"		: (0x2,),
		"jal"	: (0x3,)
	}

	r_set = {
		"add", "sub", "and", "or", "sll", "srl", "jr"
	}

	i_set = {
		"addi", "beq", "bne", "lw", "sw"
	}

	data_set = {
		"lw", "sw"
	}

	j_set = {
		"j", "jal"
	}

	tag_set = {
		"beq", "bne", "j", "jal"
	}
	
	def __init__(self):
		# creates a file
		self.looking_for_tags = {}
		self.defined_tags = {}
		self.line_number = 0
		self.machine_codes = []

	def assemble_r_type(self, inst: list) -> int:
		machine_code = 0x00000000
		machine_code |= self.instructions[inst[0]][0] << 26 # opcode
		machine_code |= self.instructions[inst[0]][1] # funct
		if inst[0] == 'jr':
			return machine_code | self.reg_bank[inst[1]] << 21 # rs
		machine_code |= self.reg_bank[inst[1]] << 11 # rd
		if inst[0] == 'sll' or inst[0] == 'srl':
			machine_code |= self.reg_bank[inst[2]] << 16 # rt
			return machine_code | ( (int(inst[3]) & 0b11111) << 6 )
		machine_code |= self.reg_bank[inst[3]] << 16 # rt
		machine_code |= self.reg_bank[inst[2]] << 21 # rs
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
		machine_code |= 0b11111111_111111111111_111111 & int(inst[1])
		return machine_code

	def preprocess_data_type(self, inst: list) -> int:
		num, reg = inst[2].split('(')
		inst[2] = reg[0:-1]
		inst.append(int(num))

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
				inst[len(inst)-1] -= self.line_number + 1
			elif opcode in self.data_set:
				self.preprocess_data_type(inst)
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
				tag = line_split[0][0:-1].lower()
				self.defined_tags[tag] = self.line_number
				self.solve_tag_dependency(tag)

			# TAG: opcode arg, arg, arg
			elif line_split[0].endswith(':'):
				tag = line_split[0][0:-1].lower()
				self.defined_tags[tag] = self.line_number

				sp = line_split[1].split(" ", 1)
				opcode = sp[0].lower()

				inst = sp[1].replace(' ', '').lower().split(',')
				inst.insert(0, opcode)
				machine_code = self.assemble_instruction(inst)
				self.machine_codes.append(machine_code)
				self.solve_tag_dependency(tag)

			# opcode arg, arg, arg
			elif line_split[0].lower() in self.instructions:
				inst = line_split[1].replace(' ','').lower().split(',')
				inst.insert(0, line_split[0].lower())
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

if __name__ == "__main__":
	fib_asm = open(argv[1]).read()

	assembler = Assembler()
	exe = assembler.assemble_program(fib_asm)
	
	file = open(argv[1][:-4] + ".bin", 'xb')
	for i in exe:
		file.write(
			i.to_bytes(4, byteorder="little")
		)
	file.close()