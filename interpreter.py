from syntaxAnalizer import *
from triadeGenerator import get_triade

class Interpreter(object):
    def __init__(self, file):
        self.analizer = SyntaxAnalizerV2()
        self.layers = self.analizer.get_layers(file)
        if len(self.layers.err) > 0:
            return
        self.variables = self.layers.variables
        self.do_function([ID, 'main', 0, 0])
        pass

    def do_function(self, function_lex, params=None):
        function_name = function_lex[1]
        if function_name == 'print':
            if params is None:
                print('\n')
            else:
                for par in params:
                    print(par)
                # print('\n')
            return

        if params is None:
            params = []
        myFunction = None
        finded = False
        for func in self.layers.functions:
            if func['name'] == function_name:
                finded = True
                if len(func['parameter_types']) == len(params):
                    myFunction = func

        if not finded:
            print('Нет функции с именем {} [{}:{}]'.format(function_lex[1], function_lex[2], function_lex[3]))
            return
        elif myFunction is None:
            print('Нет функции {} с таким количеством параметров [{}:{}]'.format(function_lex[1], function_lex[2], function_lex[3]))
            return

        layer = myFunction['layer']
        for i in range(len(myFunction['parameter_types'])):
            for j in range(len(layer.variables)):
                if myFunction['parameter_types'][i][1][1] == layer.variables[j]['name']:
                    layer.variables[j]['value'] = params[i]
        self.do_layer(layer)

    def do_layer(self, layer):
        for operator in layer.operators:
            if operator['type'] == 'DEFAULT':
                if not self.do_default_operator(operator['head'], layer):
                    break
            elif operator['type'] == 'FOR':
                self.do_for_operator(operator['head'], operator['sublayer'])

    def do_default_operator(self, operator, layer):
        triade = get_triade(operator)
        if triade['type'] == 'function':
            func_name = triade['f']['f']
            params = [self.calculate_triade(tr, layer) for tr in triade['s']]
            self.do_function(func_name, params)

        elif triade['type'] == 'assign':
            name, iter = self.get_iter(triade['f'], layer)
            value = self.calculate_triade(triade['s'], layer)
            layer.set_variable(name, value, iter)

        elif triade['type'] == 'assign_minus':
            name, iter = self.get_iter(triade['f'], layer)
            valueF = layer.get_var(name)['value']
            for i in iter:
                valueF = valueF[i]
            valueS = self.calculate_triade(triade['s'], layer)
            if valueF is None:
                print("Ошибка: использование неидентифицированного значения переменной [Строка:{}]".format(operator[0][2]+1))
                return False
            layer.set_variable(name, valueF-valueS, iter)

        elif triade['type'] == 'assign_plus':
            name, iter = self.get_iter(triade['f'], layer)
            valueF = layer.get_var(name)['value']
            for i in iter:
                valueF = valueF[i]
            valueS = self.calculate_triade(triade['s'], layer)
            if valueF is None:
                print("Ошибка: использование неидентифицированного значения переменной [Строка:{}]".format(operator[0][2]+1))
                return False
            layer.set_variable(name, valueF+valueS, iter)

        elif triade['type'] == 'assign_percent':
            name, iter = self.get_iter(triade['f'], layer)
            valueF = layer.get_var(name)['value']
            for i in iter:
                valueF = valueF[i]
            valueS = self.calculate_triade(triade['s'], layer)
            if valueF is None:
                print("Ошибка: использование неидентифицированного значения переменной [Строка:{}]".format(operator[0][2]+1))
                return False
            layer.set_variable(name, valueF % valueS, iter)

        elif triade['type'] == 'assign_star':
            name, iter = self.get_iter(triade['f'], layer)
            valueF = layer.get_var(name)['value']
            for i in iter:
                valueF = valueF[i]
            valueS = self.calculate_triade(triade['s'], layer)
            if valueF is None:
                print("Ошибка: использование неидентифицированного значения переменной [Строка:{}]".format(operator[0][2]+1))
                return False
            layer.set_variable(name, valueF*valueS, iter)

        elif triade['type'] == 'assign_slash':
            name, iter = self.get_iter(triade['f'], layer)
            valueF = layer.get_var(name)['value']
            for i in iter:
                valueF = valueF[i]
            valueS = self.calculate_triade(triade['s'], layer)
            if valueF is None:
                print("Ошибка: использование неидентифицированного значения переменной [Строка:{}]".format(operator[0][2]+1))
                return False
            layer.set_variable(name, int(valueF/valueS), iter)

        elif triade['type'] == 'ident':
            return True

        else:
            self.calculate_triade(triade, layer)

        return True

    def calculate_triade(self, triade, layer):
        if triade['type'] == 'const':
            return int(triade['f'])

        if triade['type'] == 'variable':
            value = layer.get_var(triade['f'][1])['value']
            if value is None:
                raise Exception("Использование неидентифицированной переменной {} [{}:{}]".format(triade['f'][1], triade['f'][2]+1, triade['f'][3]+1))
            return value

        if triade['type'] == 'ident':
            return self.calculate_triade(triade['f'], layer)

        if triade['type'] == 'plus':
            first = self.calculate_triade(triade['f'], layer)
            second = self.calculate_triade(triade['s'], layer)
            if type(first) is list or type(second) is list:
                raise Exception("Исользование массива в качестве операнда невозможна")
            return first + second

        if triade['type'] == 'minus':
            first = self.calculate_triade(triade['f'], layer)
            second = self.calculate_triade(triade['s'], layer)
            if type(first) is list or type(second) is list:
                raise Exception("Исользование массива в качестве операнда невозможна")
            return first - second

        if triade['type'] == 'equal':
            first = self.calculate_triade(triade['f'], layer)
            second = self.calculate_triade(triade['s'], layer)
            if type(first) is list or type(second) is list:
                raise Exception("Исользование массива в качестве операнда невозможна")
            if first == second:
                return 1
            else:
                return 0

        if triade['type'] == 'more_equal':
            first = self.calculate_triade(triade['f'], layer)
            second = self.calculate_triade(triade['s'], layer)
            if type(first) is list or type(second) is list:
                raise Exception("Исользование массива в качестве операнда невозможна")
            if first >= second:
                return 1
            else:
                return 0

        if triade['type'] == 'less_equal':
            first = self.calculate_triade(triade['f'], layer)
            second = self.calculate_triade(triade['s'], layer)
            if type(first) is list or type(second) is list:
                raise Exception("Исользование массива в качестве операнда невозможна")
            if first <= second:
                return 1
            else:
                return 0

        if triade['type'] == 'more':
            first = self.calculate_triade(triade['f'], layer)
            second = self.calculate_triade(triade['s'], layer)
            if type(first) is list or type(second) is list:
                raise Exception("Исользование массива в качестве операнда невозможна")
            if first > second:
                return 1
            else:
                return 0

        if triade['type'] == 'less':
            first = self.calculate_triade(triade['f'], layer)
            second = self.calculate_triade(triade['s'], layer)
            if type(first) is list or type(second) is list:
                raise Exception("Исользование массива в качестве операнда невозможна")
            if first < second:
                return 1
            else:
                return 0

        if triade['type'] == 'percent':
            first = self.calculate_triade(triade['f'], layer)
            second = self.calculate_triade(triade['s'], layer)
            if type(first) is list or type(second) is list:
                raise Exception("Исользование массива в качестве операнда невозможна")
            return int(first % second)

        if triade['type'] == 'star':
            first = self.calculate_triade(triade['f'], layer)
            second = self.calculate_triade(triade['s'], layer)
            if type(first) is list or type(second) is list:
                raise Exception("Исользование массива в качестве операнда невозможна")
            return first * second

        if triade['type'] == 'slash':
            first = self.calculate_triade(triade['f'], layer)
            second = self.calculate_triade(triade['s'], layer)
            if type(first) is list or type(second) is list:
                raise Exception("Исользование массива в качестве операнда невозможна")
            return int(first / second)

        if triade['type'] == 'post_increment':
            name, iter = self.get_iter(triade['f'], layer)
            value = layer.get_var(name)['value']
            for i in iter:
                value = value[i]
            if type(value) is list:
                raise Exception("Исользование массива в качестве операнда невозможна")
            layer.set_variable(name, value+1, iter)
            return value

        if triade['type'] == 'post_decrement':
            name, iter = self.get_iter(triade['f'], layer)
            value = layer.get_var(name)['value']
            for i in iter:
                value = value[i]
            if type(value) is list:
                raise Exception("Исользование массива в качестве операнда невозможна")
            layer.set_variable(name, value-1, iter)
            return value

        if triade['type'] == 'pref_increment':
            name, iter = self.get_iter(triade['f'], layer)
            value = layer.get_var(name)['value']
            for i in iter:
                value = value[i]
            if type(value) is list:
                raise Exception("Исользование массива в качестве операнда невозможна")
            layer.set_variable(name, value+1, iter)
            return value+1

        if triade['type'] == 'pref_decrement':
            name, iter = self.get_iter(triade['f'], layer)
            value = layer.get_var(name)['value']
            for i in iter:
                value = value[i]
            if type(value) is list:
                raise Exception("Исользование массива в качестве операнда невозможна")
            layer.set_variable(name, value-1, iter)
            return value-1

        if triade['type'] == 'sign_plus':
            name, iter = self.get_iter(triade['f'], layer)
            value = layer.get_var(name)['value']
            for i in iter:
                value = value[i]
            if type(value) is list:
                raise Exception("Исользование массива в качестве операнда невозможна")
            return value

        if triade['type'] == 'sign_minus':
            name, iter = self.get_iter(triade['f'], layer)
            value = layer.get_var(name)['value']
            for i in iter:
                value = value[i]
            if type(value) is list:
                raise Exception("Исользование массива в качестве операнда невозможна")
            return -value

    def get_iter(self, triade, layer):
        if triade['type'] == 'variable':
            return triade['f'][1], []
        elif triade['type'] == 'ident':
            return self.get_iter(triade['f'], layer)
        else:
            name, iter = self.get_iter(triade['f'], layer)
            iter.append(self.calculate_triade(triade['s'], layer))
            return name, iter

    def do_for_operator(self, head, sublayer):
        head1 = []
        i = 2
        while head[i][0] != SEMICOLON:
            head1.append(head[i])
            i += 1
        head1.append(head[i])
        i += 1

        head2 = []
        while head[i][0] != SEMICOLON:
            head2.append(head[i])
            i += 1
        head2.append(head[i])
        i += 1

        head3 = []
        while head[i][0] != ROUND_BRACE_CLOSE:
            head3.append(head[i])
            i += 1
        head3.append(head[i])

        self.do_default_operator(head1, sublayer)
        head2 = get_triade(head2)
        cont = True
        while self.calculate_triade(head2, sublayer) != 0 and cont:
            for operator in sublayer.operators:
                if operator['type'] == 'DEFAULT':
                    if operator['head'][0][0] == BREAK or not self.do_default_operator(operator['head'], sublayer):
                        cont = False
                        break
                elif operator['type'] == 'FOR':
                    self.do_for_operator(operator['head'], operator['sublayer'])
            self.do_default_operator(head3, sublayer)





