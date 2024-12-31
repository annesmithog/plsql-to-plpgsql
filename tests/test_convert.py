from app.convert import run_convert

def test_select1():
    with open('app/examples/oracle/select.plb', 'r') as f:
        ora = f.read()
    with open('app/examples/postgres/select.pgsql', 'r') as f:
        pos = f.read()
    assert run_convert(ora) == pos

def test_from_dual():
    with open('app/examples/oracle/select_from_dual.plb', 'r') as f:
        ora = f.read()
    with open('app/examples/postgres/select_from_dual.pgsql', 'r') as f:
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
    with open('app/examples/oracle/create_tables.plb', 'r') as f:
        ora = f.read()
    with open('app/examples/postgres/create_tables.pgsql', 'r') as f:
        pos = f.read()
    assert run_convert(ora) == pos

def test_create_employees():
    with open('app/examples/oracle/insert_tables.plb', 'r') as f:
        ora = f.read()
    with open('app/examples/postgres/insert_tables.pgsql', 'r') as f:
        pos = f.read()
    assert run_convert(ora) == pos

def test_create_employees():
    with open('app/examples/oracle/create_function.plb', 'r') as f:
        ora = f.read()
    with open('app/examples/postgres/create_function.pgsql', 'r') as f:
        pos = f.read()
    assert run_convert(ora) == pos

def test_exception():
    with open('app/examples/oracle/exception.plb', 'r') as f:
        ora = f.read()
    with open('app/examples/postgres/exception.pgsql', 'r') as f:
        pos = f.read()
    assert run_convert(ora) == pos







# TODO
# def test_cursor():
#     with open('app/examples/oracle/cursor.plb', 'r') as f:
#         ora = f.read()
#     with open('app/examples/postgres/cursor.pgsql', 'r') as f:
#         pos = f.read()
#     assert run_convert(ora) == pos
