## Formato das Instruções
#| Tipo | Opcode | rs | rt | rd | shamt | funct |
#| ---- | ------ | -- | -- | -- | ----- | ----- |
#|  R   |   6    | 5  |  5 | 5  |   5   |   6   |
#|  I   |   6    | 5  |  5 |        16          |
#|  J   |   6    |         26                   |

mips_dict = {
    # Tipo R
    "ADD": {"op": "0", "funct": "20"}, 
    "AND": {"op": "0", "funct": "24"}, 
    "JR":  {"op": "0", "funct": "8" }, 
    "OR":  {"op": "0", "funct": "25"}, 
    "SLL": {"op": "0", "funct": "0" }, 
    "SRL": {"op": "0", "funct": "2" }, 
    "SUB": {"op": "0", "funct": "22"}, 

    # Tipo I
    "ADDI":{"op": "8", "funct": None}, 
    "BEQ": {"op": "4", "funct": None}, 
    "BNE": {"op": "5", "funct": None}, 
    "LW":  {"op": "23", "funct": None}, 
    "SW":  {"op": "2B", "funct": None}, 

    # Tipo J
    "J":   {"op": "2", "funct": None}, 
    "JAL": {"op": "3", "funct": None}   
}
type_R_instructions = ["ADD", "AND", "JR", "OR", "SLL", "SRL", "SUB"]
type_I_instructions = ["ADDI", "BEQ", "BNE", "LW", "SW"]
type_J_instructions = ["J", "JAL"]

reg_bank = {
    "$zero": 0,  #Armazena a constante 0 e n˜ao pode ser escrito
    "$at": 0,    #Assembler tempor´ario
    "$v0": 0, #Armazenar retorno de fun¸c˜ao e avalia¸c˜ao de express˜oes
    "$v1": 0, #Armazenar retorno de fun¸c˜ao e avalia¸c˜ao de express˜oes
    "$a0": 0, #Argumento de fun¸c˜ao
    "$a1": 0, #Argumento de fun¸c˜ao
    "$a2": 0, #Argumento de fun¸c˜ao 
    "$a3": 0, #Argumento de fun¸c˜ao 
    "$t0": 0, #Tempor´ario "$t1" #Tempor´ario
    "$t1": 0, #Tempor´ario
    "$t2": 0, #Tempor´ario
    "$t3": 0, #Tempor´ario
    "$t4": 0, #Tempor´ario
    "$t5": 0, #Tempor´ario
    "$t6": 0, #Tempor´ario
    "$t7": 0, #Tempor´ario
    "$s0": 0, #Tempor´ario salvo
    "$s1": 0, #Tempor´ario salvo
    "$s2": 0, #Tempor´ario salvo
    "$s3": 0, #Tempor´ario salvo
    "$s4": 0, #Tempor´ario salvo
    "$s5": 0, #Tempor´ario salvo
    "$s6": 0, #Tempor´ario salvo
    "$s7": 0, #Tempor´ario salvo
    "$t8": 0, #Tempor´ario
    "$t9": 0, #Tempor´ario
    "$k0": 0, #Reservado para o kernel do SO
    "$k1": 0, #Reservado para o kernel do SO
    "$gp": 0, #Global pointer
    "$sp": 0, #Stack pointer
    "$fp": 0, #Frame pointer
    "$ra": 0  #Return address
}

def hex_to_bin( h, digits ):
    h = h.strip()
    if( h!='' ):
        b = bin(int(h, 16))[2:]
        b = "0"*(digits-len(b)) + b
        return b
    else:
        return ''

def tokenize(assembly):
    assembly = assembly.strip()
    assembly = assembly.upper()
    assembly = assembly.replace(",", " ")
    parts = assembly.split()
    instruction = parts[0]

    ling_maq = ""

    # Concatena opcode
    opcode_digits = 6
    opcode = mips_dict[ instruction ][ "op" ]
    opcode = hex_to_bin( opcode, opcode_digits )
    ling_maq += opcode

    if( instruction in type_R_instructions ): # Tipo R
        # Pega conteúdo dos registradores e shamt (se houver), passa para binário e concatena a ling_maq
        # rs_digits, rt_digits, rd_digits, shamt_digits = 5, 5, 5, 5
        # ...

        # Concatena functcode
        funct_digits = 6
        functcode = mips_dict[ parts[0] ][ "funct" ]
        functcode = hex_to_bin( functcode, funct_digits )
        # ling_maq += functcode

    elif( instruction in type_I_instructions ): # Tipo I
        rs_digits, rt_digits, Imm_or_A_digits = 5, 5, 16
        rs, rt, Imm_or_A = parts[1].lower(), parts[2].lower(), parts[3].lower()

        rs = reg_bank[ rs ]
        ling_maq += hex_to_bin( rs, rs_digits )

        rt = reg_bank[ r ]
        ling_maq += hex_to_bin( rt, rt_digits )

        Imm_or_A = reg_bank[ Imm_or_A ]
        ling_maq += hex_to_bin( Imm_or_A, Imm_or_A_digits )

    elif( instruction in type_J_instructions ): # Tipo J
        Target_digits = 26

    return ling_maq
    

a = "ADD $V0, $ZERO, $AT"
print( tokenize(a) )
