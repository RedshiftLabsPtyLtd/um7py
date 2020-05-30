import os.path
import pytest
import struct
from um7py.rsl_generator import RslGenerator


@pytest.fixture
def rsl_generator() -> RslGenerator:
    test_script_path = os.path.dirname(__file__)
    svd_file = os.path.join(test_script_path, os.pardir, os.pardir, './um7py/rsl_xml_svd/um7.svd')
    return RslGenerator(svd_file=svd_file)


@pytest.mark.gen
def test_create_setter_property(rsl_generator: RslGenerator):
    reg = rsl_generator.find_register_by(name='DREG_GYRO_RAW_XY')
    setter_prop = rsl_generator.create_setter_property(reg)
    assert len(setter_prop) > 0, "Setter property is empty!"
    print(setter_prop)


@pytest.mark.gen
def test_create_getter_property(rsl_generator: RslGenerator):
    reg = rsl_generator.find_register_by(name='DREG_HEALTH')
    getter_prop = rsl_generator.create_getter_property(reg)
    assert len(getter_prop) > 0, "Getter property is empty!"
    print(getter_prop)


@pytest.mark.gen
def test_retrieve_payload_description(rsl_generator: RslGenerator):
    reg = rsl_generator.find_register_by(address=0x55)
    payload_description = rsl_generator.retrieve_payload_description(reg)
    assert len(payload_description) > 0, "Payload description is empty!"
    print(payload_description)


@pytest.mark.gen
def test_retrieve_return_description(rsl_generator: RslGenerator):
    reg = rsl_generator.find_register_by(name='DREG_GYRO_RAW_Z')
    return_description = rsl_generator.retrieve_return_description(reg)
    assert len(return_description) > 0, "Return description is empty!"
    print(return_description)


@pytest.mark.gen
def test_get_struct_fmt_for_register_one_short(rsl_generator: RslGenerator):
    reg = rsl_generator.find_register_by(name='DREG_GYRO_RAW_Z')
    ret = rsl_generator.get_struct_fmt_for_register(reg)
    print(ret)
    assert ret == '>hxx', "Interpretted field is incorrect!"


@pytest.mark.gen
def test_get_struct_fmt_for_register_two_shorts(rsl_generator: RslGenerator):
    reg = rsl_generator.find_register_by(name='DREG_GYRO_RAW_XY')
    ret = rsl_generator.get_struct_fmt_for_register(reg)
    print(ret)
    assert ret == '>hh', "Interpreted fields for DREG_GYRO_RAW_XY are incorrect!"


@pytest.mark.gen
def test_get_struct_fmt_for_register_float(rsl_generator: RslGenerator):
    reg = rsl_generator.find_register_by(name='DREG_GYRO_PROC_X')
    ret = rsl_generator.get_struct_fmt_for_register(reg)
    print(ret)
    assert ret == '>f', "Interpreted field is incorrect!"


@pytest.mark.gen
def test_get_struct_fmt_for_register_all(rsl_generator: RslGenerator):
    for reg in rsl_generator.regs:
        fmt = rsl_generator.get_struct_fmt_for_register(reg)
        struct_size = struct.calcsize(fmt)
        assert 0 <= struct_size <= 4, f"\nregister: {reg.name} should not exceed 4, but has size {struct_size}!"


@pytest.mark.gen
def test_interpret_packed_data_1(rsl_generator: RslGenerator):
    reg = rsl_generator.find_register_by(name='DREG_GYRO_RAW_XY')
    ret = rsl_generator.interpret_packed_data(reg)
    print(ret)


@pytest.mark.gen
def test_interpret_packed_data_2(rsl_generator: RslGenerator):
    reg = rsl_generator.find_register_by(name='DREG_GYRO_PROC_Z')
    ret = rsl_generator.interpret_packed_data(reg)
    print(ret)


@pytest.mark.gen
def test_interpret_bitfield(rsl_generator: RslGenerator):
    reg = rsl_generator.find_register_by(name='CREG_COM_RATES1')
    code = rsl_generator.interpret_bitfields(reg)
    print(code)
    assert len(code) > 0, "No code is generated!"


@pytest.mark.gen
def test_generate_props_for_register_map(rsl_generator: RslGenerator):
    generated_code = rsl_generator.generate_props_for_main_register_map()
    print(generated_code)
    assert len(generated_code) > 0, "No code is generated!"
    assert "not implemented" not in generated_code.lower(), "Not implemented should not be in generated code!"


@pytest.mark.gen
def test_get_struct_fmt_for_register_with_gaps(rsl_generator: RslGenerator):
    register_name = 'CREG_COM_RATES2'
    expected_fmt = '>BxxB'
    reg = rsl_generator.find_register_by(name=register_name)
    result = rsl_generator.get_struct_fmt_for_register(reg)
    assert result == expected_fmt, f"INCORRECT struct.fmt for {register_name} expected {expected_fmt}, got {result}"


@pytest.mark.gen
def test_get_struct_fmt_for_register_first_last(rsl_generator: RslGenerator):
    register_name = 'CREG_COM_RATES4'
    expected_fmt = '>xxxB'
    reg = rsl_generator.find_register_by(name=register_name)
    result = rsl_generator.get_struct_fmt_for_register(reg)
    assert result == expected_fmt, f"INCORRECT struct.fmt for {register_name} expected {expected_fmt}, got {result}"


@pytest.mark.gen
def test_get_struct_fmt_for_register_mixed(rsl_generator: RslGenerator):
    register_name = 'CREG_COM_RATES6'
    expected_fmt = '>BxBx'
    reg = rsl_generator.find_register_by(name=register_name)
    result = rsl_generator.get_struct_fmt_for_register(reg)
    assert result == expected_fmt, f"INCORRECT struct.fmt for {register_name} expected {expected_fmt}, got {result}"


@pytest.mark.gen
def test_generated_code_for_combined(rsl_generator: RslGenerator):
    register_name = 'CREG_COM_RATES6'
    register = rsl_generator.find_register_by(name=register_name)
    generated_code = rsl_generator.generate_props_for_register(register)
    print(generated_code)
    assert len(generated_code) > 0, f"No code has been generated for {register_name}"
    assert "not implemented" not in generated_code.lower(), "Not implemented should not be in generated code!"

