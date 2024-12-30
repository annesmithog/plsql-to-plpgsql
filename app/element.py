from app.data_types import *

class Element:
    def __init__(self, oracle_code: str):
        self.tokens = []
        self.procedure_names = []
        self.oracle_code = oracle_code
        self.tokenize()
        # コメント
        self.judge_comment()
        # カテゴリ
        self.set_categories()
        self.set_procedure_categories()
        self.set_declare_categories()
        self.set_output_categories()
        # コード
        self.remove_slash_after_end()
        self.remove_from_dual()
        self.replace_data_types()
        self.replace_is_to_as()
        self.replace_output()
        self.replace_if_contains_concat()
        self.replace_concat_to_comma()
        self.replace_procedure_end()

    def __repr__(self):
        """チェック用"""
        rows = f"{'is_comment'.ljust(12)}{'category'.ljust(20)}{'code'}\n{'-'*100}\n"
        for token in self.tokens:
            is_comment = str(token['is_comment']).ljust(12)
            category = token['category'].ljust(20)
            code = token['code'].replace('\n', '[LB]')
            # code = token['code']
            # スペース, 改行はスルー
            # if not code.strip() == '':
            rows += f"{is_comment}{category}{code}\n"
        return rows

    def tokenize(self) -> None:
        """Oracle SQL コードをトークンに分割します"""
        import re
        pattern = r"(--[^\n]*|/\*.*?\*/|\(|\|\||\)|;|/|:=|=|\.|\*|,|\w+|\n|'[^']*'|\s+)"
        matches = re.findall(pattern, self.oracle_code, flags=re.IGNORECASE | re.DOTALL)
        self.tokens = [{
            "code": match, 
            "category": None, 
            "is_comment": False
        } for match in matches]

    def judge_comment(self) -> None:
        """各トークンのコメントフラグを設定します"""
        for token in self.tokens:
            if token['code'].startswith('--'):
                token['is_comment'] = True
            elif token['code'].startswith('/*'):
                token['is_comment'] = True

    def set_categories(self) -> None:
        """各トークンのカテゴリを設定します"""
        keywords = {
            'SELECT': 'select', 'FROM': 'from', 'WHERE': 'where',
            'INSERT': 'insert', 'UPDATE': 'update', 'DELETE': 'delete',
            'CREATE': 'create', 'PROCEDURE': 'procedure', 'IS': 'is',
            'DECLARE': 'declare', 'BEGIN': 'begin', 'EXCEPTION': 'exception',
            'END': 'end', 
        }
        for token in self.tokens:
            code = token['code']
            if token['is_comment']:
                token['category'] = 'comment'
            elif code.upper() in keywords:
                token['category'] = keywords[token['code'].upper()]
            elif code == ';':
                token['category'] = 'semicolon'
            elif code == '/':
                token['category'] = 'slash'
            else:
                token['category'] = 'identifier'

    def set_procedure_categories(self) -> None:
        """プロシージャのカテゴリを設定します"""
        is_create = False
        is_procedure = False
        is_procedure_name = False
        is_argument = False
        procedure_name = ''
        for i, token in enumerate(self.tokens):
            code = token['code']
            category = token['category']
            if token['is_comment'] or code == ' ' or code == '\n' or code == ',':
                continue
            if category == 'create':
                is_create = True
            elif is_create and category == 'procedure':
                is_create = False
                is_procedure = True
                self.tokens[i]['category'] = 'procedure_start'
                procedure_name = code
            elif is_procedure and category == 'identifier':
                if i+1 < len(self.tokens) and self.tokens[i+1]['code'] == '.':
                    self.tokens[i]['category'] = 'schema'
                else:
                    self.tokens[i]['category'] = 'procedure_name'
                    self.procedure_names.append(code)
                    is_procedure = False
                    is_procedure_name = True
            elif is_procedure_name and code == '(':
                is_procedure_name = False
                is_argument = True
            elif is_argument:
                if category == 'is' or code == ')':
                    is_argument = False
                elif match_data_type(code):
                    self.tokens[i]['category'] = 'data_type'
                else:
                    self.tokens[i]['category'] = 'name'
            elif procedure_name != '' and category == 'end':
                self.tokens[i]['category'] = 'procedure_end'
                procedure_name = ''

    def set_declare_categories(self) -> None:
        """宣言部のカテゴリを設定します"""
        is_declare = False
        is_first_thing = True
        for i, token in enumerate(self.tokens):
            code = token['code']
            category = token['category']
            if token['is_comment'] or code.strip() == '' or code == ',':
                continue
            if category == 'is' or category == 'declare':
                is_declare = True
                is_first_thing = True
            elif code == ';':
                is_first_thing = True
            elif is_declare:
                if category == 'begin':
                    is_declare = False
                elif match_data_type(code):
                    self.tokens[i]['category'] = 'data_type'
                elif is_first_thing:
                    self.tokens[i]['category'] = 'name'
                    is_first_thing = False

    def set_output_categories(self) -> None:
        """出力部のカテゴリを設定します""" 
        is_output = False
        brackets = 0
        for i, token in enumerate(self.tokens):
            if token['is_comment']:
                continue
            code = token['code']
            if code == 'DBMS_OUTPUT':
                is_output = True
                self.tokens[i]['category'] = 'dbms_output'
            elif is_output:
                if code == 'PUT_LINE':
                    self.tokens[i]['category'] = 'put_line'
                elif code == '(':
                    brackets += 1
                    if brackets == 1:
                        self.tokens[i]['category'] = 'output_start'
                elif code == ')':
                    brackets -= 1
                    if brackets == 0:
                        self.tokens[i]['category'] = 'output_end'
                    is_output = False
                elif code == '||':
                    self.tokens[i]['category'] = 'concat'

    def remove_slash_after_end(self) -> None:
        """スラッシュを削除します"""
        is_end = False
        remove_tokens = []
        for i, token in enumerate(self.tokens):
            code = token['code']
            category = token['category']
            if token['is_comment']:
                continue
            elif category == 'end' or category == 'procedure_end':
                is_end = True
            elif is_end:
                if code == '\n':
                    pass
                elif category == 'slash':
                    is_end = False
                    remove_tokens.append(i)
                elif category == 'semicolon':
                    continue
                elif category == 'identifier':
                    if code in self.procedure_names or code.strip() == '':
                        remove_tokens.append(i)
                else:
                    is_end = False

        for remove_token_id in sorted(remove_tokens, reverse=True):
            del self.tokens[remove_token_id]

    def remove_from_dual(self) -> None:
        """`FROM DUAL`を削除します"""
        is_from = False
        is_from_idx = None
        remove_tokens = []
        for i, token in enumerate(self.tokens):
            category = token['category']
            if category == 'from':
                is_from = True
                is_from_idx = i
            elif is_from and token['code'] == 'DUAL':
                remove_tokens.append(i)
                remove_tokens.append(is_from_idx)
                is_from = False
                is_from_idx = None
            elif is_from and category == 'identifier':
                if token['code'].strip() == '' and i+1 < len(self.tokens) and self.tokens[i+1]['code'] == 'DUAL':
                    remove_tokens.append(i)
            else:
                is_from = False
                is_from_idx = None

        for remove_token_id in sorted(remove_tokens, reverse=True):
            del self.tokens[remove_token_id]

    def replace_data_types(self) -> None:
        """データ型を変換します"""
        for i, token in enumerate(self.tokens):
            category = token['category']
            if category == 'data_type':
                self.tokens[i]['code'] = data_types[self.tokens[i]['code']]

    def replace_is_to_as(self) -> None:
        """`IS`を`AS $$`に変換します"""
        for i, token in enumerate(self.tokens):
            category = token['category']
            if category == 'is':
                self.tokens[i]['code'] = 'AS $$\nDECLARE'

    def replace_output(self) -> None:
        """出力形式を変換します"""
        is_dbms_output = False
        for i, token in enumerate(self.tokens):
            category = token['category']
            code = token['code']
            if category == 'dbms_output':
                is_dbms_output = True
                self.tokens[i]['code'] = 'RAISE'
            elif is_dbms_output:
                if code == '.':
                    self.tokens[i]['code'] = ' '
                elif category == 'put_line':
                    is_dbms_output = False
                    self.tokens[i]['code'] = "NOTICE '%', "
    
    def replace_if_contains_concat(self) -> None:
        """concat要素を含む場合、置換する"""
        is_in_output = False
        concat_count = 0
        i_start = float('inf')
        i_end = 0
        remove_tokens = []
        for i, token in enumerate(self.tokens):
            category = token['category']
            if category == 'output_start':
                is_in_output = True
                i_start = i
            elif category == 'output_end':
                is_in_output = False
                i_end = i
                if i_start < i_end:
                    if 0 < concat_count:
                        self.tokens[i_start]['code'] = 'CONCAT('
                        self.tokens[i_end]['code'] = ')'
                        concat_count = 0
                        i_start = float('inf')
                        i_end = 0
                    else:
                        remove_tokens.append(i_start)
                        remove_tokens.append(i_end)
            elif is_in_output:
                if category == 'concat':
                    concat_count += 1
        
        for remove_token_id in sorted(remove_tokens, reverse=True):
            del self.tokens[remove_token_id]

    def replace_concat_to_comma(self) -> None:
        """`||`を`, `に置換する"""
        remove_tokens = []
        for i, token in enumerate(self.tokens):
            category = token['category']
            if category == 'concat':
                self.tokens[i]['code'] = ', '
                if self.tokens[i-1]['code'].strip() == '':
                    remove_tokens.append(i-1)
                if i+1 < len(self.tokens) and self.tokens[i+1]['code'].strip() == '':
                    remove_tokens.append(i+1)

        for remove_token_id in sorted(remove_tokens, reverse=True):
            del self.tokens[remove_token_id]

    def replace_procedure_end(self) -> None:
        is_procedure_start = False
        is_procedure_name = False
        is_procedure_end = False
        is_semicolon = False
        procedure_name = ''
        remove_tokens = []
        for i, token in enumerate(self.tokens):
            code = token['code']
            category = token['category']
            if category == 'procedure_start':
                is_procedure_start = True
            elif is_procedure_start and category == 'procedure_name':
                is_procedure_start = False
                is_procedure_name = True
                procedure_name = code
            elif is_procedure_name and category == 'procedure_end':
                is_procedure_name = False
                is_procedure_end = True
            elif is_procedure_end:
                if code.strip() == '':
                    remove_tokens.append(i)
                elif code == procedure_name:
                    remove_tokens.append(i)
                    procedure_name = ''
                elif category == 'semicolon':
                    is_procedure_end = False
                    is_semicolon = True
            elif is_semicolon and code == '\n':
                self.tokens[i]['code'] += '$$ LANGUAGE plpgsql;\n'
                is_semicolon = False
        for remove_token_id in sorted(remove_tokens, reverse=True):
            del self.tokens[remove_token_id]
