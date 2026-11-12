from src.assembler import Assembler
from src.instruction import MemoryInstruction, InstConfig, MemoryInstructionConfiguration, ProcessingElementInstructionConfiguration
from src.main_buffer import MainBuffer, MainBufferConfiguration
from bitstring import Bits
import sys

def main():

    # Testing Processing Element
    errors = 0
    errors += test_read_int32()
    errors += test_read_int16()
    errors += test_read_int8()
    errors += test_write()

    # Determining the Status of All Tests
    if errors == 0:
        print("All Tests Passed!")
    else:
        print(f"{errors} Tests Failed!")
    sys.exit(errors)

def test_read_int16() -> int:
     
    mem_config = MainBufferConfiguration(
        MEM0_BITWIDTH=256,
        MEM0_DEPTH=1024,
        MEM1_BITWIDTH=32,
        MEM1_DEPTH=1024,
        MEM2_BITWIDTH=256,
        MEM2_DEPTH=1024
    )
    test_main_buffer = MainBuffer(mem_config)

    # Populating the Memory
    test_main_buffer.set_mem0([(2 * i) for i in range(1024)])
    test_main_buffer.set_mem1([(i) for i in range(1024)])
    correct_mem1_value = Bits().join([
        Bits(int=13, length=16),
        Bits(int=13, length=16),
    ])


    # Instruction List
    inst_list = [
         "READ INT16 130 26",
    ]

    # Assembling Instruction
    insts = [assemble_test_instruction(elem) for elem in inst_list]

    # Executing the Instruction
    for elem in insts:
        test_main_buffer.execute_instruction(elem)

    # Extracting Results
    read0 = test_main_buffer.read_mem0_output().uint
    read1 = test_main_buffer.read_mem1_output().uint

    # Reporting Whether the Test Passed or Failed
    if (read0 == 260) and (read1 == correct_mem1_value.uint):
        print("READ INT16 Test Passed.")
        return 0
    else:
        print(f"READ INT16 Test Failed, Read Values Were ({read0}/{test_main_buffer.read_mem0_output()}) and ({read1}/{test_main_buffer.read_mem1_output()}).")
        return 1
    
def test_read_int8() -> int:
     
    mem_config = MainBufferConfiguration(
        MEM0_BITWIDTH=256,
        MEM0_DEPTH=1024,
        MEM1_BITWIDTH=32,
        MEM1_DEPTH=1024,
        MEM2_BITWIDTH=256,
        MEM2_DEPTH=1024
    )
    test_main_buffer = MainBuffer(mem_config)

    # Populating the Memory
    test_main_buffer.set_mem0([(2 * i) for i in range(1024)])
    test_main_buffer.set_mem1([(i) for i in range(1024)])
    correct_mem1_value = Bits().join([
        Bits(int=6, length=8),
        Bits(int=6, length=8),
        Bits(int=6, length=8),
        Bits(int=6, length=8),
    ])


    # Instruction List
    inst_list = [
         "READ INT8 130 24",
    ]

    # Assembling Instruction
    insts = [assemble_test_instruction(elem) for elem in inst_list]

    # Executing the Instruction
    for elem in insts:
        test_main_buffer.execute_instruction(elem)

    # Extracting Results
    read0 = test_main_buffer.read_mem0_output().uint
    read1 = test_main_buffer.read_mem1_output().uint

    # Reporting Whether the Test Passed or Failed
    if (read0 == 260) and (read1 == correct_mem1_value.uint):
        print("READ INT8 Test Passed.")
        return 0
    else:
        print(f"READ INT8 Test Failed, Read Values Were ({read0}/{test_main_buffer.read_mem0_output()}) and ({read1}/{test_main_buffer.read_mem1_output()}).")
        return 1

def test_read_int32() -> int:
     
    mem_config = MainBufferConfiguration(
        MEM0_BITWIDTH=256,
        MEM0_DEPTH=1024,
        MEM1_BITWIDTH=32,
        MEM1_DEPTH=1024,
        MEM2_BITWIDTH=256,
        MEM2_DEPTH=1024
    )
    test_main_buffer = MainBuffer(mem_config)

    # Populating the Memory
    test_main_buffer.set_mem0([(2 * i) for i in range(1024)])
    test_main_buffer.set_mem1([(2 * i) for i in range(1024)])

    # Instruction List
    inst_list = [
         "READ INT32 130 26",
    ]

    # Assembling Instruction
    insts = [assemble_test_instruction(elem) for elem in inst_list]

    # Executing the Instruction
    for elem in insts:
        test_main_buffer.execute_instruction(elem)

    # Extracting Results
    read0 = test_main_buffer.read_mem0_output().uint
    read1 = test_main_buffer.read_mem1_output().uint

    # Reporting Whether the Test Passed or Failed
    if (read0 == 260) and (read1 == 52):
        print("READ INT32 Test Passed.")
        return 0
    else:
        print(f"READ INT32 Test Failed, Read Values Were {read0} and {read1}.")
        return 1
    
def test_write() -> int:
     
    mem_config = MainBufferConfiguration(
        MEM0_BITWIDTH=256,
        MEM0_DEPTH=1024,
        MEM1_BITWIDTH=32,
        MEM1_DEPTH=1024,
        MEM2_BITWIDTH=256,
        MEM2_DEPTH=1024
    )
    test_main_buffer = MainBuffer(mem_config)

    # Populating the Memory
    test_main_buffer.set_mem0([(2 * i) for i in range(mem_config.MEM0_DEPTH)])
    test_main_buffer.set_mem1([(2 * i) for i in range(mem_config.MEM1_DEPTH)])

    # Instruction List
    inst_list = [
         "WRITE 15",
    ]

    # Assembling Instruction
    insts = [assemble_test_instruction(elem) for elem in inst_list]

    # Setting the Output Register
    test_main_buffer.write_mem2_input(Bits(uint=176,length=mem_config.MEM2_BITWIDTH))

    # Executing the Instruction
    for elem in insts:
        test_main_buffer.execute_instruction(elem)

    mem2 = test_main_buffer.read_mem2()

    # Reporting Whether the Test Passed or Failed
    all_correct = True
    for i in range(1024):
        if i == 15:
            all_correct = all_correct and (mem2[i] == 176)
        else:
            all_correct = all_correct and (mem2[i] == 0)
    if all_correct:
        print("WRITE Test Passed.")
        return 0
    else:
        print(f"WRITE Test Failed.")
        return 1

def assemble_test_instruction(
        test_inst_str : str,
        opcode_bitwidth      =2,
        mema_offset_bitwidth =10,
        memb_offset_bitwidth =10
    ) -> MemoryInstruction:
        
        # Instruction Configuration
        inst_config = InstConfig(
            COUNT_BITWIDTH     = 10,
            MEMA_INC_BITWIDTH  = 1,
            MEMB_INC_BITWIDTH  = 1,
            MEMORY_INST_CONFIG = MemoryInstructionConfiguration(
                OPCODE_BITWIDTH      = 2,
                MODE_BITWIDTH        = 2,   
                MEMA_OFFSET_BITWIDTH = 10,
                MEMB_OFFSET_BITWIDTH = 10
            ),
            PE_INST_CONFIG     = ProcessingElementInstructionConfiguration(
                OPCODE_BITWIDTH      = opcode_bitwidth,
                MODE_BITWIDTH        = mema_offset_bitwidth,
                VALUE_BITWIDTH       = memb_offset_bitwidth
            )
        )

        assembler = Assembler(inst_config)
        return assembler.convert_mem_instruction(test_inst_str)

if __name__ == "__main__":
    main()