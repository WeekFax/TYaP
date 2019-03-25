from scaner import *
from structure import *

class SyntaxAnalizerV2:
    def __init__(self):
        self.t = TScaner()

    def make_err(self, expect, elem):
        return 'Ожидался {}, встречено {} [Line {}:{}]'.format(expect, elem[1], elem[2]+1, elem[3]+1)

    def check_correct(self, filename):
        arr = self.t.getData(filename)
        err = [e for e in arr if e[0] == ERROR]
        # arr = np.array(arr)
        if len(err) > 0:
            for e in err:
                print(e[1])
            return None
        else:
            print('Сканер: ошибок не обнаружено')
            return arr

    def get_layers(self, filename, show=False):
        lex_arr = self.check_correct(filename)
        return Layer(lex_arr, show=show)









