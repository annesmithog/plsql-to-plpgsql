from app.convert import run_convert

def test_normal_select():
    oracle = 'SELECT id FROM employees;'
    assert run_convert(oracle) == oracle

def test_from_dual():
    with open('app/examples/oracle/from_dual.sql', 'r') as f:
        ora = f.read()
    with open('app/examples/postgres/from_dual.sql', 'r') as f:
        pos = f.read()
    assert run_convert(ora) == pos

def test_select1():
    with open('app/examples/oracle/select1.sql', 'r') as f:
        ora = f.read()
    with open('app/examples/postgres/select1.sql', 'r') as f:
        pos = f.read()
    assert run_convert(ora) == pos

def test_basic_structure():
    with open('app/examples/oracle/basic_structure.sql', 'r') as f:
        ora = f.read()
    with open('app/examples/postgres/basic_structure.sql', 'r') as f:
        pos = f.read()
    assert run_convert(ora) == pos

def test_declaration():
    with open('app/examples/oracle/declaration.sql', 'r') as f:
        ora = f.read()
    with open('app/examples/postgres/declaration.sql', 'r') as f:
        pos = f.read()
    assert run_convert(ora) == pos
