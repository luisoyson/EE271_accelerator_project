from dataclasses import dataclass
from bitstring import Bits
from .processing_element import ProcessingElement, ProcessingElementConfiguration
from .main_buffer import MainBuffer, MainBufferConfiguration
from .instruction import Instruction, MemoryInstruction, ProcessingElementInstruction


@dataclass
class AcceleratorConfiguration:

    # Top Level Specific Values
    COUNTER_BITWIDTH : int
    PE_COUNT         : int

    # Internal Buffer/PE Configurations
    PE_CONFIG        : ProcessingElementConfiguration
    BUFFER_CONFIG    : MainBufferConfiguration

    # Function to Validate Configuration
    def validate(self) -> None:

        # Ensuring the Width of the Main Buffer Matches the
        # Number of PEs in the Array accounting for Input Width
        if (self.PE_COUNT != (self.BUFFER_CONFIG.MEM0_BITWIDTH/self.PE_CONFIG.INPUT_BITWIDTH)):
            raise ValueError(f"Incorrect number of PEs ({self.PE_COUNT}) with input bitwidth {self.PE_CONFIG.INPUT_BITWIDTH} for memory output bitwidth {self.BUFFER_CONFIG.MEM0_BITWIDTH}.")

        # Ensuring the Width of the Main Buffer Matches the PE input bitwidth
        if (self.PE_CONFIG.INPUT_BITWIDTH != self.BUFFER_CONFIG.MEM1_BITWIDTH):
            raise ValueError(f"Incorrect PE input bitwidth {self.PE_CONFIG.INPUT_BITWIDTH} for memory bitwidth {self.BUFFER_CONFIG.MEM1_BITWIDTH}.")

        # Ensuring the Width of the Main Buffer Matches the PE output bitwidth
        if (self.PE_COUNT != (self.BUFFER_CONFIG.MEM2_BITWIDTH/self.PE_CONFIG.OUTPUT_BITWIDTH)):
            raise ValueError(f"Incorrect number of PEs ({self.PE_COUNT}) with output bitwidth {self.PE_CONFIG.OUTPUT_BITWIDTH} for memory input bitwidth {self.BUFFER_CONFIG.MEM2_BITWIDTH}.")
AccelConfig=AcceleratorConfiguration


class Accelerator:

    def __init__(
        self,
        controller_config : AcceleratorConfiguration,
        default_counter_value = 0
    ):

        # Saving the Configuration and Validating
        self._controller_config = controller_config
        self._controller_config.validate()

        # Creating a Bit-Accurate Representation of the Counter
        self._counter = Bits(uint=default_counter_value, length=self._controller_config.COUNTER_BITWIDTH)

        # Creating an Array of PEs
        self._pe_array = [
            ProcessingElement(self._controller_config.PE_CONFIG) for _ in range(self._controller_config.PE_COUNT)
        ]

        # Creating a Main Buffer
        self._main_buffer = MainBuffer(self._controller_config.BUFFER_CONFIG)

    def set_memory(self, mem0 : list[Bits], mem1 : list[Bits]) -> None:
        self.set_mem0(mem0)
        self.set_mem1(mem1)

    def set_mem0(self, mem : list[Bits]) -> None:
        self._main_buffer.set_mem0_bits(mem)

    def set_mem1(self, mem : list[Bits]) -> None:
        self._main_buffer.set_mem1_bits(mem)

    def get_mem2(self) -> list[Bits]:
        return self._main_buffer.read_mem2_bits()

    def execute_instructions(self, instructions : list[Instruction]):
        for inst in instructions:
            self.execute_instruction(inst)

    def execute_instruction(self, instruction : Instruction):
        # START IMPLEMENTATION
        # Your Code Here
        # END IMPLEMENTATION
        return 0
