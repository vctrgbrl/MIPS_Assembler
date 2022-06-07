class Disassembler:
	def __init__(self) -> None:
		pass
		
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
			addr = machine_code & 0b000000_1111111111_1111111111_111111
			print(f"J: {opcode}, {addr}")