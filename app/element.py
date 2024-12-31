import re
from app.data_types import *
from app.exception_types import *

INF = float('inf')

class Element:
    def __init__(self, oracle_code: str):
        self.tokens = []
        self.procedure_names = []
        self.function_names = []
        self.oracle_code = oracle_code
        # code を設定
        self.tokenize()
        # is_comment を設定
        self.judge_comment()
        # category を設定
        self.set_categories()
        # 修正
        self.replace_data_types()
        self.replace_exceptions()
        self.delete_from_dual()
        self.replace_is_to_as()
        self.replace_output()
        self.replace_output_concat()
        self.delete_procedure_name_after_end(is_procedure=True)
        self.delete_procedure_name_after_end(is_procedure=False)
        self.replace_slash_after_semicolon_to_empty_text()
        self.add_plpgsql_after_procedure_end(is_procedure=True)
        self.add_plpgsql_after_procedure_end(is_procedure=False)
        self.set_procedure_with_no_arguments(is_procedure=True)
        self.set_procedure_with_no_arguments(is_procedure=False)
        self.replace_return_to_returns()
        self.replace_systimestamp()

    def __repr__(self):
        """チェック用"""
        rows = f"{'is_comment'.ljust(12)}{'category'.ljust(20)}{'code'}\n{'-'*100}\n"
        for token in self.tokens:
            is_comment = str(token['is_comment']).ljust(12)
            category = token['category'].ljust(20)
            code = token['code'].replace('\n', '[LINE BREAK]')
            # スペース, 改行はスルー
            # if not code.strip() == '':
            rows += f"{is_comment}{category}`{code}`\n"
        return rows

    def tokenize(self) -> None:
        """Oracle SQL コードをトークンに分割します"""
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
            if token['code'].startswith(('--', '/*')):
                token['is_comment'] = True

    def set_categories(self) -> None:
        """各トークンのカテゴリを設定します"""
        keywords = [
            'SELECT', 'FROM', 'INTO', 'WHERE', 'INSERT', 'UPDATE', 'DELETE',
            'CREATE', 'PROCEDURE', 'IS', 'DECLARE', 'BEGIN', 'EXCEPTION',
            'END', 'DUAL', 'DBMS_OUTPUT', 'PUT_LINE', 'OR', 'REPLACE', 
            'VALUES', 'FUNCTION', 'RETURN', 
        ]
        before_category = None
        is_procedure = False
        is_procedure_name_zone = False
        is_function = False
        is_function_name_zone = False
        for token in self.tokens:
            code = token['code']
            if token['is_comment']:
                token['category'] = 'comment'
                continue
            match code:
                case ';': token['category'] = 'semicolon'
                case '/': token['category'] = 'slash'
                case '||': token['category'] = 'concat'
                case _:   token['category'] = 'identifier'
            if code.upper() in keywords:
                token['category'] = code.lower()
            if match_data_type(code):
                token['category'] = 'data_type'
            if match_exception_type(code):
                token['category'] = 'exception_type'
            for procedure_name in self.procedure_names:
                if procedure_name == code:
                    token['category'] = 'procedure_name'
            for function_name in self.function_names:
                if function_name == code:
                    token['category'] = 'function_name'

            if token['category'] == 'identifier':
                """
                identifier
                """
                if before_category == 'procedure_start' and code.strip() != '' and code != '\n':
                    if is_procedure_name_zone:
                        if token['category'] == 'is' or code == '(':
                            is_procedure_name_zone = False
                        else:
                            token['category'] = 'procedure_name'
                            self.procedure_names.append(code)
                if before_category == 'function_start' and code.strip() != '' and code != '\n':
                    if is_function_name_zone:
                        if token['category'] == 'is' or code == '(':
                            is_function_name_zone = False
                        else:
                            token['category'] = 'function_name'
                            self.function_names.append(code)
            else:
                """
                identifier以外
                """
                if token['category'] == 'procedure':
                    is_procedure = True
                    is_procedure_name_zone = True
                    token['category'] = 'procedure_start'
                if is_procedure and token['category'] == 'end':
                    is_procedure = False
                    token['category'] = 'procedure_end'
                if token['category'] == 'function':
                    is_function = True
                    is_function_name_zone = True
                    token['category'] = 'function_start'
                if is_function and token['category'] == 'end':
                    is_function = False
                    token['category'] = 'function_end'
                # 以前のカテゴリを設定
                before_category = token['category']

    def delete_tokens(self, remove_indices) -> None:
        """トークンを削除します"""
        for remove_index in sorted(remove_indices, reverse=True):
            del self.tokens[remove_index]

    def replace_data_types(self) -> None:
        """データ型を置換します"""
        for token in self.tokens:
            if token['category'] == 'data_type':
                token['code'] = data_types[token['code']]

    def replace_exceptions(self) -> None:
        """例外を置換します"""
        for token in self.tokens:
            if token['category'] == 'exception_type':
                print(token['code'])
                token['code'] = exception_types[token['code']]

    def delete_from_dual(self) -> None:
        """`FROM DUAL`を削除します"""
        remove_indices = []
        i_start = INF
        i_end = 0
        before_category = None
        for i, token in enumerate(self.tokens):
            category = token['category']
            if category == 'comment' or category == 'identifier':
                continue
            if category == 'from':
                i_start = i
            if before_category == 'from' and category == 'dual':
                i_end = i
                for x in range(i_start, i_end + 1):
                    remove_indices.append(x)
                i_start = INF
                i_end = 0
            before_category = category
        self.delete_tokens(remove_indices)

    def replace_is_to_as(self) -> None:
        """`IS`を`AS $$ DECLARE`に置換します"""
        for token in self.tokens:
            if token['category'] == 'is':
                token['code'] = 'AS $$\nDECLARE'

    def replace_output(self) -> None:
        """出力形式を置換します"""
        output_step = 0
        for token in self.tokens:
            category = token['category']
            if category == 'comment':
                continue
            elif category == 'dbms_output':
                output_step = 1
            elif output_step == 1 and token['code'] == '.':
                output_step = 2
            elif category == 'put_line':
                output_step = 3
            else:
                output_step = 0
            match output_step:
                case 1: token['code'] = 'RAISE'
                case 2: token['code'] = ' '
                case 3: token['code'] = "NOTICE '%', "

    def replace_output_concat(self) -> None:
        """出力で結合演算子を使用している場合、置換して形式を合わせる"""
        is_output = False
        bracket_count = 0
        bracket_start = None
        concat_indices = []
        remove_indices = []
        for i, token in enumerate(self.tokens):
            category = token['category']
            match category:
                case 'comment': continue
                case 'put_line': is_output = True
                case 'procedure_end': is_output = False
                case 'concat': concat_indices.append(i)
            if is_output:
                code = token['code']
                match code:
                    case '(':
                        if bracket_count == 0:
                            bracket_start = i
                        bracket_count += 1
                    case ')':
                        bracket_count -= 1
                        if bracket_count == 0:
                            if len(concat_indices) > 0:
                                self.tokens[bracket_start]['code'] = 'CONCAT('
                                for concat_index in concat_indices:
                                    self.tokens[concat_index]['code'] = ','
                                    if self.tokens[concat_index - 1]['code'].strip() == '':
                                        self.tokens[concat_index - 1]['code'] = ''
                            else:
                                self.tokens[bracket_start]['code'] = ''
                                self.tokens[i]['code'] = ''
                            bracket_count = 0
                            bracket_start = None
                            concat_indices = []
                            is_output = False
            self.delete_tokens(remove_indices)

    def delete_procedure_name_after_end(self, *, is_procedure: bool) -> None:
        """END直後のプロシージャ名を削除します"""
        if is_procedure:
            name = 'procedure_name'
            end = 'procedure_end'
        else:
            name = 'function_name'
            end = 'function_end'
        remove_indices = []
        before_category = ''
        for i, token in enumerate(self.tokens):
            category = token['category']
            if category == 'comment' or category == 'identifier':
                continue
            elif category == name and before_category == end:
                if self.tokens[i - 1]['code'].strip() == '':
                    remove_indices.append(i - 1)
                remove_indices.append(i)
            else:
                before_category = category
        self.delete_tokens(remove_indices)

    def replace_slash_after_semicolon_to_empty_text(self) -> None:
        """`;`直後の`/`を空文字に置換します"""
        before_category = ''
        for i, token in enumerate(self.tokens):
            category = token['category']
            if category == 'comment' or category == 'identifier':
                continue
            elif category == 'slash' and before_category == 'semicolon':
                self.tokens[i]['code'] = ''
            else:
                before_category = category

    def add_plpgsql_after_procedure_end(self, *, is_procedure: bool) -> None:
        """procedure_end直後に言語文言を追加します"""
        step = 0 # 1: ***_end, 2: semicolon, 
        if is_procedure:
            end = 'procedure_end'
        else:
            end = 'function_end'

        for token in self.tokens:
            category = token['category']
            if category == 'comment':
                continue
            elif category == 'identifier':
                if token['code'] == '\n' and step == 2:
                    token['code'] += '$$ LANGUAGE plpgsql;'
                    step = 0
            elif category == end:
                step = 1
            elif category == 'semicolon' and step == 1:
                step = 2
            else:
                step = 0

    def set_procedure_with_no_arguments(self, *, is_procedure: bool) -> None:
        """引数を持たないプロシージャに括弧を追加します"""
        if is_procedure:
            start = 'procedure_start'
            name = 'procedure_name'
        else:
            start = 'function_start'
            name = 'function_name'
        step = 0
        procedure_name_index = INF
        bracket_start_count = 0
        for i, token in enumerate(self.tokens):
            category = token['category']
            if category == 'comment':
                continue
            elif step == 0 and category == start:
                step = 1
            elif step == 1 and category == name:
                step = 2
                procedure_name_index = i
            elif step == 2:
                if token['code'] == '(':
                    bracket_start_count += 1
                if category == 'is':
                    if bracket_start_count == 0:
                        self.tokens[procedure_name_index + 1]['code'] = '() '
                    bracket_start_count = 0
                    procedure_name_index = INF
            elif category == 'identifier':
                continue
            else:
                step = 0

    def replace_return_to_returns(self) -> None:
        """function宣言内の`RETURN`を`RETURNS`に置換します"""
        is_function = False
        for token in self.tokens:
            category = token['category']
            match category:
                case 'function_start': is_function = True
                case 'is': is_function = False
                case 'return':
                    if is_function:
                        token['code'] = 'RETURNS';

    def replace_systimestamp(self) -> None:
        for token in self.tokens:
            if token['category'] == 'comment':
                continue
            if token['code'].upper() == 'SYSTIMESTAMP':
                token['code'] = 'current_timestamp'
                
            
