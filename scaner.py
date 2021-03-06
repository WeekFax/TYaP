MAX_LEX_LEN = 20
TYPE_INT = 1
TYPE_SINT = 2
INT = 11
LINT = 12
FOR = 13
TYPEDEF = 14
BREAK = 15
ID = 16
MAIN = 17
ASSIGN = 20
EQUAL = 21
MORE = 22
MORE_EQUAL = 23
LESS = 24
LESS_EQUAL = 25
ROUND_BRACE_OPEN = 26
ROUND_BRACE_CLOSE = 27
PLUS = 30
MINUS = 31
SLASH = 32
DOT = 33
STAR = 34
PERCENT = 35
CURLY_BRACE_OPEN = 40
CURLY_BRACE_CLOSE = 41
SEMICOLON = 42
COMMA = 43
SQUARE_BRACE_OPEN = 44
SQUARE_BRACE_CLOSE = 45
OR = 46
AND = 47
ERROR = 100
END = 200


class TScaner():
    def __init__(self, t=''):
        self.t = t+b'\0'.decode()
        self.uk = 0
        self.numLine = 0
        self.numInLine = 0


    def Num(self):
        if (self.t[self.uk] >= '0') and (self.t[self.uk] <= '9'):
            return True
        else:
            return False

    def HexLetter(self):
        if (self.t[self.uk] >= 'a') and (self.t[self.uk] <= 'f'):
            return True
        elif (self.t[self.uk] >= 'A') and (self.t[self.uk] <= 'F'):
            return True
        else:
            return False

    def Letter(self):
        if (self.t[self.uk] >= 'a') and (self.t[self.uk] <= 'z'):
            return True
        elif (self.t[self.uk] >= 'A') and (self.t[self.uk] <= 'Z'):
            return True
        elif self.t[self.uk] == '_':
            return True
        else:
            return False

    def getData(self, file_name):
        f = open(file_name, 'r')
        self.t = ''
        for line in f.readlines():
            self.t += line
        self.t += b'\0'.decode()
        self.uk = 0

        arr = []
        sc = self.Scanner()
        arr.append([sc[0], sc[1], sc[2], sc[3]])
        while sc[0] != END:
            sc = self.Scanner()
            arr.append([sc[0], sc[1], sc[2], sc[3]])

        return arr

    def getUK(self):
        return self.uk, self.numLine, self.numInLine

    def setUK(self, uk):
        self.uk, self.numLine, self.numInLine = uk

    def Scanner(self):

        # Счтываение лексемы
        lex = ''
        while self.t[self.uk] == ' ' or self.t[self.uk] == '\n' or self.t[self.uk] == '\t' or self.t[self.uk] == '/':
            if self.t[self.uk] == '/':
                lex += self.t[self.uk]
                self.numInLine += 1
                self.uk += 1
                if self.t[self.uk] == '/':
                    while not (self.t[self.uk] == '\n' or self.t[self.uk] == '\0'):
                        self.uk += 1
                        self.numInLine += 1
                    lex = ''
                else:
                    return SLASH, lex, self.numLine, self.numInLine
            # Пропуск незначительных элементов
            while self.t[self.uk] == ' ' or self.t[self.uk] == '\n' or self.t[self.uk] == '\t':
                if self.t[self.uk] == '\n':
                    self.numInLine = 0
                    self.numLine += 1
                else:
                    self.numInLine += 1
                self.uk += 1

        numInLine = self.numInLine

        # Если первый символ буква
        if self.Letter():
            i = 0
            while (self.Letter() or self.Num()) and i<MAX_LEX_LEN:
                lex = lex + self.t[self.uk]
                self.uk += 1
                self.numInLine += 1
                i += 1
            if lex == 'break':
                return BREAK, lex, self.numLine, numInLine
            elif lex == 'typedef':
                return TYPEDEF, lex, self.numLine, numInLine
            elif lex == 'for':
                return FOR, lex, self.numLine, numInLine
            elif lex == 'int':
                return INT, lex, self.numLine, numInLine
            elif lex == '__int64':
                return LINT, lex, self.numLine, numInLine
            else:
                return ID, lex, self.numLine, numInLine

        # Если первый символ цифра
        if self.Num():
            i = 0
            if self.t[self.uk] == '0':
                lex += self.t[self.uk]
                self.numInLine += 1
                self.uk += 1
                i += 1
                if self.t[self.uk] == 'x':
                    lex += self.t[self.uk]
                    self.numInLine += 1
                    self.uk += 1
                    i += 1
                    while (self.Num() or self.HexLetter()) and i < MAX_LEX_LEN:
                        lex += self.t[self.uk]
                        self.numInLine += 1
                        self.uk += 1
                        i += 1
                    if self.Letter():
                        return ERROR, 'Неверная константа в троке {}'.format(self.numLine+1), self.numLine, numInLine
                    return TYPE_SINT, lex, self.numLine, numInLine

            while self.Num() and i < MAX_LEX_LEN:
                lex += self.t[self.uk]
                self.numInLine += 1
                self.uk += 1
                i += 1
            if self.Letter():
                return ERROR, 'Неверная константа в троке {}'.format(self.numLine+1), self.numLine, numInLine
            return TYPE_INT, lex, self.numLine, numInLine

        if self.t[self.uk] == '=':
            lex += self.t[self.uk]
            self.numInLine += 1
            self.uk += 1
            if self.t[self.uk] == '=':
                lex += self.t[self.uk]
                self.numInLine += 1
                self.uk += 1
                return EQUAL, lex, self.numLine, numInLine
            return ASSIGN, lex, self.numLine, numInLine

        if self.t[self.uk] == '>':
            lex += self.t[self.uk]
            self.numInLine += 1
            self.uk += 1
            if self.t[self.uk] == '=':
                lex += self.t[self.uk]
                self.numInLine += 1
                self.uk += 1
                return MORE_EQUAL, lex, self.numLine, numInLine
            return MORE, lex, self.numLine, numInLine

        if self.t[self.uk] == '<':
            lex += self.t[self.uk]
            self.numInLine += 1
            self.uk += 1
            if self.t[self.uk] == '=':
                lex += self.t[self.uk]
                self.numInLine += 1
                self.uk += 1
                return LESS_EQUAL, lex, self.numLine, numInLine
            return LESS, lex, self.numLine, numInLine

        if self.t[self.uk] == '+':
            lex += self.t[self.uk]
            self.numInLine += 1
            self.uk += 1
            return PLUS, lex, self.numLine, numInLine

        if self.t[self.uk] == '-':
            lex += self.t[self.uk]
            self.numInLine += 1
            self.uk += 1
            return MINUS, lex, self.numLine, numInLine

        if self.t[self.uk] == '*':
            lex += self.t[self.uk]
            self.numInLine += 1
            self.uk += 1
            return STAR, lex, self.numLine, numInLine

        if self.t[self.uk] == '%':
            lex += self.t[self.uk]
            self.numInLine += 1
            self.uk += 1
            return PERCENT, lex, self.numLine, numInLine

        if self.t[self.uk] == '(':
            lex += self.t[self.uk]
            self.numInLine += 1
            self.uk += 1
            return ROUND_BRACE_OPEN, lex, self.numLine, numInLine

        if self.t[self.uk] == ')':
            lex += self.t[self.uk]
            self.numInLine += 1
            self.uk += 1
            return ROUND_BRACE_CLOSE, lex, self.numLine, numInLine

        if self.t[self.uk] == '{':
            lex += self.t[self.uk]
            self.numInLine += 1
            self.uk += 1
            return CURLY_BRACE_OPEN, lex, self.numLine, numInLine

        if self.t[self.uk] == '}':
            lex += self.t[self.uk]
            self.numInLine += 1
            self.uk += 1
            return CURLY_BRACE_CLOSE, lex, self.numLine, numInLine

        if self.t[self.uk] == '[':
            lex += self.t[self.uk]
            self.numInLine += 1
            self.uk += 1
            return SQUARE_BRACE_OPEN, lex, self.numLine, numInLine

        if self.t[self.uk] == ']':
            lex += self.t[self.uk]
            self.numInLine += 1
            self.uk += 1
            return SQUARE_BRACE_CLOSE, lex, self.numLine, numInLine

        if self.t[self.uk] == ';':
            lex += self.t[self.uk]
            self.numInLine += 1
            self.uk += 1
            return SEMICOLON, lex, self.numLine, numInLine

        if self.t[self.uk] == '.':
            lex += self.t[self.uk]
            self.numInLine += 1
            self.uk += 1
            return DOT, lex, self.numLine, numInLine

        if self.t[self.uk] == ',':
            lex += self.t[self.uk]
            self.numInLine += 1
            self.uk += 1
            return COMMA, lex, self.numLine, numInLine

        # Если конец выходим
        if self.t[self.uk] == '\0':
            return END, 'Конец строки', self.numLine, numInLine

        self.uk+=1
        self.numInLine+=1
        return ERROR, 'Неверный символ [{}:{}]: "{}({})"'.format(self.numLine, self.numInLine+1,
                                                                 self.t[self.uk-1], self.t[self.uk-1].encode()[0]), \
               self.numLine, numInLine
