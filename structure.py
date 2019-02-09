from scaner import *
import numpy as np
class Layer:
    def __init__(self, lex_arr, param_list=None, parent=None):
        self.operators = []
        self.types = []
        self.variables = []
        self.functions = []
        self.parent = parent

        if parent is None:
            self.add_type('int', None)
            self.add_type('__int64', None)
        if param_list is not None:
            for param in param_list:
                self.parse_new_var(param)

        is_ok, err = self.parse_layer(lex_arr)
        if not is_ok:
            print(err)
        else:
            if parent is None:
                self.print()

    def get_level(self):
        if self.parent is None:
            return 0
        else:
            return self.parent.get_level() + 1

    def print(self):
        prefix = '\t' * self.get_level()
        for operator in self.operators:
            head = ''
            for lex in operator['head']:
                head += lex[1]+' '
            print(prefix+head)
            if operator['type'] == 'FUNCTION' or operator['type'] == 'FOR':
                operator['sublayer'].print()

    def get_types(self):
        if self.parent is not None:
            return self.types + self.parent.get_types()
        else:
            return self.types

    def get_variables(self):
        if self.parent is not None:
            return self.variables + self.parent.get_variables()
        else:
            return self.variables

    def get_functions(self):
        if self.parent is not None:
            return self.functions + self.parent.get_functions()
        else:
            return self.functions

    def have_type(self, name):
        for t in self.get_types():
            if t['name'] == name:
                return True
        return False

    def have_function(self, name):
        for f in self.get_functions():
            if f['name'] == name:
                return True
        return False

    def have_variable(self, name):
        for v in self.get_variables():
            if v['name'] == name:
                return True
        return False

    def set_variable(self, name, value):
        for i in range(len(self.variables)):
            if self.variables[i][0] == name:
                self.variables[i][2] = value
                return True
        if self.parent is not None:
            return self.parent.set_variable(name, value)

        return False

    def add_variable(self, name, type, value = 0):
        self.variables.append({'name':name,
                               'type':type,
                               'value':value})

    def add_type(self, name, type, count=1):
        self.types.append({'name': name,
                           'type': type,
                           'count': count})

    def add_function(self, name, return_type, parameter_types, layer):
        self.functions.append({'name':name,
                               'return_type':return_type,
                               'parameter_types':parameter_types,
                               'layer':layer})

    def merge(self, lex_arr):
        s = ''
        for l in lex_arr:
            s += l[1] + ' '
        return s

    def make_err(self, expectation, one_lex):
        return 'Ожидалось "{}", встречено "{}" [{}:{}]'.format(expectation, one_lex[1], one_lex[2]+1, one_lex[3])

    def parse_layer(self, lex_arr):
        while len(lex_arr) > 0:
            is_type_desription, err_1, line, new_lex_arr = self.check_type_desctiprion(lex_arr)
            if is_type_desription:
                if err_1 == '':
                    self.parse_new_type(line)
                    self.parse_new_operator(line)
                    lex_arr = new_lex_arr
                else:
                    return False, err_1
            else:
                is_var_description, err_2, line, new_lex_arr = self.check_var_descrtiption(lex_arr)
                if is_var_description:
                    if err_2 == '':
                        self.parse_new_var(line)
                        self.parse_new_operator(line)
                        lex_arr = new_lex_arr
                    else:
                        return False, err_2

                else:
                    is_func_description, err_3, func, new_lex_arr = self.check_func_desription(lex_arr)
                    if is_func_description:
                        if self.parent is None:
                            if err_3 == '':
                                self.parse_new_func(func)
                                lex_arr = new_lex_arr
                            else:
                                return False, err_3
                        else:
                            return False, 'Описание функций не допустимо внутри функции [{}:{}]'.format(lex_arr[0][2]+1, lex_arr[0][3])
                    else:
                        if lex_arr[0][0] == END:
                            break
                        else:
                            if self.parent is None:
                                return False, self.make_err('описание функции, переменный или типа', lex_arr[0]) + '\n' + err_3
                            else:
                                is_operator, err_4, operator, new_lex_arr = self.check_operator(lex_arr)
                                if is_operator:
                                    if err_4 == '':
                                        self.parse_new_operator(operator)
                                        lex_arr = new_lex_arr
                                    else:
                                        print(err_4)
                                        return False, err_4
                                else:
                                    return False, self.make_err('оператор', lex_arr[0])
        return True, 'Синтаксический анализатор: обработано без ошибок'

    # Объявление функции
    def check_func_desription(self, lex_arr):
        is_t, err_t = self.is_type(lex_arr[0])
        if is_t:
            if lex_arr[1][0] == ID:
                if lex_arr[2][0] == ROUND_BRACE_OPEN:
                    is_param_list, err, params, new_lex_arr = self.check_param_list(lex_arr[3:])
                    if is_param_list:
                        if err == '':
                            if new_lex_arr[0][0] == ROUND_BRACE_CLOSE:
                                if new_lex_arr[1][0] == CURLY_BRACE_OPEN:
                                    is_block, err_1, block, new_lex_arr_1 = self.check_block(new_lex_arr[2:])
                                    if is_block:
                                        if err_1 == '':
                                            if new_lex_arr_1[0][0] == CURLY_BRACE_CLOSE:
                                                return True, '', lex_arr[:3] + params + new_lex_arr[:2] + block + new_lex_arr_1[:1], new_lex_arr_1[1:]
                                            else:
                                                return True, self.make_err('}', new_lex_arr_1[0]), lex_arr[:3] + params + new_lex_arr[:2] + block, new_lex_arr_1
                                        else:
                                            return True, err_1, lex_arr[:3] + params + new_lex_arr[:2], new_lex_arr[2:]
                                    else:
                                        return True, err_1, lex_arr[:3] + params + new_lex_arr[:2], new_lex_arr[2:]
                                else:
                                    return True, self.make_err('{', new_lex_arr[1]), lex_arr[:3] + params + new_lex_arr[:1], new_lex_arr[1:]
                            else:
                                return True, self.make_err(')', new_lex_arr[0]), lex_arr[:3] + params, new_lex_arr
                        else:
                            if new_lex_arr[0][0] == ID:
                                return True, err, lex_arr[:3], new_lex_arr
                            else:
                                return True, self.make_err(') или параметры', new_lex_arr[0]), [], new_lex_arr
                    else:
                        return True, err, lex_arr[:3], new_lex_arr
                else:
                    return False, self.make_err('(', lex_arr[2]), lex_arr[:2], lex_arr[2:]
            else:
                return False, self.make_err('идентификатор', lex_arr[1]), lex_arr[:1], lex_arr[1:]
        else:
            return False, err_t, [], lex_arr

    # Проверка блока
    def check_block(self, lex_arr):
        operators = []
        while lex_arr[0][0] != CURLY_BRACE_CLOSE:
            is_var_description, err, var_description, new_lex_arr = self.check_var_descrtiption(lex_arr)
            if is_var_description:
                if err == '':
                    operators += var_description
                    lex_arr = new_lex_arr
                else:
                    return True, err, operators, new_lex_arr
            else:
                is_operator, err, operator, new_lex_arr = self.check_operator(lex_arr)
                if is_operator:
                    if err == '':
                        operators += operator
                        lex_arr = new_lex_arr
                    else:
                        return True, err, operators, new_lex_arr
                else:
                    return True, err, operators, new_lex_arr
        return True, '', operators, lex_arr

    # Проверка оператора
    def check_operator(self, lex_arr):
        if lex_arr[0][0] == BREAK:
            if lex_arr[1][0] == SEMICOLON:
                return True, '', lex_arr[:2], lex_arr[2:]
            else:
                return True, self.make_err(';', lex_arr[1]), lex_arr[1:], lex_arr[:1]
        elif lex_arr[0][0] == CURLY_BRACE_OPEN:
            is_block, err, block, new_lex_arr = self.check_block(lex_arr[1:])
            if is_block:
                if err == '':
                    if new_lex_arr[0][0] == CURLY_BRACE_CLOSE:
                        return True, '', lex_arr[:1] + block + new_lex_arr[:1], new_lex_arr[1:]
                    else:
                        return True, self.make_err('}', new_lex_arr[0]), lex_arr[:1] + block, new_lex_arr
                else:
                    return True, err, lex_arr[:2], new_lex_arr[2:]
            else:
                return True, err, lex_arr[:2], new_lex_arr[2:]
        elif lex_arr[0][0] == FOR:
            if lex_arr[1][0] == ROUND_BRACE_OPEN:
                is_var_description, err, var_description, new_lex_arr = self.check_var_descrtiption(lex_arr[2:])
                if is_var_description:
                    if err == '':
                        is_A1, err_A1, A1, new_lex_arr_A1 = self.A1(new_lex_arr)
                        if is_A1:
                            if err_A1 == '':
                                if new_lex_arr_A1[0][0] == SEMICOLON:
                                    is_A1_1, err_A1_1, A1_1, new_lex_arr_A1_1 = self.A1(new_lex_arr_A1[1:])
                                    if is_A1_1:
                                        if err_A1_1 == '':
                                            if new_lex_arr_A1_1[0][0] == ROUND_BRACE_CLOSE:
                                                is_operator, err_oper, operator, new_lex_arr_oper = self.check_operator(new_lex_arr_A1_1[1:])
                                                if is_operator:
                                                    if err_oper == '':
                                                        return True, '', lex_arr[:2] + var_description + A1 + \
                                                               new_lex_arr_A1[:1] + A1_1 + new_lex_arr_A1_1[:1] + \
                                                               operator, new_lex_arr_oper
                                                    else:
                                                        return True, err_oper, [], new_lex_arr_oper
                                                else:
                                                    return True, err_oper, [], new_lex_arr_oper
                                            else:
                                                return True, self.make_err(')', new_lex_arr_A1_1[0]), [], new_lex_arr_A1_1
                                        else:
                                            return True, err_A1_1, [], new_lex_arr_A1
                                    else:
                                        return True, err_A1_1, [], new_lex_arr_A1
                                else:
                                    return True, self.make_err(';', new_lex_arr_A1[0]), [], new_lex_arr_A1
                            else:
                                return True, err_A1, [], new_lex_arr
                        else:
                            return True, err_A1, [], new_lex_arr
                    else:
                        return True, err, [], lex_arr[2:]
                else:
                    return True, err, [], lex_arr[2:]
            else:
                return True, self.make_err('(', lex_arr[1]), [], lex_arr[1:]
        else:
            is_A1, err, A1, new_lex_arr = self.A1(lex_arr)
            if is_A1:
                if err == '':
                    if new_lex_arr[0][0] == SEMICOLON:
                        return True, '', A1 + new_lex_arr[:1], new_lex_arr[1:]
                    else:
                        return True, self.make_err(';', new_lex_arr[0]), A1, new_lex_arr
                else:
                    return True, err, [], new_lex_arr
            else:
                if lex_arr[0][0] == SEMICOLON:
                    return True, '', lex_arr[:1], lex_arr[1:]
                else:
                    return False, self.make_err('оператор', lex_arr[0]), [], lex_arr

    # Один оператор
    def check_single_operator(self, lex_arr):
        if lex_arr[0][0] == ID:
            if lex_arr[1][0] == ROUND_BRACE_OPEN:
                if lex_arr[2][0] == ROUND_BRACE_CLOSE:
                    return True, '', lex_arr[:3], lex_arr[3:]
                else:
                    params = []
                    lex_arr_1 = lex_arr[2:]
                    while lex_arr_1[0][0] != ROUND_BRACE_CLOSE:
                        is_A1, err, A1, new_lex_arr = self.A1(lex_arr_1)
                        if is_A1:
                            if err == '':
                                params += A1
                                lex_arr_1 = new_lex_arr
                            else:
                                return True, err, [], lex_arr_1
                        else:
                            return True, err, [], lex_arr_1
                        if lex_arr_1[0][0] == COMMA:
                            params += lex_arr_1[:1]
                            lex_arr_1 = lex_arr_1[1:]
                    if lex_arr_1[0][0] == ROUND_BRACE_CLOSE:
                        return True, '', lex_arr[:2] + params + lex_arr_1[:1], lex_arr_1[1:]
                    else:
                        return True, self.make_err(')', lex_arr[0]), [], lex_arr
            else:
                if lex_arr[1][0] == SQUARE_BRACE_OPEN:
                    is_A1, err, A1, new_lex_arr = self.A1(lex_arr[2:])
                    if is_A1:
                        if err == '':
                            if new_lex_arr[0][0] == SQUARE_BRACE_CLOSE:
                                if new_lex_arr[1][0] == ASSIGN:
                                    is_A1_1, err_1, A1_1, new_lex_arr_1 = self.A1(new_lex_arr[2:])
                                    if is_A1_1:
                                        if err_1 == '':
                                            return True, '', lex_arr[:2] + A1 + new_lex_arr[:2] + A1_1, new_lex_arr_1
                                        else:
                                            return True, err, [], new_lex_arr[1:]
                                    else:
                                        return True, err, [], new_lex_arr[1:]
                                else:
                                    if new_lex_arr[2][0] == ASSIGN:
                                        if new_lex_arr[1][0] == STAR or new_lex_arr[1][0] == SLASH or new_lex_arr[1][0] == PLUS or new_lex_arr[1][0] == MINUS:
                                            is_A1_1, err_1, A1_1, new_lex_arr_1 = self.A1(new_lex_arr[3:])
                                            if is_A1_1:
                                                if err_1 == '':
                                                    return True, '', lex_arr[:3] + A1 + new_lex_arr[
                                                                                        :3] + A1_1, new_lex_arr_1
                                                else:
                                                    return True, err, [], new_lex_arr[2:]
                                            else:
                                                return True, err, [], new_lex_arr[2:]
                                    else:
                                        return True, '', lex_arr[:2] + A1 + new_lex_arr[:1], new_lex_arr[1:]
                            else:
                                return True, self.make_err(']', new_lex_arr[0]), lex_arr[:2], new_lex_arr
                        else:
                            return True, err, [], lex_arr[1:]
                    else:
                        return True, err, [], lex_arr[1:]
                else:
                    if lex_arr[1][0] == ASSIGN:
                        is_A1_1, err_1, A1_1, new_lex_arr_1 = self.A1(lex_arr[2:])
                        if is_A1_1:
                            if err_1 == '':
                                return True, '', lex_arr[:2]+A1_1, new_lex_arr_1
                            else:
                                return True, err_1, [], lex_arr[2:]
                        if err_1 == '':
                            return True, err_1, [], lex_arr[2:]

                    if lex_arr[2][0] == ASSIGN:
                        if lex_arr[1][0] == STAR or lex_arr[1][0] == SLASH or lex_arr[1][0] == PLUS or lex_arr[1][0] == MINUS:
                            is_A1_1, err_1, A1_1, new_lex_arr_1 = self.A1(lex_arr[3:])
                            if is_A1_1:
                                if err_1:
                                    return True, '', lex_arr[:3] + A1_1, new_lex_arr_1
                                else:
                                    return True, err_1, [], lex_arr[3:]
                            if err_1 == '':
                                return True, err_1, [], lex_arr[3:]
                    return True, '', lex_arr[:1], lex_arr[1:]
        return False, self.make_err('идентификатор', lex_arr[0]), [], lex_arr

    # Список параметров
    def check_param_list(self, lex_arr):
        params = []
        while lex_arr[0][0] != ROUND_BRACE_CLOSE:
            is_t, err_t = self.is_type(lex_arr[0])
            if is_t:
                if lex_arr[1][0] == ID:
                    if lex_arr[2][0] == ASSIGN:
                        if lex_arr[3][0] == TYPE_INT or lex_arr[3][0] == TYPE_SINT:
                            params += lex_arr[:4]
                            lex_arr = lex_arr[4:]
                        else:
                            return True, self.make_err('константа', lex_arr[3]), params, lex_arr
                    else:
                        params += lex_arr[:2]
                        lex_arr = lex_arr[2:]
                else:
                    return True, self.make_err('идентификатор', lex_arr[1]), params, lex_arr
            else:
                return True, err_t, params, lex_arr
            if lex_arr[0][0] == COMMA:
                params += lex_arr[:1]
                lex_arr = lex_arr[1:]
        return True, '', params, lex_arr

    # Объявление типов
    def check_type_desctiprion(self, lex_arr):
        if lex_arr[0][0] == TYPEDEF:
            is_t, err_t = self.is_type(lex_arr[1])
            if is_t:
                if lex_arr[2][0] == ID:
                    is_t, err_t = self.is_type(lex_arr[2])
                    if is_t:
                        return True, 'Такой тип уже был объявлен', [], lex_arr
                    if lex_arr[3][0] == SQUARE_BRACE_OPEN:
                        if lex_arr[4][0] == TYPE_INT or lex_arr[4][0] == TYPE_SINT:
                            if lex_arr[5][0] == SQUARE_BRACE_CLOSE:
                                if lex_arr[6][0] == SEMICOLON:
                                    return True, '', lex_arr[:7], lex_arr[7:]
                                else:
                                    return True, self.make_err(';', lex_arr[6]), [], lex_arr
                            else:
                                return True, self.make_err(']', lex_arr[5]), [], lex_arr
                        else:
                            return True, self.make_err('константа', lex_arr[4]), [], lex_arr
                    if lex_arr[3][0] == SEMICOLON:
                        return True, '', lex_arr[:4], lex_arr[4:]
                    else:
                        return True, self.make_err(';', lex_arr[6]), [], lex_arr
                else:
                    return True, self.make_err('идентификатор', lex_arr[2]), [], lex_arr
            else:
                return True, err_t, [], lex_arr
        return False, '', [], lex_arr

    # Объявение переменной
    def check_var_descrtiption(self, lex_arr):
        is_t, err_t = self.is_type(lex_arr[0])
        if is_t:
            is_var_list, err, vars, new_lex_arr = self.check_var_list(lex_arr[1:])
            if is_var_list:
                if err == '':
                    if new_lex_arr[0][0] == SEMICOLON:
                        return True, '', lex_arr[:1] + vars + new_lex_arr[:1], new_lex_arr[1:]
                    else:
                        return True, self.make_err(';', new_lex_arr[0]), lex_arr[:1] + vars, new_lex_arr
                else:
                    return True, err, vars, new_lex_arr
            else:
                return False, err, vars, new_lex_arr
        else:
            return False, err_t, [], lex_arr

    # Список переменных
    def check_var_list(self, lex_arr):
        vars = []
        while lex_arr[0][0] == ID:
            if lex_arr[1][0] == ROUND_BRACE_OPEN:
                return False, '', [], lex_arr
            if lex_arr[1][0] == SQUARE_BRACE_OPEN:
                if lex_arr[2][0] == TYPE_INT or lex_arr[2][0] == TYPE_SINT:
                    if lex_arr[3][0] == SQUARE_BRACE_CLOSE:
                        if lex_arr[4][0] == COMMA:
                            vars += lex_arr[:5]
                            lex_arr = lex_arr[5:]
                        else:
                            vars += lex_arr[:4]
                            lex_arr = lex_arr[4:]
                            return True, '', vars, lex_arr
                    else:
                        return True, self.make_err(']', lex_arr[3]), vars, lex_arr
                else:
                    return True, self.make_err('константа', lex_arr[2]), vars, lex_arr

            elif lex_arr[1][0] == ASSIGN:
                is_A1, err, A1, new_lex_arr = self.A1(lex_arr[2:])
                if is_A1:
                    if err == '':
                        if new_lex_arr[0][0] == COMMA:
                            vars += lex_arr[:2] + A1 + new_lex_arr[:1]
                            lex_arr = new_lex_arr[1:]
                        else:
                            vars += lex_arr[:2] + A1
                            lex_arr = new_lex_arr
                            return True, '', vars, lex_arr
                    else:
                        return True, err, vars, lex_arr
                else:
                    return True, err, vars, lex_arr

            else:
                if lex_arr[1][0] == COMMA:
                    vars += lex_arr[:2]
                    lex_arr = lex_arr[2:]
                else:
                    vars += lex_arr[:1]
                    lex_arr = lex_arr[1:]
                    return True, '', vars, lex_arr
        return False, self.make_err('идентификатор', lex_arr[0]), [], lex_arr

    def A1(self, lex_arr):
        is_A2, err, A2, new_lex_arr = self.A2(lex_arr)
        if is_A2:
            if err == '':
                if new_lex_arr[0][0] == EQUAL or new_lex_arr[0][0] == MORE_EQUAL or new_lex_arr[0][0] == LESS_EQUAL or \
                        new_lex_arr[0][0] == MORE or new_lex_arr[0][0] == LESS:
                    is_A2_1, err_1, A2_1, new_lex_arr_1 = self.A2(new_lex_arr[1:])
                    if is_A2_1:
                        if err_1 == '':
                            return True, '', A2 + new_lex_arr[:1] + A2_1, new_lex_arr_1
                        else:
                            return True, err_1, [], new_lex_arr_1
                    else:
                        return True, err_1, [], new_lex_arr_1
                else:
                    return True, '', A2, new_lex_arr
            else:
                return True, err, [], new_lex_arr
        else:
            return False, err, [], new_lex_arr

    def A2(self, lex_arr):
        is_A3, err, A3, new_lex_arr = self.A3(lex_arr)
        if is_A3:
            if err == '':
                if new_lex_arr[0][0] == PLUS or new_lex_arr[0][0] == MINUS:
                    is_A3_1, err_1, A3_1, new_lex_arr_1 = self.A3(new_lex_arr[1:])
                    if is_A3_1:
                        if err_1 == '':
                            return True, '', A3 + new_lex_arr[:1] + A3_1, new_lex_arr_1
                        else:
                            return True, err_1, [], new_lex_arr_1
                    else:
                        return True, err_1, [], new_lex_arr_1
                else:
                    return True, '', A3, new_lex_arr
            else:
                return True, err, [], new_lex_arr
        else:
            return False, err, [], new_lex_arr

    def A3(self, lex_arr):
        is_A4, err, A4, new_lex_arr = self.A4(lex_arr)
        if is_A4:
            if err == '':
                if new_lex_arr[0][0] == STAR or new_lex_arr[0][0] == SLASH or new_lex_arr[0][0] == PERCENT:
                    is_A4_1, err_1, A4_1, new_lex_arr_1 = self.A4(new_lex_arr[1:])
                    if is_A4_1:
                        if err_1 == '':
                            return True, '', A4 + new_lex_arr[:1] + A4_1, new_lex_arr_1
                        else:
                            return True, err_1, [], new_lex_arr_1
                    else:
                        return True, err_1, [], new_lex_arr_1
                else:
                    return True, '', A4, new_lex_arr
            else:
                return True, err, [], new_lex_arr
        else:
            return False, err, [], new_lex_arr

    def A4(self, lex_arr):
        is_A5, err, A5, new_lex_arr = self.A5(lex_arr)
        if is_A5:
            if err == '':
                if new_lex_arr[0][0] == PLUS and new_lex_arr[1][0] == PLUS or \
                        new_lex_arr[0][0] == MINUS and new_lex_arr[1][0] == MINUS:
                    return True, '', A5 + new_lex_arr[:2], new_lex_arr[2:]
                else:
                    return True, '', A5, new_lex_arr
            else:
                return True, err, [], new_lex_arr
        else:
            return False, err, [], new_lex_arr

    def A5(self, lex_arr):
        if lex_arr[0][0] == PLUS and lex_arr[1][0] == PLUS or \
                lex_arr[0][0] == MINUS and lex_arr[1][0] == MINUS:
            is_A6, err, A6, new_lex_arr = self.A6(lex_arr[2:])
            if is_A6:
                if err == '':
                    return True, '', new_lex_arr[:2] + A6, new_lex_arr
                else:
                    return True, err, [], new_lex_arr
            else:
                return False, err, [], new_lex_arr
        elif lex_arr[0][0] == PLUS or lex_arr[0][0] == MINUS:
            is_A6, err, A6, new_lex_arr = self.A6(lex_arr[1:])
            if is_A6:
                if err == '':
                    return True, '', new_lex_arr[:1] + A6, new_lex_arr
                else:
                    return True, err, [], new_lex_arr
            else:
                return False, err, [], new_lex_arr
        else:
            is_A6, err, A6, new_lex_arr = self.A6(lex_arr)
            if is_A6:
                if err == '':
                    return True, '', A6, new_lex_arr
                else:
                    return True, err, [], new_lex_arr
            else:
                return False, err, [], new_lex_arr

    def A6(self, lex_arr):
        if lex_arr[0][0] == TYPE_INT or lex_arr[0][0] == TYPE_SINT:
            return True, '', lex_arr[:1], lex_arr[1:]
        elif lex_arr[0][0] == ROUND_BRACE_OPEN:
            is_A1, err, A1, new_lex_arr = self.A1(lex_arr[1:])
            if is_A1:
                if err == '':
                    if new_lex_arr[0][0] == ROUND_BRACE_CLOSE:
                        return True, '', lex_arr[:1] + A1 + new_lex_arr[:1], new_lex_arr[1:]
                    else:
                        return True, self.make_err(')', new_lex_arr[0]), lex_arr[:1] + A1, new_lex_arr
                else:
                    return True, err, [], new_lex_arr
            else:
                return False, err, [], new_lex_arr
        else:
            is_single_oper, err, single_oper, new_lex_arr = self.check_single_operator(lex_arr)
            if is_single_oper:
                if err == '':
                    return True, '', single_oper, new_lex_arr
                else:
                    return True, err, [], new_lex_arr
            else:
                return False, err, [], new_lex_arr

    # Проверка типа
    def is_type(self, one_lex):
        if self.have_type(one_lex[1]):
            return True, ''
        else:
            return False, 'Неизвестный тип {} [{}:{}]'.format(one_lex[1], one_lex[2]+1, one_lex[3])

    # Вычисление оператора
    def calculate(self, oper):
        return 0

    # Добавление нового типа
    def parse_new_type(self, oper):
        new_type = oper[1][1]
        name = oper[2][1]
        if len(oper) > 4:
            self.add_type(name, new_type, int(oper[4][1]))
        else:
            self.add_type(name, new_type)

    # Добавление новой переменной
    def parse_new_var(self, oper):
        var_type = oper[0][1]
        oper = oper[1:]
        while oper[0][0] != SEMICOLON:
            name = oper[0][1]
            oper = oper[1:]
            if oper[0][0] == ASSIGN:
                assign_oper = []
                oper = oper[1:]
                while oper[0][0] != COMMA and oper[0][0] != SEMICOLON:
                    assign_oper += oper[:1]
                    oper = oper[1:]
                self.add_variable(name, var_type, self.calculate(assign_oper))
                oper = oper[1:]
            else:
                self.add_variable(name, var_type)
            if len(oper) > 0:
                if oper[0][0] == COMMA:
                    oper = oper[1:]
            else:
                break

    # Добавление оператора
    def parse_new_operator(self, oper):
        if oper[0][0] == FOR:
            head = []
            while oper[0][0] != ROUND_BRACE_CLOSE:
                head.append(oper[0])
                oper = oper[1:]
            head.append(oper[0])
            oper = oper[1:]

            body = []
            if oper[0][0] == CURLY_BRACE_OPEN:
                oper = oper[1:]
                while oper[0][0] != CURLY_BRACE_CLOSE:
                    body.append(oper[0])
                    oper = oper[1:]
            else:
                body = oper

            new_param = []
            for i in head[2:]:
                if i[0] == SEMICOLON:
                    new_param.append(i)
                    break
                new_param.append(i)

            self.operators.append({'type': 'FOR', 'head': head, 'sublayer': Layer(body, param_list=[new_param], parent=self)})
        else:
            self.operators.append({'type': 'DEFAULT', 'head': oper})

    # Добавление новой фунции
    def parse_new_func(self, func):
        return_type = func[0][1]
        func_name = func[1][1]
        params_arr = func[3:]
        head = func[:3]
        params = []
        while params_arr[0][0] != ROUND_BRACE_CLOSE:
            head.append(params_arr[0])
            param = []
            while params_arr[0][0] != COMMA and params_arr[0][0] != ROUND_BRACE_CLOSE:
                param.append(params_arr)
                params_arr = params_arr[1:]

            params += [params_arr[0]]
            if params_arr[0][0] == COMMA:
                params_arr = params_arr[1:]
        head.append(params_arr[0])
        block_arr = params_arr[2:-1]
        layer = Layer(block_arr, params, self)
        self.add_function(func_name, return_type, params, layer)
        self.operators.append({'type': 'FUNCTION', 'head': head, 'sublayer': layer})
