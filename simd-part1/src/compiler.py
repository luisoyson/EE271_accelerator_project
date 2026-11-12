from src.accelerator import AccelConfig
from src.main_buffer import MainBufferConfiguration
from src.processing_element import ProcessingElementConfiguration
from src.instruction import InstConfig, ProcessingElementInstructionConfiguration, MemoryInstructionConfiguration, Mode
import numpy as np
from bitstring import Bits

def generate_accelerator_and_instruction_configuration(
    processing_element_count                 = 4,
    processing_element_input_bitwidth        = 32,
    processing_element_accumulation_bitwidth = 32,
    processing_element_output_bitwidth       = 32,
    controller_counter_bitwidth              = 10
) -> tuple[AccelConfig, InstConfig]:

    # Configuring the Accelerator
    accel_config = AccelConfig(
        COUNTER_BITWIDTH = controller_counter_bitwidth,
        PE_COUNT         = processing_element_count,
        PE_CONFIG        = ProcessingElementConfiguration(
            INPUT_BITWIDTH        = processing_element_input_bitwidth,
            ACCUMULATION_BITWIDTH = processing_element_accumulation_bitwidth,
            OUTPUT_BITWIDTH       = processing_element_output_bitwidth
        ),
        BUFFER_CONFIG    = MainBufferConfiguration(
            MEM0_BITWIDTH = processing_element_count * processing_element_input_bitwidth,
            MEM0_DEPTH    = (2 ** controller_counter_bitwidth),
            MEM1_BITWIDTH = processing_element_input_bitwidth,
            MEM1_DEPTH    = (2 ** (controller_counter_bitwidth - int(np.ceil(np.log2(processing_element_input_bitwidth/Mode.SMALLEST_MODE)))) ),
            MEM2_BITWIDTH = processing_element_count * processing_element_output_bitwidth,
            MEM2_DEPTH    = (2 ** controller_counter_bitwidth)
        )
    )
    
    # Configuring the Instruction Format
    # NOTE: These Values Come From the ISA Definition
    inst_config = InstConfig(
        COUNT_BITWIDTH     = controller_counter_bitwidth,
        MEMA_INC_BITWIDTH  = 1,
        MEMB_INC_BITWIDTH  = 1,
        MEMORY_INST_CONFIG = MemoryInstructionConfiguration(
            OPCODE_BITWIDTH      = 2,
            MODE_BITWIDTH        = 2, 
            MEMA_OFFSET_BITWIDTH = controller_counter_bitwidth,
            MEMB_OFFSET_BITWIDTH = controller_counter_bitwidth
        ),
        PE_INST_CONFIG     = ProcessingElementInstructionConfiguration(
            OPCODE_BITWIDTH      = 2,
            MODE_BITWIDTH        = 2,
            VALUE_BITWIDTH       = 5
        )
    )

    return accel_config, inst_config

def compile_matrix_vector_multiplication(
    matrix : np.ndarray,
    vector : np.ndarray,
    config : AccelConfig,
    computation_bitwidth : int
) -> tuple[list[Bits],list[Bits],list[str],int]:
    # Creating Lists to Store the Required MEM0 and MEM1 Configurations
    mem0_configs = []
    mem1_configs = []
    instruction_list = []

    # Computing How to Split the Computation into Sub-Computations
    number_of_rows         = config.PE_COUNT * int(config.PE_CONFIG.INPUT_BITWIDTH/computation_bitwidth)
    row_sub_comp_count     = int(np.ceil(len(matrix)/number_of_rows))

    for sub_matrix_row in range(row_sub_comp_count):
        for sub_matrix_col in range(len(matrix[0])):

            # Extracting the Sub Matrix and Padding
            sub_matrix = matrix[(sub_matrix_row * number_of_rows):((sub_matrix_row+1) * number_of_rows),sub_matrix_col]
            (elem_count,) = sub_matrix.shape
            if elem_count < number_of_rows:
                zero_matrix = np.zeros(number_of_rows-elem_count, dtype=np.int64)
                sub_matrix = np.concatenate([sub_matrix, zero_matrix], axis=0)

            # Packing into a Single Memory Entry
            mem_entry = Bits().join([
                Bits(int=elem, length=computation_bitwidth) for elem in sub_matrix
            ])
            mem0_configs = mem0_configs + [mem_entry]

        # Creating Instruction
        instruction_list = instruction_list + [f"NOP | CLR {Mode.BITWIDTH_TO_STR_DICT[computation_bitwidth]} | 1 0 0"]
        instruction_list = instruction_list + [f"READ {Mode.BITWIDTH_TO_STR_DICT[computation_bitwidth]} {sub_matrix_row * len(matrix[0])} 0 | MAC {Mode.BITWIDTH_TO_STR_DICT[computation_bitwidth]} | {len(matrix[0])} 1 1"]
        instruction_list = instruction_list + [f"NOP | OUT {Mode.BITWIDTH_TO_STR_DICT[computation_bitwidth]} | 1 0 0"]
        instruction_list = instruction_list + [f"WRITE {sub_matrix_row} | NOP {Mode.BITWIDTH_TO_STR_DICT[computation_bitwidth]} | 1 0 0"]

    # Organizing MEM1
    number_of_cols         = int(config.PE_CONFIG.INPUT_BITWIDTH/computation_bitwidth)
    col_sub_comp_count     = int(np.ceil(len(matrix[0])/number_of_cols))
    for sub_vector_col in range(col_sub_comp_count):

        # Extracting the Sub Vector and Padding
        sub_vector = vector[(sub_vector_col * number_of_cols):((sub_vector_col+1) * number_of_cols)]
        (row_count, _) = sub_vector.shape
        if row_count < number_of_cols:
            zero_matrix = np.zeros((number_of_cols-row_count,1), dtype=np.int64)
            sub_vector = np.concatenate([sub_vector, zero_matrix], axis=0)
        
        # Flattening the Sub-Vector and Reversing
        sub_vector = sub_vector.flatten()
        sub_vector = [sub_vector[-1 * (i + 1)] for i in range(len(sub_vector))]

        # Packing into a Single Memory Entry
        mem_entry = Bits().join([
            Bits(int=elem, length=computation_bitwidth) for elem in sub_vector
        ])
        mem1_configs = mem1_configs + [mem_entry]

    # Padding Memory
    mem0_configs = mem0_configs + [Bits(int=0,length=config.BUFFER_CONFIG.MEM0_BITWIDTH) for _ in range(config.BUFFER_CONFIG.MEM0_DEPTH - len(mem0_configs))]
    mem1_configs = mem1_configs + [Bits(int=0,length=config.BUFFER_CONFIG.MEM1_BITWIDTH) for _ in range(config.BUFFER_CONFIG.MEM1_DEPTH - len(mem1_configs))]

    # Returning Configurations and Instructions
    return mem0_configs, mem1_configs, instruction_list, len(matrix)

def extract_results_from_memory(
    memory : list[Bits],
    num_elems_to_extract : int,
    config : AccelConfig,
    computation_bitwidth : int
) -> np.ndarray:
    
    # Computing Necessary Parameters
    elems_per_entry = config.PE_COUNT * (config.PE_CONFIG.OUTPUT_BITWIDTH/computation_bitwidth)
    entries_to_read = int(np.ceil(num_elems_to_extract / elems_per_entry))

    # Iterating
    output = []
    for mem_idx in range(entries_to_read):
        value = memory[mem_idx]
        output = output + [elem.int for elem in value.cut(computation_bitwidth)]

    # Returning
    return np.array(list(output[:num_elems_to_extract]))