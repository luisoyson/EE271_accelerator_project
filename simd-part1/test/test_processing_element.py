from src.processing_element import ProcessingElement, ProcessingElementConfiguration
from src.instruction import ProcessingElementInstruction, ProcessingElementInstructionConfiguration, MemoryInstructionConfiguration, InstConfig
from src.assembler import Assembler
import sys
from bitstring import Bits


def main():

    # Testing Processing Element
    errors = 0
    errors += test_mac_int32()
    errors += test_pass_int32()
    errors += test_rnd_int32()
    errors += test_clr_int32()
    errors += test_mac_int16()
    errors += test_pass_int16()
    errors += test_rnd_int16()
    errors += test_clr_int16()
    errors += test_mac_int8()
    errors += test_pass_int8()
    errors += test_rnd_int8()
    errors += test_clr_int8()

    # Determining the Status of All Tests
    if errors == 0:
        print("All Tests Passed!")
    else:
        print(f"{errors} Tests Failed!")
    sys.exit(errors)


def test_mac_int32() -> int:

    # Creating a Test PE Configuration
    pe_test_config = ProcessingElementConfiguration(
        INPUT_BITWIDTH=32,
        ACCUMULATION_BITWIDTH=(32*2),
        OUTPUT_BITWIDTH=32
    )
    test_pe = ProcessingElement(pe_test_config)

    # Loading the Inputs

    a_value = Bits(int=1073741824,length=32)
    b_value = Bits(int=2,length=32)

    test_pe.input_a(a_value)
    test_pe.input_b(b_value)

    # Instruction List
    inst_list = [
         "MAC INT32",
         "OUT INT32",
    ]

    # Assembling Instruction
    insts = [assemble_test_instruction(elem) for elem in inst_list]

    # Executing the Instruction
    for elem in insts:
        test_pe.execute_instruction(elem)

    # Reporting Whether the Test Passed or Failed
    if test_pe.get_output() == Bits(hex="0x7fffffff", length=32):
        print("INT32 MAC Test Passed.")
        return 0
    else:
        print(f"INT32 MAC Test Failed.  Value was {test_pe.get_output()}")
        return 1
    
def test_pass_int32() -> int:

    # Creating a Test PE Configuration
    pe_test_config = ProcessingElementConfiguration(
        INPUT_BITWIDTH=32,
        ACCUMULATION_BITWIDTH=(32*2),
        OUTPUT_BITWIDTH=32
    )
    test_pe = ProcessingElement(pe_test_config)

    # Loading the Inputs
    a_value = Bits(int=15,length=32)
    b_value = Bits(int=-6,length=32)

    test_pe.input_a(a_value)
    test_pe.input_b(b_value)

    # Instruction List
    inst_list = [
         "PASS INT32",
         "OUT INT32",
    ]

    # Assembling Instruction
    insts = [assemble_test_instruction(elem) for elem in inst_list]

    # Executing the Instruction
    for elem in insts:
        test_pe.execute_instruction(elem)

    # Reporting Whether the Test Passed or Failed
    if test_pe.get_output() == Bits(hex="0x0000000f", length=32):
        print("INT32 PASS Test Passed.")
        return 0
    else:
        print(f"INT32 PASS Test Failed. Value Was {test_pe.get_output()}.")
        return 1
    
def test_rnd_int32() -> int:

    # Creating a Test PE Configuration
    pe_test_config = ProcessingElementConfiguration(
        INPUT_BITWIDTH=32,
        ACCUMULATION_BITWIDTH=(32*2),
        OUTPUT_BITWIDTH=32
    )
    test_pe = ProcessingElement(pe_test_config)

    # Loading the Inputs
    a_value = Bits(int=15,length=32)
    b_value = Bits(int=-6,length=32)

    test_pe.input_a(a_value)
    test_pe.input_b(b_value)

    # Instruction List
    inst_list = [
         "PASS INT32",
         "RND INT32 2",
         "OUT INT32",
    ]

    # Assembling Instruction
    insts = [assemble_test_instruction(elem) for elem in inst_list]

    # Executing the Instruction
    for elem in insts:
        test_pe.execute_instruction(elem)

    # Reporting Whether the Test Passed or Failed
    if test_pe.get_output() == Bits(hex="0x00000004", length=32):
        print("INT32 RND Test Passed.")
        return 0
    else:
        print(f"INT32 RND Test Failed. Value Was {test_pe.get_output()}.")
        return 1

def test_clr_int32() -> int:

    # Creating a Test PE Configuration
    pe_test_config = ProcessingElementConfiguration(
        INPUT_BITWIDTH=32,
        ACCUMULATION_BITWIDTH=(32*2),
        OUTPUT_BITWIDTH=32
    )
    test_pe = ProcessingElement(pe_test_config)

    # Loading the Inputs
    a_value = Bits(int=15,length=32)
    b_value = Bits(int=-6,length=32)

    test_pe.input_a(a_value)
    test_pe.input_b(b_value)

    # Instruction List
    inst_list = [
         "MAC INT32",
         "OUT INT32",
         "CLR INT32"
    ]

    # Assembling Instruction
    insts = [assemble_test_instruction(elem) for elem in inst_list]

    # Executing the Instruction
    for elem in insts:
        test_pe.execute_instruction(elem)

    # Reporting Whether the Test Passed or Failed
    if (test_pe.get_output() == Bits(uint=0, length=32)) and (test_pe.get_accumulation() == Bits(uint=0, length=64)):
        print("INT32 CLR Test Passed.")
        return 0
    else:
        print(f"INT32 CLR Test Failed.  Value was {test_pe.get_output()}")
        return 1


def test_mac_int16() -> int:

    # Creating a Test PE Configuration
    pe_test_config = ProcessingElementConfiguration(
        INPUT_BITWIDTH=32,
        ACCUMULATION_BITWIDTH=(32*2),
        OUTPUT_BITWIDTH=32
    )
    test_pe = ProcessingElement(pe_test_config)

    # Loading the Inputs

    a_value = Bits().join([
        Bits(int=-20000,length=16),
        Bits(int=20000,length=16)
    ])
    b_value = Bits().join([
        Bits(int=2,length=16),
        Bits(int=2,length=16)
    ])

    test_pe.input_a(a_value)
    test_pe.input_b(b_value)

    # Instruction List
    inst_list = [
         "MAC INT16",
         "OUT INT16",
    ]

    # Assembling Instruction
    insts = [assemble_test_instruction(elem) for elem in inst_list]

    # Executing the Instruction
    for elem in insts:
        test_pe.execute_instruction(elem)

    # Reporting Whether the Test Passed or Failed
    if test_pe.get_output() == Bits(hex="0x80007fff", length=32):
        print("INT16 MAC Test Passed.")
        return 0
    else:
        print(f"INT16 MAC Test Failed.  Value was {test_pe.get_output()}")
        return 1
    
def test_pass_int16() -> int:

    # Creating a Test PE Configuration
    pe_test_config = ProcessingElementConfiguration(
        INPUT_BITWIDTH=32,
        ACCUMULATION_BITWIDTH=(32*2),
        OUTPUT_BITWIDTH=32
    )
    test_pe = ProcessingElement(pe_test_config)

    # Loading the Inputs

    a_value = Bits().join([
        Bits(int=-15,length=16),
        Bits(int=7,length=16)
    ])
    b_value = Bits().join([
        Bits(int=8,length=16),
        Bits(int=3,length=16)
    ])

    test_pe.input_a(a_value)
    test_pe.input_b(b_value)

    # Instruction List
    inst_list = [
         "PASS INT16",
         "OUT INT16",
    ]

    # Assembling Instruction
    insts = [assemble_test_instruction(elem) for elem in inst_list]

    # Executing the Instruction
    for elem in insts:
        test_pe.execute_instruction(elem)

    # Reporting Whether the Test Passed or Failed
    if test_pe.get_output() == Bits(hex="0xfff10007", length=32):
        print("INT16 PASS Test Passed.")
        return 0
    else:
        print(f"INT16 PASS Test Failed, Value Was {test_pe.get_output()}.")
        return 1
    
def test_rnd_int16() -> int:

    # Creating a Test PE Configuration
    pe_test_config = ProcessingElementConfiguration(
        INPUT_BITWIDTH=32,
        ACCUMULATION_BITWIDTH=(32*2),
        OUTPUT_BITWIDTH=32
    )
    test_pe = ProcessingElement(pe_test_config)

    # Loading the Inputs

    a_value = Bits().join([
        Bits(hex="ABCD",length=16),
        Bits(hex="EF00",length=16)
    ])
    b_value = Bits().join([
        Bits(int=8,length=16),
        Bits(int=3,length=16)
    ])

    test_pe.input_a(a_value)
    test_pe.input_b(b_value)

    # Instruction List
    inst_list = [
         "PASS INT16",
         "RND INT16 8",
         "OUT INT16",
    ]

    # Assembling Instruction
    insts = [assemble_test_instruction(elem) for elem in inst_list]

    # Executing the Instruction
    for elem in insts:
        test_pe.execute_instruction(elem)

    # Reporting Whether the Test Passed or Failed
    if test_pe.get_output() == Bits(hex="0xffACffEF", length=32):
        print("INT16 RND Test Passed.")
        return 0
    else:
        print(f"INT16 RND Test Failed. Value Was {test_pe.get_output()}.")
        return 1

def test_clr_int16() -> int:

    # Creating a Test PE Configuration
    pe_test_config = ProcessingElementConfiguration(
        INPUT_BITWIDTH=32,
        ACCUMULATION_BITWIDTH=(32*2),
        OUTPUT_BITWIDTH=32
    )
    test_pe = ProcessingElement(pe_test_config)

    # Loading the Inputs

    a_value = Bits().join([
        Bits(int=-15,length=16),
        Bits(int=7,length=16)
    ])
    b_value = Bits().join([
        Bits(int=8,length=16),
        Bits(int=3,length=16)
    ])

    test_pe.input_a(a_value)
    test_pe.input_b(b_value)

    # Instruction List
    inst_list = [
         "MAC INT16",
         "OUT INT16",
         "CLR INT16"
    ]

    # Assembling Instruction
    insts = [assemble_test_instruction(elem) for elem in inst_list]

    # Executing the Instruction
    for elem in insts:
        test_pe.execute_instruction(elem)

    # Reporting Whether the Test Passed or Failed
    if (test_pe.get_output() == Bits(uint=0, length=32)) and (test_pe.get_accumulation() == Bits(uint=0, length=64)):
        print("INT16 CLR Test Passed.")
        return 0
    else:
        print(f"INT16 CLR Test Failed.  Value was {test_pe.get_output()}")
        return 1


def test_mac_int8() -> int:

    # Creating a Test PE Configuration
    pe_test_config = ProcessingElementConfiguration(
        INPUT_BITWIDTH=32,
        ACCUMULATION_BITWIDTH=(32*2),
        OUTPUT_BITWIDTH=32
    )
    test_pe = ProcessingElement(pe_test_config)

    # Loading the Inputs
    a_value = Bits().join([
        Bits(int=100,length=8),
        Bits(int=-100,length=8),
        Bits(int=3,length=8),
        Bits(int=-3,length=8),
    ])
    b_value = Bits().join([
        Bits(int=2,length=8),
        Bits(int=2,length=8),
        Bits(int=-8,length=8),
        Bits(int=-8,length=8),
    ])

    test_pe.input_a(a_value)
    test_pe.input_b(b_value)

    # Instruction List
    inst_list = [
         "MAC INT8",
         "OUT INT8",
    ]

    # Assembling Instruction
    insts = [assemble_test_instruction(elem) for elem in inst_list]

    # Executing the Instruction
    for elem in insts:
        test_pe.execute_instruction(elem)

    # Reporting Whether the Test Passed or Failed
    if test_pe.get_output() == Bits(hex="0x7f80e818", length=32):
        print("INT8 MAC Test Passed.")
        return 0
    else:
        print(f"INT8 MAC Test Failed.  Value was {test_pe.get_output()}")
        return 1
    
def test_pass_int8() -> int:

    # Creating a Test PE Configuration
    pe_test_config = ProcessingElementConfiguration(
        INPUT_BITWIDTH=32,
        ACCUMULATION_BITWIDTH=(32*2),
        OUTPUT_BITWIDTH=32
    )
    test_pe = ProcessingElement(pe_test_config)

    # Loading the Inputs
    a_value = Bits().join([
        Bits(int=5,length=8),
        Bits(int=-5,length=8),
        Bits(int=3,length=8),
        Bits(int=-3,length=8),
    ])
    b_value = Bits().join([
        Bits(int=10,length=8),
        Bits(int=10,length=8),
        Bits(int=-8,length=8),
        Bits(int=-8,length=8),
    ])

    test_pe.input_a(a_value)
    test_pe.input_b(b_value)

    # Instruction List
    inst_list = [
         "PASS INT8",
         "OUT INT8",
    ]

    # Assembling Instruction
    insts = [assemble_test_instruction(elem) for elem in inst_list]

    # Executing the Instruction
    for elem in insts:
        test_pe.execute_instruction(elem)

    # Reporting Whether the Test Passed or Failed
    if test_pe.get_output() == Bits(hex="0x05fb03fd", length=32):
        print("INT8 PASS Test Passed.")
        return 0
    else:
        print(f"INT8 PASS Test Failed, Value Was {test_pe.get_output()}.")
        return 1
    
def test_rnd_int8() -> int:

    # Creating a Test PE Configuration
    pe_test_config = ProcessingElementConfiguration(
        INPUT_BITWIDTH=32,
        ACCUMULATION_BITWIDTH=(32*2),
        OUTPUT_BITWIDTH=32
    )
    test_pe = ProcessingElement(pe_test_config)

    # Loading the Inputs
    a_value = Bits().join([
        Bits(int=5,length=8),
        Bits(int=-5,length=8),
        Bits(int=3,length=8),
        Bits(int=-3,length=8),
    ])
    b_value = Bits().join([
        Bits(int=10,length=8),
        Bits(int=10,length=8),
        Bits(int=-8,length=8),
        Bits(int=-8,length=8),
    ])

    test_pe.input_a(a_value)
    test_pe.input_b(b_value)

    # Instruction List
    inst_list = [
         "PASS INT8",
         "RND INT8 1",
         "OUT INT8",
    ]

    # Assembling Instruction
    insts = [assemble_test_instruction(elem) for elem in inst_list]

    # Executing the Instruction
    for elem in insts:
        test_pe.execute_instruction(elem)

    # Reporting Whether the Test Passed or Failed
    if test_pe.get_output() == Bits(hex="0x02fe02fe", length=32):
        print("INT8 RND Test Passed.")
        return 0
    else:
        print(f"INT8 RND Test Failed, Value Was {test_pe.get_output()}.")
        return 1

def test_clr_int8() -> int:

    # Creating a Test PE Configuration
    pe_test_config = ProcessingElementConfiguration(
        INPUT_BITWIDTH=32,
        ACCUMULATION_BITWIDTH=(32*2),
        OUTPUT_BITWIDTH=32
    )
    test_pe = ProcessingElement(pe_test_config)

    # Loading the Inputs
    a_value = Bits().join([
        Bits(int=5,length=8),
        Bits(int=-5,length=8),
        Bits(int=3,length=8),
        Bits(int=-3,length=8),
    ])
    b_value = Bits().join([
        Bits(int=10,length=8),
        Bits(int=10,length=8),
        Bits(int=-8,length=8),
        Bits(int=-8,length=8),
    ])

    test_pe.input_a(a_value)
    test_pe.input_b(b_value)

    # Instruction List
    inst_list = [
         "MAC INT8",
         "OUT INT8",
         "CLR INT8"
    ]

    # Assembling Instruction
    insts = [assemble_test_instruction(elem) for elem in inst_list]

    # Executing the Instruction
    for elem in insts:
        test_pe.execute_instruction(elem)

    # Reporting Whether the Test Passed or Failed
    if (test_pe.get_output() == Bits(uint=0, length=32)) and (test_pe.get_accumulation() == Bits(uint=0, length=64)):
        print("INT8 CLR Test Passed.")
        return 0
    else:
        print(f"INT8 CLR Test Failed.  Value was {test_pe.get_output()}")
        return 1


def assemble_test_instruction(
        test_inst_str : str,
        opcode_bitwidth=2,
        mode_bitwidth=2,
        value_bitwidth=5
    ) -> ProcessingElementInstruction:
        
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
                MODE_BITWIDTH        = mode_bitwidth,
                VALUE_BITWIDTH       = value_bitwidth
            )
        )

        assembler = Assembler(inst_config)
        return assembler.convert_pe_instruction(test_inst_str)

if __name__ == "__main__":
    main()