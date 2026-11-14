from bitstring import Bits
from .instruction import MemoryInstruction, MI, Mode
from dataclasses import dataclass
import numpy as np

@dataclass
class MainBufferConfiguration:
    MEM0_BITWIDTH : int
    MEM0_DEPTH    : int
    MEM1_BITWIDTH : int
    MEM1_DEPTH    : int
    MEM2_BITWIDTH : int
    MEM2_DEPTH    : int

class MainBuffer:

    def __init__(
        self,
        config : MainBufferConfiguration,
        default_value = 0
    ):

        # Saving the Config
        self._buffer_config = config

        # Creating the Individual Memories
        self._mem0 = [Bits(int=default_value, length=self._buffer_config.MEM0_BITWIDTH) for _ in range(self._buffer_config.MEM0_DEPTH)]
        self._mem1 = [Bits(int=default_value, length=self._buffer_config.MEM1_BITWIDTH) for _ in range(self._buffer_config.MEM1_DEPTH)]
        self._mem2 = [Bits(int=default_value, length=self._buffer_config.MEM2_BITWIDTH) for _ in range(self._buffer_config.MEM2_DEPTH)]

        # Creating the Output And Input Ports
        self._mem0_output_port = Bits(int=default_value, length=self._buffer_config.MEM0_BITWIDTH) #one liner
        self._mem1_output_port = Bits(int=default_value, length=self._buffer_config.MEM1_BITWIDTH) #one liner
        self._mem2_input_port  = Bits(int=default_value, length=self._buffer_config.MEM2_BITWIDTH)

    def execute_instruction(self, instruction : MemoryInstruction) -> None:
        """verified """
        opcode = instruction.get_opcode().uint 
        if opcode == MI.READ:
          self._handle_read(instruction) 
        elif opcode == MI.WRITE: 
          self._handle_write(instruction)
        elif opcode == MI.NOP:
            pass 
        else:
            raise ValueError(f"Not a valid instruction: {opcode}")

        return None

    def _handle_read(self, instruction : MemoryInstruction) -> None:
        #MEM0
        address_offset_a = instruction.get_mema_offset().uint #grab the row address
        self._mem0_output_port = self._mem0[address_offset_a]  #get value of raw address 

        #MEM1 
        lane_width = Mode.bitwidth(instruction.get_mode().uint)       # 8, 16 or 32
        pieces = self._buffer_config.MEM1_BITWIDTH // lane_width      # 4, 2 or 1
        address_offset_b = instruction.get_memb_offset().uint
        select = address_offset_b % pieces                            # low bit(s): which sub-word
        address = address_offset_b // pieces                          # the rest: the MEM1 address

        word = self._mem1[address]
        # Bits index 0 is the MSB, so sub-word 0 (least significant) is the LAST lane_width bits
        start = len(word) - (select + 1) * lane_width
        sub_word = word[start:start + lane_width]

        #mode = Mode.bitwidth(instruction.get_mode().uint)

        #selector = instruction.get_mode().uint #gives 0, 1, 2 

        #total_address_offset_b = instruction.get_memb_offset()
        #address_offset_b = total_address_offset_b[9:selector+1]  
        #sub_word_status = addres_offset_b[selector:0]
     
        #lane_width = Mode.bitwidth(lane_width) #gives 8,16, or 32

        #address_offset_b

       #16-bit case, 8-bit case
       #grab the mode bitwidth
       #grab the MSB:

        #self._mem1_output_port = self._mem1[address_offset_b] 
        self._mem1_output_port = Bits().join([sub_word] * pieces)

       
        return None

    def _handle_write(self, instruction : MemoryInstruction) -> None:
        """verified"""
        address_offset = instruction.get_mema_offset().uint 
        self._mem2[address_offset] = self._mem2_input_port
        return None

    def read_mem0_output(self) -> Bits:
        return self._mem0_output_port

    def read_mem1_output(self) -> Bits:
        return self._mem1_output_port

    def write_mem2_input(self, value : Bits) -> None:
        self._mem2_input_port = value

    def set_mem0(self, mem : list[int]) -> None:
        # Ensuring the Memory List is the Proper Length and Writing
        if len(mem) != self._buffer_config.MEM0_DEPTH:
            raise ValueError(f"Length of Memory [{len(mem)}] is incorrect for depth [{self._buffer_config.MEM0_DEPTH}] ")
        self._mem0 = [Bits(int=elem, length=self._buffer_config.MEM0_BITWIDTH) for elem in mem]

    def set_mem1(self, mem : list[int]) -> None:
        # Ensuring the Memory List is the Proper Length and Writing
        if len(mem) != self._buffer_config.MEM1_DEPTH:
            raise ValueError(f"Length of Memory [{len(mem)}] is incorrect for depth [{self._buffer_config.MEM1_DEPTH}] ")
        self._mem1 = [Bits(int=elem, length=self._buffer_config.MEM1_BITWIDTH) for elem in mem]

    def set_mem0_bits(self, mem : list[Bits]) -> None:
        # Ensuring the Memory List is the Proper Length and Writing
        if len(mem) != self._buffer_config.MEM0_DEPTH:
            raise ValueError(f"Length of Memory [{len(mem)}] is incorrect for depth [{self._buffer_config.MEM0_DEPTH}] ")
        self._mem0 = mem

    def set_mem1_bits(self, mem : list[Bits]) -> None:
        # Ensuring the Memory List is the Proper Length and Writing
        if len(mem) != self._buffer_config.MEM1_DEPTH:
            raise ValueError(f"Length of Memory [{len(mem)}] is incorrect for depth [{self._buffer_config.MEM1_DEPTH}] ")
        self._mem1 = mem

    def read_mem2(self) -> list[int]:
        return [elem.int for elem in self._mem2]

    def read_mem2_bits(self) -> list[Bits]:
        return self._mem2
