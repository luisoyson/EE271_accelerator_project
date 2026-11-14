from bitstring import Bits
from .instruction import ProcessingElementInstruction, PEI
from dataclasses import dataclass
#TO SELF: Java: Bits word 
def unpack_lanes(word: Bits, lane_bits: int) -> list[int]: 
    """purpose of this unpacking is to perform calculations (in signed integers)"""
    #assuming lane_bits is of values 8, 16, 32 
    #lane_bits is size of each lane

    lanes_list = list(word.cut(lane_bits)) # gets all output from iterable 
    lanes_list = [p.int for p in lanes_list] #convert to lanes_list, always use .int for ease of signed complement 
    lanes_list.reverse()  #consider using reversed(lanes)
    return lanes_list


def pack_lanes(lanes: list[int], lane_bits: int) -> Bits: 
    """purpose of this is to bring back values from int to bit form for storage"""
    #we just simply combine the lanes
    lanes_list = lanes[::-1]  #to not change the callers list, we do not use reverse
    #convert from int to bit 
    bits_lane = Bits().join(Bits(int=p, length=lane_bits) for p in lanes_list)
    return bits_lane
    #example list of products 

    
@dataclass #not to edit, 
class ProcessingElementConfiguration: #just declares PE config has 3 integer fields
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
        #Bits() -> constructor to create bitspring object
        self._input_a_value = Bits(int=default_value, length=self._config.INPUT_BITWIDTH) #
        self._input_b_value = Bits(int=default_value, length=self._config.INPUT_BITWIDTH)
        self._acc_value     = Bits(int=default_value, length=self._config.ACCUMULATION_BITWIDTH)
        self._output_value  = Bits(int=default_value, length=self._config.OUTPUT_BITWIDTH)

    def input_a(self, value : Bits) -> None: #setter method 
        self._input_a_value = value

    def input_b(self, value : Bits) -> None: #setter method
        self._input_b_value = value

    # Handling Each Instruction
    def execute_instruction(self, instruction : ProcessingElementInstruction) -> None:
        """ execute_instruction is a PE decoder pe.execute_instruction(elem) """
        #instruction.get_mode_bitwidth()  --> all handled by inner methods 
        #PEI.NO_VALUE, PEI.RND, PEI.MAC, PEI.NOP, PEI.OUT, PEI.PASS, PEI.CLR  
        opcode =   instruction.get_opcode().uint
        value = instruction.get_value().uint 
        #if opcode == 1: 
        if opcode == PEI.RND:
            self._handle_rnd(instruction)
        elif opcode == PEI.NO_VALUE: #assuming just 0
            if value == PEI.MAC: 
                self._handle_mac(instruction)
            elif value == PEI.NOP:
               pass 
            elif value == PEI.OUT: 
                self._handle_out(instruction)
            elif value == PEI.PASS:
               self._handle_pass(instruction)
            elif value == PEI.CLR: 
                self._handle_clr(instruction)
            else:
                    raise ValueError(f"Unknown PE operation in value field: {value}")
        else:
            raise ValueError(f"Unknown PE opcode: {opcode}")
             
        return None

    def _handle_mac(self, instruction : ProcessingElementInstruction):
        #STEP 1: 
        lane_width = instruction.get_mode_bitwidth()
        input_a_list = unpack_lanes(self._input_a_value, lane_width) 
        input_b_list = unpack_lanes(self._input_b_value, lane_width)
        product_list = [] 
        for n in range(len(input_a_list)): 
            product_list.append(input_a_list[n] * input_b_list[n]) 

        acc_lane_width = 2 * lane_width 
        accum_list = unpack_lanes(self._acc_value, acc_lane_width) 

        for n in range(len(product_list)):
            accum_list[n] += product_list[n]  

        self._acc_value = pack_lanes(accum_list, acc_lane_width) 

        return None 

    def _handle_out(self, instruction : ProcessingElementInstruction):
        """not yet verified tests """ 
        # Clamp each signed wide lane to its signed output range; preserve accumulation. Clamping
        lane_width = instruction.get_mode_bitwidth() 
        acc_lane_width = 2 * lane_width 
        # to self, in future: would this run into issues, if we got lane_width here, or just get acc_lane_width, is there a function for this?
        
        accum_list = unpack_lanes(self._acc_value, acc_lane_width) #list[int]
        ## arithmetic clamping and narrowing manipulation --> given we are in int, already reduces
        accum_list = [min(max(p, -2**(lane_width -1)), 2**(lane_width - 1) - 1) for p in accum_list] 
        #according to lane_width, slices
        self._output_value = pack_lanes(accum_list, lane_width) 

        return None

    def _handle_pass(self, instruction : ProcessingElementInstruction):
        """handle_pass , verified, sign-extended into accumulator"""
        lane_width = instruction.get_mode_bitwidth()
        acc_lane_width = 2 * lane_width 
        data0_list = unpack_lanes(self._input_a_value, lane_width) #this is a list[int] 
        #data0_list = [Bits(int=p, length=acc_lane_width) for p in data0_list] #this is a list of sign extended bits
        self._acc_value = pack_lanes(data0_list, acc_lane_width) #set accumulator value
        
        return None

    def _handle_clr(self, instruction : ProcessingElementInstruction):
        """clear output and accumulator register"""
        self._acc_value = Bits(uint=0, length=self._config.ACCUMULATION_BITWIDTH)
        self._output_value = Bits(uint=0, length=self._config.OUTPUT_BITWIDTH)
        return None

    def _handle_rnd(self, instruction : ProcessingElementInstruction):
        """handle_rnd, handles value, not yet verified"""
        # Divide signed wide lanes by 2**unsigned(value), nearest with ties to even; preserve output.
        lane_width = instruction.get_mode_bitwidth()
        acc_lane_width = 2 * lane_width
        accum_list = unpack_lanes(self._acc_value, acc_lane_width)   # lane 0 first
        div_factor = instruction.get_value().uint                    # s, unsigned
        divisor = 1 << div_factor                                    # 2**s as an exact int

        rounded_list = []
        for p in accum_list:
            quotient, remainder = divmod(p, divisor)    # floor division; 0 <= remainder < divisor
            if 2 * remainder > divisor or (2 * remainder == divisor and quotient % 2 == 1):
                quotient += 1                           # past halfway, or a tie with an odd floor
            rounded_list.append(quotient)

        self._acc_value = pack_lanes(rounded_list, acc_lane_width)
     
      #int -> float -> int ? yeah do not use round() ! 
    
        return None

    def get_output(self) -> Bits:
        return self._output_value

    def get_accumulation(self) -> Bits:
        return self._acc_value
