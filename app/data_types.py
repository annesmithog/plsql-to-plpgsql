data_types = {
    "NUMBER": "NUMERIC",
    "VARCHAR2": "VARCHAR",
    "NVARCHAR2": "VARCHAR",
    "DATE": "TIMESTAMP",
    "CLOB": "TEXT",
    "BLOB": "BYTEA",
    "RAW": "BYTEA",
    "LONG": "TEXT"
}

def match_data_type(code: str) -> bool:
    """データ型の場合真を返します"""
    if code in data_types:
        return True
    return None

# def get_data_type(code: str) -> str:
#     """データ型を変換して返します"""
#     return data_types[code]
