#--------------------------------------------------------------------
# メイン処理
#--------------------------------------------------------------------
from .element import Element
from .parse import smooth

def run_convert(oracle_code: str) -> str:
    element = Element(oracle_code)
    postgresql_code = smooth(element)
    # Check
    print(element)
    print(postgresql_code)
    return postgresql_code
