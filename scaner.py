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
        elif (self.t[self.uk] >= 'A') and (self[self.uk] <= 'F'):
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
                self.uk += 1


        # Если первый символ буква
        if self.Letter():
            i = 0
            while (self.Letter() or self.Num()) and i<MAX_LEX_LEN:
                lex = lex + self.t[self.uk]
                self.uk += 1
                self.numInLine += 1
                i += 1
            if lex == 'main':
                return MAIN, lex, self.numLine, self.numInLine
            elif lex == 'break':
                return BREAK, lex, self.numLine, self.numInLine
            elif lex == 'typedef':
                return TYPEDEF, lex, self.numLine, self.numInLine
            elif lex == 'for':
                return FOR, lex, self.numLine, self.numInLine
            elif lex == 'int':
                return INT, lex, self.numLine, self.numInLine
            elif lex == '__int64':
                return LINT, lex, self.numLine, self.numInLine
            else:
                return ID, lex, self.numLine, self.numInLine

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
                        return ERROR, 'Неверная константа в троке {}'.format(self.numLine+1), self.numLine, self.numInLine
                    return TYPE_SINT, lex, self.numLine, self.numInLine

            while self.Num() and i < MAX_LEX_LEN:
                lex += self.t[self.uk]
                self.numInLine += 1
                self.uk += 1
                i += 1
            if self.Letter():
                return ERROR, 'Неверная константа в троке {}'.format(self.numLine+1), self.numLine, self.numInLine
            return TYPE_INT, lex, self.numLine, self.numInLine

        if self.t[self.uk] == '=':
            lex += self.t[self.uk]
            self.numInLine += 1
            self.uk += 1
            if self.t[self.uk] == '=':
                lex += self.t[self.uk]
                self.numInLine += 1
                self.uk += 1
                return EQUAL, lex, self.numLine, self.numInLine
            return ASSIGN, lex, self.numLine, self.numInLine

        if self.t[self.uk] == '>':
            lex += self.t[self.uk]
            self.numInLine += 1
            self.uk += 1
            if self.t[self.uk] == '=':
                lex += self.t[self.uk]
                self.numInLine += 1
                self.uk += 1
                return MORE_EQUAL, lex, self.numLine, self.numInLine
            return MORE, lex, self.numLine, self.numInLine

        if self.t[self.uk] == '<':
            lex += self.t[self.uk]
            self.numInLine += 1
            self.uk += 1
            if self.t[self.uk] == '=':
                lex += self.t[self.uk]
                self.numInLine += 1
                self.uk += 1
                return LESS_EQUAL, lex, self.numLine, self.numInLine
            return LESS, lex, self.numLine, self.numInLine

        if self.t[self.uk] == '+':
            lex += self.t[self.uk]
            self.numInLine += 1
            self.uk += 1
            return PLUS, lex, self.numLine, self.numInLine

        if self.t[self.uk] == '-':
            lex += self.t[self.uk]
            self.numInLine += 1
            self.uk += 1
            return MINUS, lex, self.numLine, self.numInLine

        if self.t[self.uk] == '*':
            lex += self.t[self.uk]
            self.numInLine += 1
            self.uk += 1
            return STAR, lex, self.numLine, self.numInLine

        if self.t[self.uk] == '%':
            lex += self.t[self.uk]
            self.numInLine += 1
            self.uk += 1
            return PERCENT, lex, self.numLine, self.numInLine

        if self.t[self.uk] == '(':
            lex += self.t[self.uk]
            self.numInLine += 1
            self.uk += 1
            return ROUND_BRACE_OPEN, lex, self.numLine, self.numInLine

        if self.t[self.uk] == ')':
            lex += self.t[self.uk]
            self.numInLine += 1
            self.uk += 1
            return ROUND_BRACE_CLOSE, lex, self.numLine, self.numInLine

        if self.t[self.uk] == '{':
            lex += self.t[self.uk]
            self.numInLine += 1
            self.uk += 1
            return CURLY_BRACE_OPEN, lex, self.numLine, self.numInLine

        if self.t[self.uk] == '}':
            lex += self.t[self.uk]
            self.numInLine += 1
            self.uk += 1
            return CURLY_BRACE_CLOSE, lex, self.numLine, self.numInLine

        if self.t[self.uk] == '[':
            lex += self.t[self.uk]
            self.numInLine += 1
            self.uk += 1
            return SQUARE_BRACE_OPEN, lex, self.numLine, self.numInLine

        if self.t[self.uk] == ']':
            lex += self.t[self.uk]
            self.numInLine += 1
            self.uk += 1
            return SQUARE_BRACE_CLOSE, lex, self.numLine, self.numInLine

        if self.t[self.uk] == ';':
            lex += self.t[self.uk]
            self.numInLine += 1
            self.uk += 1
            return SEMICOLON, lex, self.numLine, self.numInLine

        if self.t[self.uk] == '.':
            lex += self.t[self.uk]
            self.numInLine += 1
            self.uk += 1
            return DOT, lex, self.numLine, self.numInLine

        if self.t[self.uk] == ',':
            lex += self.t[self.uk]
            self.numInLine += 1
            self.uk += 1
            return COMMA, lex, self.numLine, self.numInLine

        # Если конец выходим
        if self.t[self.uk] == '\0':
            return END, '', self.numLine, self.numInLine

        self.uk+=1
        self.numInLine+=1
        return ERROR, 'Неверный символ [{}:{}]: "{}({})"'.format(self.numLine, self.numInLine+1,
                                                                 self.t[self.uk-1], self.t[self.uk-1].encode()[0]), \
               self.numLine, self.numInLine
