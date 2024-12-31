from app.convert import run_convert

def test_select1():
    with open('app/examples/oracle/select1.plb', 'r') as f:
        ora = f.read()
    with open('app/examples/postgres/select1.pgsql', 'r') as f:
        pos = f.read()
    assert run_convert(ora) == pos

def test_from_dual():
    with open('app/examples/oracle/from_dual.plb', 'r') as f:
        ora = f.read()
    with open('app/examples/postgres/from_dual.pgsql', 'r') as f:
        pos = f.read()
    assert run_convert(ora) == pos

def test_create_procedure():
    with open('app/examples/oracle/create_procedure.plb', 'r') as f:
        ora = f.read()
    with open('app/examples/postgres/create_procedure.pgsql', 'r') as f:
        pos = f.read()
    assert run_convert(ora) == pos

def test_declaration():
    with open('app/examples/oracle/declaration.plb', 'r') as f:
        ora = f.read()
    with open('app/examples/postgres/declaration.pgsql', 'r') as f:
        pos = f.read()
    assert run_convert(ora) == pos

def test_create_employees():
    with open('app/examples/oracle/create_employees.plb', 'r') as f:
        ora = f.read()
    with open('app/examples/postgres/create_employees.pgsql', 'r') as f:
        pos = f.read()
    assert run_convert(ora) == pos

def test_create_employees():
    with open('app/examples/oracle/insert_employees.plb', 'r') as f:
        ora = f.read()
    with open('app/examples/postgres/insert_employees.pgsql', 'r') as f:
        pos = f.read()
    assert run_convert(ora) == pos

def test_create_employees():
    with open('app/examples/oracle/create_function.plb', 'r') as f:
        ora = f.read()
    with open('app/examples/postgres/create_function.pgsql', 'r') as f:
        pos = f.read()
    assert run_convert(ora) == pos









# TODO
# def test_cursor():
#     with open('app/examples/oracle/cursor.plb', 'r') as f:
#         ora = f.read()
#     with open('app/examples/postgres/cursor.pgsql', 'r') as f:
#         pos = f.read()
#     assert run_convert(ora) == pos
