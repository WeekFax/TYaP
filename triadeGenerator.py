from scaner import *


def get_triade(lex_arr):
    return operator(lex_arr)


def operator(lex_arr):
    if lex_arr[0][0] == BREAK:
        return {'type': 'break', 'f': lex_arr[0:1], 's': None}
    else:
        return A1(lex_arr)[0]


def A1(lex_arr):
    triade_A2, lex_arr_A2 = A2(lex_arr)
    if lex_arr_A2[0][0] == EQUAL or lex_arr_A2[0][0] == LESS_EQUAL or lex_arr_A2[0][0] == MORE_EQUAL or \
        lex_arr_A2[0][0] == LESS or lex_arr_A2[0][0] == MORE:
        if lex_arr_A2[0][0] == EQUAL:
            A1_type = 'equal'
        elif lex_arr_A2[0][0] == LESS_EQUAL:
            A1_type = 'less_equal'
        elif lex_arr_A2[0][0] == MORE_EQUAL:
            A1_type = 'more_equal'
        elif lex_arr_A2[0][0] == LESS:
            A1_type = 'less'
        else:
            A1_type = 'more'

        triade_A1, lex_arr_A1 = A1(lex_arr_A2[1:])
        return {'type': A1_type, 'f': triade_A2, 's': triade_A1}, lex_arr_A1
    return triade_A2, lex_arr_A2


def A2(lex_arr):
    triade_A3, lex_arr_A3 = A3(lex_arr)
    if lex_arr_A3[0][0] == PLUS or lex_arr_A3[0][0] == MINUS:
        if lex_arr_A3[0][0] == PLUS:
            A2_type = 'plus'
        else:
            A2_type = 'minus'
        triade_A2, lex_arr_A2 = A2(lex_arr_A3[1:])
        return {'type': A2_type, 'f': triade_A3, 's': triade_A2}, lex_arr_A2
    return triade_A3, lex_arr_A3


def A3(lex_arr):
    triade_A4, lex_arr_A4 = A4(lex_arr)
    if lex_arr_A4[0][0] == PERCENT or lex_arr_A4[0][0] == STAR or lex_arr_A4[0][0] == SLASH:
        if lex_arr_A4[0][0] == PERCENT:
            A3_type = 'percent'
        elif lex_arr_A4[0][0] == STAR:
            A3_type = 'star'
        else:
            A3_type = 'slash'
        triade_A3, lex_arr_A3 = A3(lex_arr_A4[1:])
        return {'type': A3_type, 'f': triade_A4, 's': triade_A3}, lex_arr_A3
    return triade_A4, lex_arr_A4


def A4(lex_arr):
    triade_A5, lex_arr_A5 = A5(lex_arr)
    if lex_arr_A5[0][0] == PLUS and lex_arr_A5[1][0] == PLUS or lex_arr_A5[0][0] == MINUS and lex_arr_A5[1][0] == MINUS:
        if lex_arr_A5[0][0] == PLUS:
            A5_type = 'post_increment'
        else:
            A5_type = 'post_decrement'
        return {'type': A5_type, 'f': triade_A5, 's': None}, lex_arr_A5[2:]
    return triade_A5, lex_arr_A5


def A5(lex_arr):
    if lex_arr[0][0] == PLUS and lex_arr[1][0] == PLUS or lex_arr[0][0] == MINUS and lex_arr[1][0] == MINUS or \
        lex_arr[0][0] == PLUS or lex_arr[0][0] == MINUS:
        if lex_arr[0][0] == PLUS and lex_arr[1][0] == PLUS:
            A5_type = 'pref_increment'
            lex_arr = lex_arr[2:]
        elif lex_arr[0][0] == MINUS and lex_arr[1][0] == MINUS:
            A5_type = 'pref_decrement'
            lex_arr = lex_arr[2:]
        elif lex_arr[0][0] == PLUS:
            A5_type = 'sign_plus'
            lex_arr = lex_arr[1:]
        else:
            A5_type = 'sign_minus'
            lex_arr = lex_arr[1:]
        triade_A5, lex_arr_A5 = A5(lex_arr)
        return {'type': A5_type, 'f': triade_A5, 's': None}
    return A6(lex_arr)


def A6(lex_arr):
    if lex_arr[0][0] == TYPE_INT or lex_arr[0][0] == TYPE_SINT:
        return {'type': 'const', 'f': lex_arr[0][1], 's': None}, lex_arr[1:]
    if lex_arr[0][0] ==ROUND_BRACE_OPEN:
        triade_A1, lex_arr_A1 = A1(lex_arr[1:])
        return triade_A1, lex_arr_A1[1:]
    return single_operator(lex_arr)


def single_operator(lex_arr):

    if lex_arr[1][0] == ID:
        ident = {'type': 'variable', 'f': lex_arr[1], 's': None}
        lex_arr = lex_arr[2:]
        isident = True
    else:
        ident = {'type': 'variable', 'f': lex_arr[0], 's': None}
        lex_arr = lex_arr[1:]
        isident = False

    if lex_arr[0][0] == ROUND_BRACE_OPEN:
        params = []
        triade_A1, lex_arr = A1(lex_arr[1:])
        params.append(triade_A1)
        while lex_arr[0][0] == COMMA:
            triade_A1, lex_arr = A1(lex_arr[1:])
            params.append(triade_A1)
        return {'type': 'function', 'f': ident, 's': params}, lex_arr[1:]

    iter_triade = None
    while lex_arr[0][0] == SQUARE_BRACE_OPEN:
        triade_A1, lex_arr = A1(lex_arr[1:])
        if iter_triade == None:
            iter_triade = {'type': 'iterator', 'f': ident, 's': triade_A1}
        else:
            iter_triade = {'type': 'iterator', 'f': iter_triade, 's': triade_A1}
        lex_arr = lex_arr[1:]

    if iter_triade is not None:
        ident = iter_triade


    if lex_arr[0][0] == ASSIGN:
        triade_A1, lex_arr = A1(lex_arr[1:])
        return {'type': 'assign', 'f': ident, 's': triade_A1}, lex_arr
    if lex_arr[0][0] == MINUS and lex_arr[1][0] == ASSIGN:
        triade_A1, lex_arr = A1(lex_arr[2:])
        return {'type': 'assign_minus', 'f': ident, 's': triade_A1}, lex_arr
    if lex_arr[0][0] == PLUS and lex_arr[1][0] == ASSIGN:
        triade_A1, lex_arr = A1(lex_arr[2:])
        return {'type': 'assign_plus', 'f': ident, 's': triade_A1}, lex_arr
    if lex_arr[0][0] == PERCENT and lex_arr[1][0] == ASSIGN:
        triade_A1, lex_arr = A1(lex_arr[2:])
        return {'type': 'assign_percent', 'f': ident, 's': triade_A1}, lex_arr
    if lex_arr[0][0] == STAR and lex_arr[1][0] == ASSIGN:
        triade_A1, lex_arr = A1(lex_arr[2:])
        return {'type': 'assign_star', 'f': ident, 's': triade_A1}, lex_arr
    if lex_arr[0][0] == SLASH and lex_arr[1][0] == ASSIGN:
        triade_A1, lex_arr = A1(lex_arr[2:])
        return {'type': 'assign_slash', 'f': ident, 's': triade_A1}, lex_arr
    if isident:
        return {'type': 'ident', 'f': ident, 's': None}, lex_arr
    else:
        return ident, lex_arr











