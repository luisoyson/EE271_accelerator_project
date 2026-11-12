from .instruction import InstructionConfiguration
from .instruction import ProcessingElementInstruction, MemoryInstruction, Instruction
from .instruction import PEI, MI, Mode

class Assembler:

    def __init__(
        self,
        inst_config : InstructionConfiguration,
    ):
        
        # Saving Configs
        self._inst_config = inst_config
        self._mem_config  = inst_config.MEMORY_INST_CONFIG
        self._pe_config   = inst_config.PE_INST_CONFIG

    def assemble_instructions(self, instructions : list[str]) -> list[Instruction]:
        return [self.convert_instruction(inst) for inst in instructions]

    def convert_instruction(self, inst_str : str) -> Instruction:

        # Creating the Instruction to Populate
        inst = Instruction(self._inst_config)

        # Parsing the Input
        params = inst_str.strip().upper().split('|')
        params = [elem.strip() for elem in params]
        
        if len(params) != 3:
            raise ValueError(f"Malformed Instruction: {inst_str}")

        # Parsing/Setting the Memory/PE Instructions
        mem_inst = self.convert_mem_instruction(params[0])
        pe_inst  = self.convert_pe_instruction(params[1])
        inst.set_mem_instruction(mem_inst)
        inst.set_pe_instruction(pe_inst)

        # Parsing the Controller Instruction
        params = params[2].strip().upper().split(' ')
        try:     value = int(params[0])
        except:  raise ValueError(f"Unable to Convert \"{params[0]}\" to Count.")
        inst.set_count(value-1)
        try:     value = int(params[1])
        except:  raise ValueError(f"Unable to Convert \"{params[1]}\" to MEMA Increment.")
        inst.set_mema_inc(value)
        try:     value = int(params[2])
        except:  raise ValueError(f"Unable to Convert \"{params[2]}\" to MEMB Increment.")
        inst.set_memb_inc(value)
        return inst        


    def convert_mem_instruction(self, mem_inst_str : str) -> MemoryInstruction:

        # Creating the Instruction to Populate
        inst = MemoryInstruction(self._mem_config)

        # Parsing the Input
        params = mem_inst_str.strip().upper().split(' ')

        # Checking Params
        if not (len(params) in [1, 2, 4]):
            raise ValueError(f"Error when parsing sub-instruction: \"{mem_inst_str}\"")
        
        # Setting the opcode
        opcode = MI.STR_TO_OPCODE_DICT.get(params[0])
        if opcode is None:
            raise ValueError(f"Operation \"{params[0]}\" not recognized.")
        elif  len(opcode) == 1:
            inst.set_opcode(opcode[0])
        else:
            raise ValueError("STR_TO_OPCODE_DICT is Incorrect.")
        
        # Handling NOP
        if opcode[0] == MI.NOP:
            if not (len(params) in [1]):
                raise ValueError(f"Error when parsing parameters of sub-instruction: \"{mem_inst_str}\"")
            return inst
        
        # Handling Write
        if opcode[0] == MI.WRITE:
            if not (len(params) in [2]):
                raise ValueError(f"Error when parsing parameters of sub-instruction: \"{mem_inst_str}\"")
            try:     value = int(params[1])
            except:  raise ValueError(f"Unable to Convert \"{params[1]}\" to MEMA Offset.")
            inst.set_mema_offset(value)
            inst.set_memb_offset(0)

        # Handling Read
        if opcode[0] == MI.READ:
            if not (len(params) in [4]):
                raise ValueError(f"Error when parsing parameters of sub-instruction: \"{mem_inst_str}\"")
            
            # Extracting Datatype
            datatype = Mode.STR_TO_BITWIDTH_DICT.get(params[1])
            if datatype is None:
                raise ValueError(f"Datatype \"{params[1]}\" not recognized.")
            else:
                inst.set_mode(Mode.opcode(datatype[0]))

            # Extracting Offsets
            try:     value = int(params[2])
            except:  raise ValueError(f"Unable to Convert \"{params[1]}\" to MEMA Offset.")
            inst.set_mema_offset(value)
            try:     value = int(params[3])
            except:  raise ValueError(f"Unable to Convert \"{params[2]}\" to MEMB Offset.")
            inst.set_memb_offset(value)

        # Returning the Instruction
        return inst

    def convert_pe_instruction(self, pe_inst_str : str) -> ProcessingElementInstruction:

        # Creating Instruction to Populate
        inst = ProcessingElementInstruction(self._pe_config)

        # Parsing the Input
        params = pe_inst_str.strip().upper().split(' ')

        # Checking Params
        if not (len(params) in [2, 3]):
            raise ValueError(f"Error when parsing sub-instruction: \"{pe_inst_str}\"")

        # Setting the opcode
        opcode = PEI.STR_TO_OPCODE_DICT.get(params[0])
        if opcode is None:
            raise ValueError(f"Operation \"{params[0]}\" not recognized.")
        elif  len(opcode) == 1:
            inst.set_opcode(opcode[0])
        elif  len(opcode) == 2:
            inst.set_opcode(opcode[0])
            inst.set_value(opcode[1])
        else:
            raise ValueError("STR_TO_OPCODE_DICT is Incorrect.")

        # Setting the datatype
        datatype = Mode.STR_TO_BITWIDTH_DICT.get(params[1])
        if datatype is None:
            raise ValueError(f"Datatype \"{params[1]}\" not recognized.")
        else:
            inst.set_mode(Mode.opcode(datatype[0]))

        # If the Opcode is Round, Set the Value
        if opcode[0] == PEI.RND:
            if len(params) != 3:
                raise ValueError(f"Sub-Instruction RND requires a Third Shift Parameter.")
            try:     value = int(params[2])
            except:  raise ValueError(f"Unable to Convert \"{params[2]}\" to integer shift amount.")
            inst.set_value(value)

        # Returning the Converted Instruction
        return inst
