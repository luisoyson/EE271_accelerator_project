from dataclasses import dataclass
from bitstring import Bits
import numpy as np

@dataclass
class MemoryInstructionConfiguration:
    OPCODE_BITWIDTH      : int
    MODE_BITWIDTH        : int
    MEMA_OFFSET_BITWIDTH : int
    MEMB_OFFSET_BITWIDTH : int

    def get_width(self):
        return self.OPCODE_BITWIDTH + self.MODE_BITWIDTH + self.MEMA_OFFSET_BITWIDTH + self.MEMB_OFFSET_BITWIDTH

class MemoryInstructionEnum:
    READ   = 0
    WRITE  = 1
    NOP    = 2

    # Dictionaries for Convient Translation
    STR_TO_OPCODE_DICT = {
        'READ'  : [READ],
        'WRITE' : [WRITE],
        'NOP'   : [NOP]
    }

MI=MemoryInstructionEnum

class MemoryInstruction:

    def __init__(
        self,
        memory_config : MemoryInstructionConfiguration
    ):
        # Ensuring the Memory Configuration is Valid
        self._memory_config = memory_config

        # Generating the Bitstring Representation
        self._instruction_value = Bits(uint=0, length=self._memory_config.get_width())

        # Computing the Indicies of the Pertinent Values within the Instruction
        self._opcode_start = 0
        self._mode_start        = self._opcode_start      + self._memory_config.OPCODE_BITWIDTH
        self._mema_offset_start = self._mode_start        + self._memory_config.MODE_BITWIDTH
        self._memb_offset_start = self._mema_offset_start + self._memory_config.MEMA_OFFSET_BITWIDTH

    def get_width(self) -> int:
        return self._memory_config.get_width()

    def set_opcode(self, value : int) -> None:
        self._instruction_value = Bits().join([
            Bits(uint=value,length=self._memory_config.OPCODE_BITWIDTH),
            self.get_mode(),
            self.get_mema_offset(),
            self.get_memb_offset()
        ])

    def get_opcode(self) -> Bits:
        return self._instruction_value[self._opcode_start:(self._opcode_start + self._memory_config.OPCODE_BITWIDTH)]

    def set_mode(self, value : int) -> None:
        self._instruction_value = Bits().join([
            self.get_opcode(),
            Bits(uint=value,length=self._memory_config.MODE_BITWIDTH),
            self.get_mema_offset(),
            self.get_memb_offset()
        ])

    def get_mode(self) -> Bits:
        return self._instruction_value[self._mode_start:(self._mode_start + self._memory_config.MODE_BITWIDTH)]

    def set_mema_offset(self, value : int) -> None:
        self._instruction_value = Bits().join([
            self.get_opcode(),
            self.get_mode(),
            Bits(uint=value,length=self._memory_config.MEMA_OFFSET_BITWIDTH),
            self.get_memb_offset()
        ])

    def get_mema_offset(self) -> Bits:
        return self._instruction_value[self._mema_offset_start:(self._mema_offset_start + self._memory_config.MEMA_OFFSET_BITWIDTH)]

    def set_memb_offset(self, value : int) -> None:
        self._instruction_value = Bits().join([
            self.get_opcode(),
            self.get_mode(),
            self.get_mema_offset(),
            Bits(uint=value,length=self._memory_config.MEMB_OFFSET_BITWIDTH),
        ])

    def get_memb_offset(self) -> Bits:
        return self._instruction_value[self._memb_offset_start:(self._memb_offset_start + self._memory_config.MEMB_OFFSET_BITWIDTH)]

    def get_instruction(self) -> Bits:
        return self._instruction_value

    def set_instruction(self, value : Bits) -> None:
        self._instruction_value = value

@dataclass
class ProcessingElementInstructionConfiguration:
    OPCODE_BITWIDTH      : int
    MODE_BITWIDTH        : int
    VALUE_BITWIDTH       : int

    def get_width(self):
        return self.OPCODE_BITWIDTH + self.MODE_BITWIDTH + self.VALUE_BITWIDTH

class ProcessingElementInstructionEnum:

    # Instructions Which Use the Value
    # Field as the "Opcode"
    NO_VALUE = 0
    MAC      = 0
    NOP      = 1
    OUT      = 2
    PASS     = 3
    CLR      = 4

    # Instructions Which Require the Value Field
    RND      = 1

    # Dictionaries for Convient Translation
    STR_TO_OPCODE_DICT = {
        'MAC'  : [NO_VALUE, MAC],
        'NOP'  : [NO_VALUE, NOP],
        'OUT'  : [NO_VALUE, OUT],
        'PASS' : [NO_VALUE, PASS],
        'CLR'  : [NO_VALUE, CLR],
        'RND'  : [RND]
    }

PEI=ProcessingElementInstructionEnum

class Mode:

    # Bitwidths
    INT8    = 8
    INT16   = 16
    INT32   = 32
    SMALLEST_MODE = 8

    @staticmethod
    def opcode(value : int) -> int:
        return int(np.ceil(np.log2(value/8)))

    @staticmethod
    def bitwidth(value : int) -> int:
        return ((2**value) * 8)

    # Dictionaries for Convient Translation
    STR_TO_BITWIDTH_DICT = {
        'INT8'  : [INT8],
        'INT16' : [INT16],
        'INT32' : [INT32]
    }
    BITWIDTH_TO_STR_DICT = {
        INT8    : 'INT8',
        INT16   : 'INT16',
        INT32   : 'INT32'
    }


class ProcessingElementInstruction:

    def __init__(
        self,
        memory_config : ProcessingElementInstructionConfiguration
    ):
        # Saving the Memory Configuration
        self._memory_config = memory_config

        # Generating the Bitstring Representation
        self._instruction_value = Bits(uint=0, length=self._memory_config.get_width())

        # Computing the Indicies of the Pertinent Values within the Instruction
        self._opcode_start = 0
        self._mode_start   = self._opcode_start + self._memory_config.OPCODE_BITWIDTH
        self._value_start  = self._mode_start   + self._memory_config.MODE_BITWIDTH

    def get_width(self) -> int:
        return self._memory_config.get_width()

    def set_opcode(self, value : int) -> None:
        self._instruction_value = Bits().join([
            Bits(uint=value,length=self._memory_config.OPCODE_BITWIDTH),
            self.get_mode(),
            self.get_value()
        ])

    def get_opcode(self) -> Bits:
        return self._instruction_value[self._opcode_start:(self._opcode_start + self._memory_config.OPCODE_BITWIDTH)]

    def set_mode(self, value : int) -> None:
        self._instruction_value = Bits().join([
            self.get_opcode(),
            Bits(uint=value,length=self._memory_config.MODE_BITWIDTH),
            self.get_value()
        ])

    def get_mode(self) -> Bits:
        return self._instruction_value[self._mode_start:(self._mode_start + self._memory_config.MODE_BITWIDTH)]

    def get_mode_bitwidth(self) -> int:
        return Mode.bitwidth(int(self.get_mode().uint))

    def set_value(self, value : int) -> None:
        self._instruction_value = Bits().join([
            self.get_opcode(),
            self.get_mode(),
            Bits(uint=value,length=self._memory_config.VALUE_BITWIDTH)
        ])

    def get_value(self) -> Bits:
        return self._instruction_value[self._value_start:(self._value_start + self._memory_config.VALUE_BITWIDTH)]

    def get_instruction(self) -> Bits:
        return self._instruction_value

    def set_instruction(self, value : Bits) -> None:
        self._instruction_value = value

@dataclass
class InstructionConfiguration:

    # Instruction-Level Configuration Options
    COUNT_BITWIDTH       : int
    MEMA_INC_BITWIDTH    : int
    MEMB_INC_BITWIDTH    : int

    # Configurations for Sub-Instructions
    MEMORY_INST_CONFIG   : MemoryInstructionConfiguration
    PE_INST_CONFIG       : ProcessingElementInstructionConfiguration

    def get_width(self):
        return self.COUNT_BITWIDTH + self.MEMA_INC_BITWIDTH + self.MEMB_INC_BITWIDTH
InstConfig=InstructionConfiguration

class Instruction:
    def __init__(
        self,
        inst_config : InstructionConfiguration
    ):
        # Saving Memory Configurations
        self._inst_config = inst_config

        # Computing the Indicies of the Pertinent Values within the Instruction
        self._mem_inst_start  = 0
        self._pe_inst_start   = self._mem_inst_start + self._inst_config.MEMORY_INST_CONFIG.get_width()
        self._count_start     = self._pe_inst_start  + self._inst_config.PE_INST_CONFIG.get_width()
        self._mema_inc_start  = self._count_start    + self._inst_config.COUNT_BITWIDTH
        self._memb_inc_start  = self._mema_inc_start + self._inst_config.MEMA_INC_BITWIDTH

        # Creating Empty Variables
        self._mem_instruction = MemoryInstruction(self._inst_config.MEMORY_INST_CONFIG)
        self._pe_instruction  = ProcessingElementInstruction(self._inst_config.PE_INST_CONFIG)
        self._count    = Bits(uint=0,length=self._inst_config.COUNT_BITWIDTH)
        self._mema_inc = Bits(uint=0,length=self._inst_config.MEMA_INC_BITWIDTH)
        self._memb_inc = Bits(uint=0,length=self._inst_config.MEMB_INC_BITWIDTH)

    def get_width(self) -> int:
        return self._inst_config.get_width() + self._inst_config.MEMORY_INST_CONFIG.get_width() + self._inst_config.PE_INST_CONFIG.get_width()

    def set_mem_instruction(self, value : MemoryInstruction) -> None:
        self._mem_instruction = value

    def get_mem_instruction(self) -> MemoryInstruction:
        return self._mem_instruction

    def set_pe_instruction(self, value : ProcessingElementInstruction) -> None:
        self._pe_instruction = value

    def get_pe_instruction(self) -> ProcessingElementInstruction:
        return self._pe_instruction

    def set_count(self, value : int) -> None:
        self._count = Bits(uint=value,length=self._inst_config.COUNT_BITWIDTH)

    def get_count(self) -> Bits:
        return self._count

    def set_mema_inc(self, value : int) -> None:
        self._mema_inc = Bits(uint=value,length=self._inst_config.MEMA_INC_BITWIDTH)

    def get_mema_inc(self) -> Bits:
        return self._mema_inc

    def set_memb_inc(self, value : int) -> None:
        self._memb_inc = Bits(uint=value,length=self._inst_config.MEMB_INC_BITWIDTH)

    def get_memb_inc(self) -> Bits:
        return self._memb_inc

    def get_instruction(self) -> Bits:
        # print(self._pe_instruction.get_instruction())
        return Bits().join([
            self._mem_instruction.get_instruction(),
            self._pe_instruction.get_instruction(),
            self._count,
            self._mema_inc,
            self._memb_inc
        ])

    def set_instruction(self, value : Bits) -> None:

        # Slicing the input
        mem_inst_bits = value[self._mem_inst_start :(self._mem_inst_start + self._inst_config.MEMORY_INST_CONFIG.get_width())]
        pe_inst_bits  = value[self._pe_inst_start  :(self._pe_inst_start  + self._inst_config.PE_INST_CONFIG.get_width())    ]
        count_bits    = value[self._count_start    :(self._count_start    + self._inst_config.COUNT_BITWIDTH)                ]
        mema_inc_bits = value[self._mema_inc_start :(self._mema_inc_start + self._inst_config.MEMA_INC_BITWIDTH)             ]
        memb_inc_bits = value[self._memb_inc_start :(self._memb_inc_start + self._inst_config.MEMB_INC_BITWIDTH)             ]

        # Setting Values
        self._mem_instruction.set_instruction(mem_inst_bits)
        self._pe_instruction.set_instruction(pe_inst_bits)
        self._count = count_bits
        self._mema_inc = mema_inc_bits
        self._memb_inc = memb_inc_bits
