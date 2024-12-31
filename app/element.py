import re
from app.keywords import *
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
        self.set_methods_category(is_procedure=True)
        self.set_methods_category(is_procedure=False)
        # 修正
        self.replace_data_types()
        self.replace_exceptions()
        self.delete_from_dual()
        self.replace_systimestamp()
        self.replace_is_to_as()
        self.replace_output()
        self.replace_concat()
        self.delete_output_brackets_if_not_concat()
        self.replace_slash_after_semicolon_to_empty_text()
        if len(self.procedure_names) > 0:
            self.delete_method_name_after_end(is_procedure=True)
            self.add_plpgsql_after_method_end(is_procedure=True)
            self.add_method_bracket_with_no_arguments(is_procedure=True)
        if len(self.function_names) > 0:
            self.delete_method_name_after_end(is_procedure=False)
            self.add_plpgsql_after_method_end(is_procedure=False)
            self.add_method_bracket_with_no_arguments(is_procedure=False)
        self.replace_return_to_returns()

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

    def ignore(self, category):
        """修正対象でないカテゴリである場合真を返します"""
        match category:
            case 'comment':     return True
            case 'whitespace':  return True
            case 'line_break':  return True
            case _:             return False

    def delete_tokens(self, delete_indices) -> None:
        """トークンを削除します"""
        for delete_index in sorted(delete_indices, reverse=True):
            del self.tokens[delete_index]

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
        for token in self.tokens:
            if token['is_comment']: 
                token['category'] = 'comment' 
                continue
            code = token['code']
            match code:
                case '||': token['category'] = 'concat'
                case ';': token['category'] = 'semicolon'
                case '/': token['category'] = 'slash'
                case '(': token['category'] = 'bracket_start'
                case ')': token['category'] = 'bracket_end'
                case ',': token['category'] = 'comma'
                case '.': token['category'] = 'dot'
                case _: token['category'] = 'identifier'
            if code == '\n':
                token['category'] = 'line_break'
            elif code.strip() == '':
                token['category'] = 'whitespace'
            elif match_keyword(code.upper()):
                token['category'] = code.lower()
            elif match_data_type(code):
                token['category'] = 'data_type'
            elif match_exception_type(code):
                token['category'] = 'exception_type'

    def set_methods_category(self, *, is_procedure: bool) -> None:
        """メソッド関連のカテゴリを設定します"""
        if is_procedure:
            method_type = 'procedure' 
        else:
            method_type = 'function'
        is_method = False
        before_category = None
        for token in self.tokens:
            category = token['category']
            if self.ignore(category): continue
            if before_category == method_type + '_start':
                token['category'] = method_type + '_name'
                code = token['code']
                if is_procedure:
                    self.procedure_names.append(code)
                else:
                    self.function_names.append(code)
            if category == 'end' and is_method:
                token['category'] = method_type + '_end'
                is_method = False
            if category == method_type:
                is_method = True
                token['category'] = method_type + '_start'
            before_category = token['category']
            
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
        from_index = INF
        delete_indices = []
        for i, token in enumerate(self.tokens):
            category = token['category']
            if self.ignore(category): 
                continue
            else:
                if category == 'from':
                    from_index = i
                elif category == 'dual':
                    for idx in range(from_index, i + 1):
                        delete_indices.append(idx)
                    from_index = INF
                else:
                    from_index = INF
        self.delete_tokens(delete_indices)

    def replace_systimestamp(self) -> None:
        """`systimestamp` to `current_timestamp`"""
        for token in self.tokens:
            if self.ignore(token['category']):continue
            if token['code'].upper() == 'SYSTIMESTAMP':
                token['code'] = 'current_timestamp'
                
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
            if self.ignore(category): continue
            if output_step == 0 and category == 'dbms_output':
                output_step = 1
            elif output_step == 1 and category == 'dot':
                output_step = 2
            elif output_step == 2 and category == 'put_line':
                output_step = 3
            else:
                output_step = 0
            match output_step:
                case 1: token['code'] = 'RAISE'
                case 2: 
                    token['code'] = ' '
                    token['category'] = 'whitespace'
                case 3: token['code'] = "NOTICE '%', "

    def replace_concat(self) -> None:
        """結合演算子を使用している場合置換する"""
        delete_indices = []
        for i, token in enumerate(self.tokens):
            category = token['category']
            if self.ignore(category): continue
            if category == 'concat':
                minus = 1
                while self.tokens[i - minus]['category'] == 'identifier' or self.ignore(self.tokens[i - minus]['category']):
                    minus += 1
                plus = 0
                self.tokens[i - minus + plus]['code'] = 'CONCAT('
                while self.tokens[i - minus + plus]['category'] == 'identifier'   or \
                      self.ignore(self.tokens[i - minus + plus]['category'])      or \
                      self.tokens[i - minus + plus]['category'] == 'concat'       or \
                      self.tokens[i - minus + plus]['category'] != 'bracket_end':
                            plus += 1
                            if self.tokens[i - minus + plus]['code'].strip() == '':
                                delete_indices.append(i - minus + plus)
                            elif self.tokens[i - minus + plus]['code'] == '||':
                                self.tokens[i - minus + plus]['category'] = 'comma'
                                self.tokens[i - minus + plus]['code'] = ', '
        self.delete_tokens(delete_indices)
        
    def delete_output_brackets_if_not_concat(self) -> None:
        """出力時、CONCAT以外の場合は両端の括弧を削除する"""
        is_output = False
        before_category = ''
        bracket_count = 0
        bracket_start_index = INF
        delete_indices = []
        is_no_concat = False
        for i, token in enumerate(self.tokens):
            category = token['category']
            if self.ignore(category): continue
            if before_category == 'put_line' and category == 'bracket_start':
                is_output = True
            if is_output:
                match category:
                    case 'bracket_start':
                        if token['code'] == '(':
                            is_no_concat = True
                        if bracket_count == 0:
                            bracket_start_index = i
                        bracket_count += 1
                    case 'bracket_end':
                        bracket_count -= 1
                        if bracket_count == 0:
                            if is_no_concat:
                                delete_indices.append(bracket_start_index)
                                delete_indices.append(i)
                            is_output = False
                            is_no_concat = False
                            bracket_start_index = INF
            before_category = category
        self.delete_tokens(delete_indices)
                         
    def delete_method_name_after_end(self, *, is_procedure: bool) -> None:
        """END直後のプロシージャ名を削除します"""
        if is_procedure:
            method_type = 'procedure'
        else:
            method_type = 'function'
        delete_indices = []
        before_category = ''
        for i, token in enumerate(self.tokens):
            category = token['category']
            if self.ignore(category):
                continue
            elif before_category == method_type + '_end' and category != 'semicolon':
                if self.tokens[i - 1]['code'].strip() == '':
                    delete_indices.append(i - 1)
                delete_indices.append(i)
            before_category = category
        self.delete_tokens(delete_indices)

    def replace_slash_after_semicolon_to_empty_text(self) -> None:
        """`;`直後の`/`を空文字に置換します"""
        before_category = ''
        delete_indices = []
        for i, token in enumerate(self.tokens):
            category = token['category']
            if self.ignore(category): 
                continue
            elif category == 'slash' and before_category == 'semicolon':
                delete_indices.append(i)
            before_category = category
        self.delete_tokens(delete_indices)

    def add_plpgsql_after_method_end(self, *, is_procedure: bool) -> None:
        """メソッド直後に言語文言を追加します"""
        step = 0 # 1: ***_end, 2: semicolon, 
        if is_procedure:
            method_type = 'procedure'
        else:
            method_type = 'function'
        for token in self.tokens:
            category = token['category']
            match step:
                case 0:
                    if category == method_type + '_end':
                        step = 1
                case 1:
                    if category == 'semicolon':
                        step = 2
                case 2:
                    if category == 'line_break':
                        token['code'] += '$$ LANGUAGE plpgsql;'
                        step = 0

    def add_method_bracket_with_no_arguments(self, *, is_procedure: bool) -> None:
        """引数を持たないプロシージャに括弧を追加します"""
        if is_procedure:
            method_type = 'procedure'
        else:
            method_type = 'function'
        step = 0
        method_name_index = INF
        bracket_start_count = 0
        for i, token in enumerate(self.tokens):
            category = token['category']
            if self.ignore(category): continue
            match step:
                case 0:
                    if category == method_type + '_start':
                        step = 1
                case 1:
                    if category == method_type + '_name':
                        step = 2
                        method_name_index = i
                case 2:
                    if category == 'bracket_start':
                        bracket_start_count += 1
                    elif category == 'is':
                        if bracket_start_count == 0:
                            self.tokens[method_name_index + 1]['code'] = '() '
                        bracket_start_count = 0
                        method_name_index = INF
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

    
            
