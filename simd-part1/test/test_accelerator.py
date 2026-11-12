from src.accelerator import Accelerator
from src.assembler import Assembler
from src.instruction import Mode
from src.compiler import generate_accelerator_and_instruction_configuration, compile_matrix_vector_multiplication, extract_results_from_memory
import numpy as np
import sys

def main():

    errors = 0
    errors = errors + run_test(768,64,12345,Mode.INT16, 64)
    errors = errors + run_test(768,64,12345,Mode.INT32, 13)
    errors = errors + run_test(64,3,0,Mode.INT8, 9)

    # Determining the Status of All Tests
    if errors == 0:
        print("All Tests Passed!")
    else:
        print(f"{errors} Tests Failed!")
    sys.exit(errors)

def run_test(
    rows, cols, seed, precision, pe_count
):
    # Configuring
    accel_config, inst_config = generate_accelerator_and_instruction_configuration(
        processing_element_accumulation_bitwidth=64,
        processing_element_count=pe_count,
        controller_counter_bitwidth=16
    )
    assembler = Assembler(inst_config)
    accel = Accelerator(accel_config)

    matrix, vector, gold_result = generate_test_matrix_vector_computation(rows, cols, seed)

    # Compiling Computation
    mem0, mem1, instructions, num_elements = compile_matrix_vector_multiplication(
        matrix, vector, accel_config, precision
    )

    # Loading Data into Accelerator
    accel.set_memory(mem0,mem1)

    # Executing Instructions with the Accelerator
    accel.execute_instructions(assembler.assemble_instructions(instructions))

    # Decoding the Results
    result = extract_results_from_memory(
        accel.get_mem2(), num_elements, accel_config, precision
    )

    if np.all(result == gold_result):
        print(f"(Rows:{rows},Cols:{cols},Prec:{precision},PE Count:{pe_count}) Test Passed!")
        return 0
    else:
        print(f"(Rows:{rows},Cols:{cols},Prec:{precision},PE Count:{pe_count}) Test Failed!")
        return 1


def generate_test_matrix_vector_computation(
    rows : int, cols : int, seed : int,
    min_value = -5, max_value = 5
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:

    # Creating a Matrix to Test With Seed
    np.random.seed(seed)
    test_matrix = np.random.randint(min_value, max_value, size=(rows,cols))
    test_vector = np.random.randint(min_value, max_value, size=(cols,1))
    gold_result = test_matrix @ test_vector
    gold_result = gold_result.flatten()
    return test_matrix, test_vector, gold_result


if __name__ == "__main__":
    main()