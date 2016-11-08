#
# plytw.py
#
import re

tokens = (
    # 'DEFINE',
    'NAME','SYMBOL','BOUND',
    # 'LCURL','RCURL','COLON'
    'PLUS','STAR','OR','AND','MINUS',
    'UPPER', 'LOWER', 'COMPOSE',
    # 'LPAREN','RPAREN',
    'LBRACKET','RBRACKET',
    'EQUALS','LEFTARROW','RIGHTARROW','DOUBLEARROW',
    'UNDERSCORE','SEMICOLON'
    )

# Tokens

# t_DEFINE   = r'DEFINE'
#t_COLON   = r'\:'
#t_LCURL   = r'\{'
#t_RCURL   = r'\}'
#t_BOUND     = r'[.][#][.]'
t_BOUND     = r'§'
t_UPPER   = r'[.]u'
t_LOWER   = r'[.]l'
t_COMPOSE = r'[.]o[.]'
t_PLUS    = r'\+'
t_STAR    = r'\*'
t_OR      = r'\|'
t_AND     = r'\&'
t_MINUS   = r'-'
#t_LPAREN  = r'\('
#t_RPAREN  = r'\)'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_EQUALS  = r'='
t_LEFTARROW  = r'<='
t_RIGHTARROW  = r'=>'
t_DOUBLEARROW = r'<=>'
t_UNDERSCORE = r'\_'
t_SEMICOLON = r';'

t_NAME = r'<[A-ZÅÄÖa-zåäö][A-ZÅÄÖa-zåäö0-9]*>'

def t_SYMBOL(t):
     r'[{a-zåäöA-ZÅÄÖØ:{}][a-zåäöA-ZÅÄÖ0-9Ø:{}]*'
     #print("t.value =", t.value)
     return(t)

def t_COMMENT(t):
    r'\!.*'
    pass
    # No return value. Token discarded

# Ignored characters
t_ignore = " \t"

def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")
    
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)
    
# Build the lexer
import ply.lex as lex
lexer = lex.lex()

#lex.input("{ij}:j <=> :V :Ø* _ :Ø* :V")
#while True:
#    tok = lex.token()
#    if not tok: break
#    print(tok)



# Parsing rules

precedence = (
    ('left', 'SEMICOLON'),
    ('left', 'UNDERSCORE'),
    ('right', 'COMPOSE'),
    ('right','OR','MINUS'),
    ('right','AND'),
    ('right', 'CONCAT'),
    ('left','STAR','PLUS'),
    #('right', 'DEFINE')
)

import twrl, twbt, twex
definitions = {'PI': ':' }
twol_rules = {}

input_symbols = {'§'}
output_symbols = {'§'}
twex.read_examples()
# print(twex.symbol_pair_set) ##
for insym, outsym in twex.symbol_pair_set:
    input_symbols.add(insym)
    output_symbols.add(outsym)

def p_statement_definition(p):
    'statement : NAME EQUALS expression'
    global definitions
    name = p[1][1:-1] # remove the enclosing < >
    str3, nam3 = p[3]
    definitions[name] = nam3 # store for display purposes and testing
    twrl.define(name, str3)
    twbt.ppdef(twrl.XRC, name, nam3)
    p[0] = ("DEFINE", name, p[3])
    #print(p[0]) ##

def p_statement_left_arrow_rule(p):
    'statement : expression LEFTARROW contexts'
    x_expr, x_orig = p[1]
    ctx_expr_lst, ctx_orig_lst = p[3]
    R = twrl.leftarrow(x_expr, *ctx_expr_lst)
    name = twrl.rule_name(x_orig, "<=", *ctx_orig_lst)
    R.set_name(name)
    twbt.ppfst(R, True)
    twol_rules[name] = R
    p[0] = ("<=", p[1], tuple(p[3]))
    # print(p[0]) ##

def p_statement_right_arrow_rule(p):
    'statement : expression RIGHTARROW contexts'
    x_expr, x_orig = p[1]
    ctx_expr_lst, ctx_orig_lst = p[3]
    R = twrl.rightarrow(x_expr, *ctx_expr_lst)
    name = twrl.rule_name(x_orig, "=>", *ctx_orig_lst)
    R.set_name(name)
    twbt.ppfst(R, True)
    twol_rules[name] = R
    p[0] = ("=>", p[1], p[3])
    # print(p[0]) ##

def p_statement_double_arrow_rule(p):
    'statement : expression DOUBLEARROW contexts'
    x_expr, x_orig = p[1]
    ctx_expr_lst, ctx_orig_lst = p[3]
    R = twrl.doublearrow(x_expr, *ctx_expr_lst)
    name = twrl.rule_name(x_orig, "<=>", *ctx_orig_lst)
    R.set_name(name)
    twbt.ppfst(R, True)
    twol_rules[name] = R
    p[0] = ("<=>", p[1], p[3])
    # print(p[0]) ##

def p_contexts_contexts(p):
    '''contexts : contexts SEMICOLON context
                | context'''
    s1, n1 = p[1]
    if len(p) == 4:
        s3, n3 = p[3]
        ls1 = s1.copy()
        ln1 = n1.copy()
        ls1.append(s3)
        ln1.append(n3)
        p[0] = (ls1, ln1)
    elif len(p) == 2:
        p[0] = ([s1], [n1])
    # print(p[0]) ##

def p_context_lcontext_rcontext(p):
    'context : expression UNDERSCORE expression'
    str1, nam1 = p[1]
    str3, nam3 = p[3]
    p[0] = ((str1, str3), (nam1, nam3))
    # print(p[0]) ##

def p_context_rcontext(p):
    'context : UNDERSCORE expression'
    str2, nam2 = p[2]
    p[0] = (("[]", str2), ("", nam2))
    # print(p[0]) ##

def p_context_lcontext(p):
    'context : expression UNDERSCORE'
    str1, nam1 = p[1]
    p[0] = ((str1, "[]"), (nam1, ""))
    # print(p[0]) ##

def p_context_none(p):
    'context : UNDERSCORE'
    p[0] = (("[]", "[]"), ("", ""))
    # print(p[0]) ##

def p_expression_composables(p):
    '''expression : expression COMPOSE orable'''
    str1, nam1 = p[1]
    str3, nam3 = p[3]
    p[0] = ("{} .o. {}".format(str1, str3),
            "{} .o. {}".format(nam1, nam3))

def p_expression_composable(p):
    '''expression : orable'''
    p[0] = p[1]

def p_orable_andables(p):
    '''orable : orable OR andable'''
    # print("orable:", p[1], p[3])
    str1, nam1 = p[1]
    str3, nam3 = p[3]
    p[0] = ("{} | {}".format(str1, str3),
            "{}|{}".format(nam1, nam3))
    # print(p[0]) ##

def p_orable_minus(p):
    '''orable : orable MINUS andable'''
    str1, nam1 = p[1]
    str3, nam3 = p[3]
    p[0] = ("{} - {}".format(str1, str3), "{}-{}".format(nam1, nam3))
    # print(p[0]) ##

def p_orable_andable(p):
    '''orable : andable'''
    p[0] = p[1]
    # print(p[0]) ##

def p_andable_and(p):
    '''andable : andable AND catenable'''
    str1, nam1 = p[1]
    str3, nam3 = p[3]
    p[0] = ("[{} & {}]".format(str1, str3),
            "[{}&{}]".format(nam1, nam3))
    # print(p[0]) ##

def p_andable_catenable(p):
    '''andable : catenable'''
    p[0] = p[1]
    # print(p[0]) ##

def p_catenable_concat(p):
    '''catenable : catenable ignorable %prec CONCAT'''
    str1, nam1 = p[1]
    str2, nam2 = p[2]
    p[0] = ("{} {}".format(str1, str2),
            "{} {}".format(nam1, nam2))

def p_catenable_ignorable(p):
    '''catenable : ignorable'''
    p[0] = p[1]

def p_ignorable_suffixable(p):
    '''ignorable : suffixable'''
    p[0] = p[1]

def p_suffixable_star(p):
    'suffixable : suffixable STAR'
    str, nam = p[1]
    p[0] = ("{}*".format(str), "{}*".format(nam))

def p_suffixable_upper(p):
    'suffixable : suffixable UPPER'
    str, nam = p[1]
    p[0] = ("{}.u".format(str), "{}.u".format(nam))

def p_suffixable_lower(p):
    'suffixable : suffixable LOWER'
    str, nam = p[1]
    p[0] = ("{}.l".format(str), "{}.l".format(nam))

def p_suffixable_plus(p):
    'suffixable : suffixable PLUS'
    str, nam = p[1]
    p[0] = ("{}+".format(str), "{}+".format(nam))

def p_suffixable_prefixable(p):
    'suffixable : prefixable'
    p[0] = p[1]

def p_prefixable_group(p):
    'prefixable : LBRACKET expression RBRACKET'
    str, nam = p[2]
    p[0] = ("[{}]".format(str), "[{}]".format(nam))

def p_prefixable_end(p):
    '''prefixable : BOUND'''
    p[0] = ("§", "§")

def p_prefixable_single_symbol(p):
    '''prefixable : SYMBOL'''
    global input_symbols, output_symbols
    m = re.match(r"^([{}a-zåäöA-ZÅÄÖØ]*)([:]?)([a-zåäöA-ZÅÄÖØ]*)$",
                 p[1])
    if not m:
        raise SyntaxError
    ins, colo, outs = m.groups()
    inq = re.sub(r"([{}])", r"%\1", ins)
    outq = re.sub(r"([{}])", r"%\1", outs)
    if colo == ":":
        if ins == "" and outs == "":
            str = "PI"
        elif ins in input_symbols and outs in output_symbols:
            str = "{}:{}".format(inq, outq)
        elif ins == "" and outs in output_symbols:
            str = "[PI .o. {}]".format(outq)
        elif outs == "" and ins in input_symbols:
            str = "[{} .o. PI]".format(inq)
        else:
            print(p[1], "is an udeclared symbol")
            raise SyntaxError
    elif colo == "":
        if ins in definitions and outs == "":
            str = "{}".format(ins)
        elif ins in input_symbols and ins in output_symbols:
            str = inq
        else:
            print(p[1], "is an udeclared symbol")
            raise SyntaxError
    else:
        raise SyntaxError
    p[0] = (str, p[1])

def p_error(t):
    global parser, s
    if not t:
        print('EOF')
        return
    print(s)
    print(" "*(t.lexpos-1), "*",
          "Syntax error at '{}'".format(t.value))
    # print(parser.token(), dir(parser.token()))
    # dir(t)

twrl.init()
# print("input_symbols:", input_symbols) ##
# print("output_symbols:", output_symbols) ##
# twbt.ppdef(twrl.XRC, "PI") ##
    
import ply.yacc as yacc
parser = yacc.yacc()

while True:
    try:
        s = input('')   # Use raw_input on Python 2
        #print(s)
    except EOFError:
        break
    parser.parse(s, debug=1, tracking=True)

# print('all definitions:', definitions) ##
# print('all rules:', twol_rules) ##
