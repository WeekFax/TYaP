from scaner import *


class SyntaxAnalizer:
    def __init__(self):
        self.t = TScaner()

    def check_correct(self, filename):
        self.t.getData(filename)
        arr = []
        sc = self.t.Scanner()
        arr.append([sc[0], sc[1], sc[2], sc[3]])
        while sc[0] != END:
            sc = self.t.Scanner()
            arr.append([sc[0], sc[1], sc[2], sc[3]])
        err = [e for e in arr if e[0] == ERROR]
        if len(err) > 0:
            for e in err:
                print(e[1])
            return False
        return self.program(arr)

    # Программа
    def program(self, arr):
        err = None

        while err is None:
            if arr[0][0] == END:
                return err
            elif arr[0][0] == INT and arr[1][0] == MAIN and \
                    arr[2][0] == ROUND_BRACE_OPEN and arr[3][0] == ROUND_BRACE_CLOSE:
                err, arr = self.block(arr[4:])

            else:
                err, arr = self.data(arr)

        return err

    # Тип
    def type(self, arr):
        err = None
        if arr[0][0] == INT or arr[0][0] == LINT or arr[0][0] == ID:
            arr = arr[1:]
        else:
            err = 'Ожидался идентификатор, встречено {} [Line {}:{}]'.format(arr[0][1], arr[0][2]+1, arr[0][3])
        return err, arr

    # Описание данных
    def data(self, arr):
        err = None
        bufArr = arr

        if arr[0][0] == TYPEDEF:
            err, arr = self.ID(arr[1:])
            if err is None:
                err, arr = self.type(arr[1:])
                if err is None:
                    if arr[0][0] == SQUARE_BRACE_OPEN:
                        err, arr = self.const(arr[1:])
                        if err is None:
                            if arr[0][0] == SQUARE_BRACE_CLOSE:
                                arr = arr[1:]
                            else:
                                err = 'Ожидалось "]", встречено {} [Line {}:{}]'.format(arr[0][1], arr[0][2]+1, arr[0][3])
                                arr = bufArr

        else:
            err, arr = self.type(arr)
            if err is None:
                err, arr = self.list(arr)
                if err is not None:
                    arr = bufArr

        if err is None:
            if arr[0][0] == SEMICOLON:
                arr = arr[1:]
            else:
                err = 'Ожидалась ";", встречено {} [Line {}:{}]'.format(arr[0][1], arr[0][2]+1, arr[0][3])

        return err, arr

    # Список переменных
    def list(self, arr):
        err = None
        err, arr = self.ID(arr)
        if err is None:
            arr = arr[1:]
            if arr[0][0] == ASSIGN:
                err, arr = self.A1(arr[1:])
            elif arr[0][0] == SQUARE_BRACE_OPEN:
                err, arr = self.const(arr)
                if err is None:
                    if arr[0][0] == SQUARE_BRACE_CLOSE:
                        arr = arr[1:]
                    else:
                        err = 'Ожидалось "]", встречено {} [Line {}:{}]'.format(arr[0][1], arr[0][2]+1, arr[0][3])
        if err is None:
            if arr[0][0] == COMMA:
                bufArr = arr
                err, arr = self.list(arr[1:])
                if err is not None:
                    arr = bufArr
        return err, arr

    # Блок
    def block(self, arr):
        err = None
        if arr[0][0] == CURLY_BRACE_OPEN:
            arr=arr[1:]
            while arr[0][0] != CURLY_BRACE_CLOSE and err is None:

                err, bufArr = self.data(arr)
                if err is not None and bufArr==arr:
                    arr = bufArr
                    err, arr = self.operator(arr)
                else:
                    arr = bufArr

            if err is None:
                if arr[0][0] == CURLY_BRACE_CLOSE:
                    arr = arr[1:]
                else:
                    err = 'Ожидалось "}"' + ', встречено {} [Line {}:{}]'.format(arr[0][1], arr[0][2]+1, arr[0][3])
        else:
            err = 'Ожидалось "{", встречено {} [Line {}:{}]'.format(arr[0][1], arr[0][2]+1, arr[0][3])
        return err, arr

    # Оператор
    def operator(self, arr):
        err = None
        if arr[0][0] == SEMICOLON:
            return err, arr[1:]
        elif arr[0][0] == BREAK:
            if arr[1][0] == SEMICOLON:
                return err, arr[2:]
            else:
                err = 'Ожидалось ";", встречено {} [Line {}:{}]'.format(arr[0][1], arr[0][2]+1, arr[0][3])
        elif arr[0][0] == FOR:
            err, arr = self.for_operator(arr)
        elif arr[0][0] == CURLY_BRACE_OPEN:
            err, arr = self.block(arr)
        else:
            err, arr = self.A1(arr)
            if err is None:
                if arr[0][0] == SEMICOLON:
                    return err, arr[1:]
                else:
                    err = 'Ожидалось ";", встречено {} [Line {}:{}]'.format(arr[0][1], arr[0][2]+1, arr[0][3])
            # err = 'Ожидался оператор, встречено {}'.format(arr[0][1])
        return err, arr

    # for
    def for_operator(self, arr):
        err = None
        if arr[0][0] == FOR:
            if arr[1][0] == ROUND_BRACE_OPEN:
                err, arr = self.data(arr[2:])
                if err is None:
                    err, arr = self.A1(arr)
                    if err is None:
                        if arr[0][0] == SEMICOLON:
                            err, arr = self.A1(arr[1:])
                            if err is None:
                                if arr[0][0] == ROUND_BRACE_CLOSE:
                                    return self.operator(arr[1:])
                                else:
                                    err = 'Ожидалось ")", встречено {} [Line {}:{}]'.format(arr[0][1], arr[0][2]+1, arr[0][3])
                        else:
                            err = 'Ожидалось ";", встречено {} [Line {}:{}]'.format(arr[0][1], arr[0][2]+1, arr[0][3])
            else:
                err = 'Ожидалось "(", встречено {} [Line {}:{}]'.format(arr[0][1], arr[0][2]+1, arr[0][3])
        return err, arr


    # Один оператор
    def single_operator(self, arr):
        err = None
        err, arr = self.ID(arr)
        if err is not None:
            return err, arr
        else:
            arr = arr[1:]

        if arr[0][0] == ROUND_BRACE_OPEN:
            err, arr = self.A1(arr[1:])
            if err is None:
                while arr[0][0] == COMMA:
                    err, arr = self.A1(arr[1:])
                    if err is not None:
                        return err, arr
            else:
                return err, arr
            if arr[0][0] == ROUND_BRACE_CLOSE:
                return None, arr[1:]
            else:
                err = 'Ожидалось ")", встречено {} [Line {}:{}]'.format(arr[0][1], arr[0][2]+1, arr[0][3])
        else:
            while err is None and arr[0][0] == SQUARE_BRACE_OPEN:
                err, arr = self.A1(arr[1:])
                if err is None:
                    if arr[0][0] == SQUARE_BRACE_CLOSE:
                        arr = arr[1:]
                    else:
                        err = 'Ожидалось "]", встречено {} [Line {}:{}]'.format(arr[0][1], arr[0][2]+1, arr[0][3])
                else:
                    return err, arr
            if arr[0][0] == ASSIGN:
                return self.A1(arr[1:])
            elif arr[0][0] == PLUS and arr[1][0] == EQUAL or arr[0][0] == MINUS and arr[1][0] == EQUAL or \
                arr[0][0] == SLASH and arr[1][0] == EQUAL or arr[0][0] == STAR and arr[1][0] == EQUAL:
                return self.A1(arr[2:])
            else:
                return None, arr
        return err, arr



    # Идентификатор
    def ID(self, arr):
        err = None
        if arr[0][0] != ID :
            err = 'Ожидался идентификатор, встречено: {} [Line {}:{}]'.format(arr[0][1], arr[0][2]+1, arr[0][3])
        return err, arr

    # Константа
    def const(self, arr):
        err = None
        if arr[0][0] == TYPE_INT or arr[0][0] == TYPE_SINT:
            arr = arr[1:]
        else:
            err = 'Ожидалась константа, встречено: {} [Line {}:{}]'.format(arr[0][1], arr[0][2]+1, arr[0][3])
        return err, arr

    # A1
    def A1(self, arr):
        err = None
        err, arr = self.A2(arr)
        while (arr[0][0] == LESS or arr[0][0] == MORE or arr[0][0] == LESS_EQUAL or arr[0][0] == MORE_EQUAL) and\
                err is None:
            err, arr = self.A2(arr[1:])
        return err, arr

    # A2
    def A2(self, arr):
        err = None
        err, arr = self.A3(arr)
        while (arr[0][0] == PLUS or arr[0][0] == MINUS) and err is None:
            err, arr = self.A3(arr[1:])
        return err, arr

    # A3
    def A3(self, arr):
        err = None
        err, arr = self.A4(arr)
        while (arr[0][0] == PERCENT or arr[0][0] == SLASH or arr[0][0] == STAR) and err is None:
            err, arr = self.A4(arr[1:])
        return err, arr

    # A4
    def A4(self, arr):
        err = None
        err, arr = self.A5(arr)
        if arr[0][0] == PLUS and arr[1][0] == PLUS or arr[0][0] == MINUS and arr[1][0] == MINUS:
            arr = arr[2:]
        return err, arr

    # A5
    def A5(self, arr):
        err = None
        if arr[0][0] == PLUS and arr[1][0] == PLUS or arr[0][0] == MINUS and arr[1][0] == MINUS:
            arr = arr[2:]
        elif arr[0][0] == PLUS or arr[0][0] == MINUS:
            arr = arr[1:]
        err, arr = self.A6(arr)
        return err, arr

    # A6
    def A6(self, arr):
        err = None
        if arr[0][0] == ROUND_BRACE_OPEN:
            err, arr = self.A1(arr[1:])
            if err is None:
                if arr[0][0] == ROUND_BRACE_CLOSE:
                    err = 'Ожидалось ")", встречено {} [Line {}:{}]'.format(arr[0][1], arr[0][2]+1, arr[0][3])
            return err, arr

        err, arr = self.const(arr)
        if err is None:
            return err, arr
        else:
            err, arr = self.single_operator(arr)
        return err, arr




if __name__ == '__main__':
    a = SyntaxAnalizer()
    print(a.check_correct('code.txt'))






