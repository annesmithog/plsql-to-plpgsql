keywords = [
    'SELECT', 
    'FROM', 
    'INTO', 
    'WHERE', 
    'INSERT', 
    'UPDATE', 
    'DELETE',
    'CREATE', 
    'PROCEDURE', 
    'IS', 
    'DECLARE', 
    'BEGIN', 
    'EXCEPTION',
    'END', 
    'DUAL', 
    'DBMS_OUTPUT', 
    'PUT_LINE', 
    'OR', 
    'REPLACE', 
    'VALUES', 
    'FUNCTION', 
    'RETURN', 
]

def match_keyword(code: str) -> bool:
    """キーワードの場合真を返します"""
    if code in keywords:
        return True
    return None
