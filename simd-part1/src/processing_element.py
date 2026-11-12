from bitstring import Bits
from .instruction import ProcessingElementInstruction, PEI
from dataclasses import dataclass

@dataclass
class ProcessingElementConfiguration:
    INPUT_BITWIDTH        : int
    ACCUMULATION_BITWIDTH : int
    OUTPUT_BITWIDTH       : int

class ProcessingElement:

    def __init__(
        self,
        config : ProcessingElementConfiguration,
        default_value = 0
    ):

        # Saving Inputs
        self._config = config

        # Creating Bitstrings
        self._input_a_value = Bits(int=default_value, length=self._config.INPUT_BITWIDTH)
        self._input_b_value = Bits(int=default_value, length=self._config.INPUT_BITWIDTH)
        self._acc_value     = Bits(int=default_value, length=self._config.ACCUMULATION_BITWIDTH)
        self._output_value  = Bits(int=default_value, length=self._config.OUTPUT_BITWIDTH)

    def input_a(self, value : Bits) -> None:
        self._input_a_value = value

    def input_b(self, value : Bits) -> None:
        self._input_b_value = value

    # Handling Each Instruction
    def execute_instruction(self, instruction : ProcessingElementInstruction) -> None:
        # START IMPLEMENTATION
        # Your Code Here
        # END IMPLEMENTATION
        return None

    def _handle_mac(self, instruction : ProcessingElementInstruction):
        # START IMPLEMENTATION
        # Your Code Here
        # END IMPLEMENTATION
        return None

    def _handle_out(self, instruction : ProcessingElementInstruction):
        # Clamp each signed wide lane to its signed output range; preserve accumulation.
        # START IMPLEMENTATION
        # Your Code Here
        # END IMPLEMENTATION
        return None

    def _handle_pass(self, instruction : ProcessingElementInstruction):
        # START IMPLEMENTATION
        # Your Code Here
        # END IMPLEMENTATION
        return None

    def _handle_clr(self, instruction : ProcessingElementInstruction):
        # START IMPLEMENTATION
        # Your Code Here
        # END IMPLEMENTATION
        return None

    def _handle_rnd(self, instruction : ProcessingElementInstruction):
        # Divide signed wide lanes by 2**unsigned(value), nearest with ties to even; preserve output.
        # START IMPLEMENTATION
        # Your Code Here
        # END IMPLEMENTATION
        return None

    def get_output(self) -> Bits:
        return self._output_value

    def get_accumulation(self) -> Bits:
        return self._acc_value
