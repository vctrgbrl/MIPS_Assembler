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

shamt_instructions = ["SLL", "SRL"]
data_transfer_instructions = ["LW", "SW"]

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

line_adresses = {}

def to_bin( n, source_base, digits ):
    n = str(n)
    n = n.strip()
    if( n!='' ):
        b = bin(int(n, source_base))[2:]
        b = "0"*(digits-len(b)) + b
        return b
    else:
        return ''

# Esta função traduz cada linha de assembly do arquivo .asm
def translate( assembly, file_line ):
    assembly = assembly.strip()
    assembly = assembly.upper()
    assembly = assembly.replace(",", " ")

    # Para o caso de linhas endereçadas, como em "TESTE: OR $T3,$T1,$T2"
    line_address = ""
    if( assembly.find(":") != -1 ):
        assembly = assembly.split(":")
        line_address = assembly[0].strip().lower()

        line_adresses[ line_address ] = file_line 
        # Exemplo: line_adresses[ "TESTE" ] = linha da instrução

        assembly = assembly[1].strip()
    
    parts = assembly.split()
    instruction = parts[0].upper() # mips_dict opcodes estão em maiúsculo
    
    for i in range(1, len(parts)):
        parts[i] = parts[i].lower()

    ling_maq = ""

    # Concatena opcode
    opcode_digits = 6
    opcode = mips_dict[ instruction ][ "op" ]
    opcode = to_bin( opcode, 16, opcode_digits )
    ling_maq += opcode

    if( instruction in type_R_instructions ): # Tipo R
        # Pega conteúdo dos registradores e shamt (para SLL e SRL), 
        # passa para binário, e concatena à ling_maq
        rs_digits, rt_digits, rd_digits, shamt_digits, funct_digits = 5, 5, 5, 5, 6

        if( len(parts[1:])==3 ):
            if( instruction in shamt_instructions ): 
                # OP $rd $rs shamt
                rd, rs, shamt = parts[1], parts[2], parts[3]

                rs = reg_bank[ rs ]
                ling_maq += to_bin( rs, 10, rs_digits )

                ling_maq += "0"*rt_digits

            else: 
                # OP $rd $rs $rt
                rd, rs, rt = parts[1], parts[2], parts[3]

                rs = reg_bank[ rs ]
                ling_maq += to_bin( rs, 10, rs_digits )

                rt = reg_bank[ rt ]
                ling_maq += to_bin( rt, 10, rt_digits )

                rd = reg_bank[ rd ]
                ling_maq += to_bin( rd, 10, rd_digits )

                ling_maq += "0"*shamt_digits

        else: 
            # JR $rs
            rs = parts[1]
            rs = reg_bank[ rs ]
            ling_maq += to_bin( rs, 10, rs_digits )

            ling_maq += "0"*rt_digits
            ling_maq += "0"*rd_digits
            ling_maq += "0"*shamt_digits
                
        # Concatena functcode
        functcode = mips_dict[ instruction ][ "funct" ]
        functcode = to_bin( functcode, 16, funct_digits )
        ling_maq += functcode

    elif( instruction in type_I_instructions ): # Tipo I
        r_digits, Imm_or_A_digits = 5, 16

        if( instruction in data_transfer_instructions ):
            a = parts[2]
            a = a.replace("(", " ").replace(")", " ")
            a = a.split()

            if( instruction == "LW"):
                rd, Imm, rs = parts[1], a[0], a[1]

                rd = reg_bank[ rd ]
                rd = to_bin( rd, 10, r_digits )

                Imm = to_bin( Imm, 10, Imm_or_A_digits )

                rs = reg_bank[ rs ]
                rs = to_bin( rs, 10, r_digits )
                # ... to be continued ...
                
            elif( instruction == "SW"):
                rs, Imm, rt = parts[1], a[0], a[1]
                # ... to be continued ...

        else:
            rd, rs, Imm_or_A = parts[1], parts[2], parts[3]
            # ... to be continued ...

    elif( instruction in type_J_instructions ): # Tipo J
        Target_digits = 26
        target = parts[1]
        
        if( instruction == "JAL" ): # JAL line_address
            target = line_adresses[ target ]
        
        ling_maq += to_bin( target, 10, Target_digits )
    
    return ling_maq


## Tipo R
add = "ADD $V0, $ZERO, $AT"
#ADD = 000000 
#rd = $V0 = 00010
#rs = $ZERO = 00000
#rt = $AT = 00001
#shamt = 00000
#funct = 20 (base 16) = 100000
#=>00000000000000010001000000100000
#=>00000000000000010001000000100000 (Deu certo!)

jr = "JR $T0"
#JR = 000000
#rd = 00000
#rs = $T0 = 8 = 01000
#rt = 00000
#shamt = 00000
#funct = 8 (base 16) = 001000
#=>00000001000000000000000000001000
#=>00000001000000000000000000001000 (Deu certo!)

## Tipo J
j = "J 16"
#J = 000010
#target = 32 = 00000000000000000000100000
#=>00001000000000000000000000100000
#=>00001000000000000000000000010000 (Deu certo!)

print( translate(add, 1) )
print( translate(jr, 1) )
print( translate(j, 1) )

print( to_bin(" 5  ", 10, 6) )
#Problema: para números negativos não está retornando em complemento a 2
print( to_bin(" -5  ", 10, 6) ) 
