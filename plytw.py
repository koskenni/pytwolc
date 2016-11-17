#
# plytw.py
#
import re

tokens = (
     # 'DEFINE',
     'NAME','SYMBOL','BOUND',
     # 'LCURL','RCURL','COLON'
     'BACKSLASH','SLASH','DOLLAR',
     'PLUS','STAR','OR','AND','MINUS',
     'UPPER', 'LOWER', 'INVERSE', 'COMPOSE',
     'LPAREN','RPAREN',
     'LBRACKET','RBRACKET',
     'EQUALS','LEFTARROW','RIGHTARROW','DOUBLEARROW',
     'UNDERSCORE','SEMICOLON', 'COMMA'
)

# Tokens

# t_DEFINE   = r'DEFINE'
#t_COLON   = r'\:'
#t_LCURL   = r'\{'
#t_RCURL   = r'\}'
#t_BOUND     = r'[.][#][.]'
t_BOUND     = r'§'
t_BACKSLASH = r'\\'
t_DOLLAR  = r'[$]'
t_SLASH   = r'/'
t_UPPER   = r'[.]u'
t_LOWER   = r'[.]l'
t_INVERSE = r'[.]i'
t_COMPOSE = r'[.]o[.]'
t_PLUS    = r'\+'
t_STAR    = r'\*'
t_OR      = r'\|'
t_AND     = r'\&'
t_MINUS   = r'-'
t_LPAREN  = r'\('
t_RPAREN  = r'\)'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_EQUALS  = r'='
t_LEFTARROW  = r'<='
t_RIGHTARROW  = r'=>'
t_DOUBLEARROW = r'<=>'
t_UNDERSCORE = r'\_'
t_SEMICOLON = r';'
t_COMMA = r','

t_NAME = r'<[A-ZÅÄÖa-zåäöØ][A-ZÅÄÖa-zåäØö0-9]*>'

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
    ('left', 'COMMA'),
    ('left', 'UNDERSCORE'),
    ('left', 'COMPOSE'),
    ('left', 'OR','MINUS'),
    ('left', 'AND'),
    ('left', 'CONCAT'),
    ('left', 'STAR','PLUS','UPPER','LOWER','INVERSE'),
    ('left', 'SLASH', 'BACKSLASH')
    #('right', 'DEFINE')
)

import twrl, twbt, twex
from twrl import XRC

verbosity_level = 0
definitions = {'PI': ':' }
twol_rules = {}

input_symbols = {'§'}
output_symbols = {'§'}

for insym, outsym in twex.symbol_pair_set:
    input_symbols.add(insym)
    output_symbols.add(outsym)

def p_grammar_statement(p):
    '''grammar : grammar statement
               | statement'''

def p_statement_definition(p):
    '''statement : NAME EQUALS expression SEMICOLON'''
    global definitions, XRC
    name = p[1][1:-1] # remove the enclosing < >
    str3, nam3 = p[3]
    definitions[name] = nam3 # store for display purposes and testing
    twrl.define(name, str3)
    if verbosity_level >= 1: twbt.ppdef(XRC, name, nam3)
    p[0] = ("DEFINE", name, p[3])
    if verbosity_level >= 2: print(p[0]) ##

def p_statement_left_arrow_rule(p):
    'statement : expression LEFTARROW contexts SEMICOLON'
    global twol_rules
    x_expr, x_orig = p[1]
    ctx_expr_lst, ctx_orig_lst = p[3]
    R = twrl.leftarrow(x_expr, *ctx_expr_lst)
    name = twrl.rule_name(x_orig, "<=", *ctx_orig_lst)
    R.set_name(name)
    if verbosity_level >= 1: twbt.ppfst(R, True) ##
    twol_rules[name] = R
    p[0] = ("<=", p[1], tuple(p[3]))
    if verbosity_level >= 2: print(p[0]) ##

def p_statement_right_arrow_rule(p):
    'statement : expression RIGHTARROW contexts SEMICOLON'
    global twol_rules
    x_expr, x_orig = p[1]
    ctx_expr_lst, ctx_orig_lst = p[3]
    R = twrl.rightarrow(x_expr, *ctx_expr_lst)
    name = twrl.rule_name(x_orig, "=>", *ctx_orig_lst)
    R.set_name(name)
    if verbosity_level >= 1: twbt.ppfst(R, True) ##
    twol_rules[name] = R
    p[0] = ("=>", p[1], p[3])
    if verbosity_level >= 2: print(p[0]) ##

def p_statement_double_arrow_rule(p):
    'statement : expression DOUBLEARROW contexts SEMICOLON'
    global twol_rules
    x_expr, x_orig = p[1]
    ctx_expr_lst, ctx_orig_lst = p[3]
    R = twrl.doublearrow(x_expr, *ctx_expr_lst)
    name = twrl.rule_name(x_orig, "<=>", *ctx_orig_lst)
    R.set_name(name)
    if verbosity_level >= 1: twbt.ppfst(R, True) ##
    twol_rules[name] = R
    p[0] = ("<=>", p[1], p[3])
    if verbosity_level >= 2: print(p[0]) ##

def p_contexts_contexts(p):
    '''contexts : contexts COMMA context
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
    if verbosity_level >= 3: print(p[0]) ##

def p_context_lcontext_rcontext(p):
    'context : expression UNDERSCORE expression'
    str1, nam1 = p[1]
    str3, nam3 = p[3]
    p[0] = ((str1, str3), (nam1, nam3))
    if verbosity_level >= 3: print(p[0]) ##

def p_context_rcontext(p):
    'context : UNDERSCORE expression'
    str2, nam2 = p[2]
    p[0] = (("[]", str2), ("", nam2))
    if verbosity_level >= 3: print(p[0]) ##

def p_context_lcontext(p):
    'context : expression UNDERSCORE'
    str1, nam1 = p[1]
    p[0] = ((str1, "[]"), (nam1, ""))
    if verbosity_level >= 3: print(p[0]) ##

def p_context_none(p):
    'context : UNDERSCORE'
    p[0] = (("[]", "[]"), ("", ""))
    if verbosity_level >= 3: print(p[0]) ##

def p_expression_compose(p):
    '''expression : expression COMPOSE expression2
                  | expression2'''
    if len(p) == 2:
         p[0] = p[1]
    else:
         str1, nam1 = p[1]
         str3, nam3 = p[3]
         p[0] = ("[{} {} {}]".format(str1, p[2], str3),
                 "[{} {} {}]".format(nam1, p[2], nam3))

def p_expression2_or(p):
    '''expression2 : expression2 OR expression3
                   | expression2 MINUS expression3
                   | expression3'''
    if len(p) == 2:
         p[0] = p[1]
    else:
         str1, nam1 = p[1]
         str3, nam3 = p[3]
         p[0] = ("[{} {} {}]".format(str1, p[2], str3),
                 "[{} {} {}]".format(nam1, p[2], nam3))

def p_expression3_and(p):
    '''expression3 : expression3 AND expression4
                   | expression4'''
    if len(p) == 2:
         p[0] = p[1]
    else:
         str1, nam1 = p[1]
         str3, nam3 = p[3]
         p[0] = ("[{} {} {}]".format(str1, p[2], str3),
                 "[{} {} {}]".format(nam1, p[2], nam3))

def p_expression4_concat(p):
    '''expression4 : expression4 expression5 %prec CONCAT
                   | expression5'''
    if len(p) == 2:
         p[0] = p[1]
    else:
         str1, nam1 = p[1]
         str2, nam2 = p[2]
         p[0] = ("[{} {}]".format(str1, str2),
                 "[{} {}]".format(nam1, nam2))

def p_expression5_ignore(p):
    '''expression5 : SLASH expression6
                   | expression6'''
    if len(p) == 2:
         p[0] = p[1]
    else:
         str, nam = p[2]
         p[0] = ("[PI-[{}]]".format(str), "\\[{}]".format(nam))

def p_expression6_suffix(p):
    '''expression6 : expression6 STAR
                   | expression6 PLUS
                   | expression6 UPPER
                   | expression6 LOWER
                   | expression6 INVERSE
                   | expression7'''
    if len(p) == 2:
         p[0] = p[1]
    else:
         str, nam = p[1]
         p[0] = ("[{}{}]".format(str, p[2]),
                 "[{}{}]".format(nam, p[2]))

def p_expression7_group(p):
    '''expression7 : LBRACKET expression RBRACKET
                   | LPAREN expression RPAREN'''
    str, nam = p[2]
    p[0] = ("[{}]".format(str), "[{}]".format(nam))

def p_expression7_term(p):
    '''expression7 : BACKSLASH expression7
                   | DOLLAR expression7
                   | term'''
    if len(p) == 2:
         p[0] = p[1]
    else:
         str, nam = p[2]
         p[0] = ("[{}[{}] & PI]".format(p[1], str),
                 "[{}{}]".format(p[1], nam))

def p_term_end(p):
    '''term : BOUND'''
    p[0] = ("§", "§")

def p_term_single_symbol(p):
    '''term : SYMBOL'''
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
            if (ins, outs) not in twex.symbol_pair_set:
                   print("Warning: {} is an undeclared pair".format(p[1]))
            str = "{}:{}".format(inq, outq)
        elif ins == "" and outs in output_symbols:
            str = "[PI .o. {}]".format(outq)
        elif outs == "" and ins in input_symbols:
            str = "[{} .o. PI]".format(inq)
        else:
            print(p[1], "is an undeclared symbol")
            raise SyntaxError
    elif colo == "":
        if ins in definitions and outs == "":
            str = "{}".format(ins)
        elif ins in input_symbols and ins in output_symbols:
            str = inq
        else:
            str = inq 
            print(p[1], "Warning: is an undeclared symbol")
            ### raise SyntaxError
    else:
        raise SyntaxError
    p[0] = (str, p[1])

input_lines = ""
input_list = []

def p_error(t):
    global parser, input_lines, input_list
    if not t:
        # print('EOF') ##
        return
    # if verbosity_level >= 5: print("input_lines:", input_lines) ##
    # print("lexpos:", t.lexpos) ##
    # print("lineno:", t.lineno) ##
    i = 0
    for j in range (0,t.lineno-1):
        i += len(input_list[j])
    print(input_list[t.lineno-1].strip())
    print(" "*(t.lexpos-i), "*",
          "Syntax error at '{}' in line {}".format(t.value, t.lineno))

# twrl.init() # init here if not already initialized
# print("input_symbols:", input_symbols) ##
# print("output_symbols:", output_symbols) ##
# twbt.ppdef(twrl.XRC, "PI") ##

import ply.yacc as yacc
    
def run(rule_file_name, verbosity, debugging):
    global input_lines, input_list, verbosity_level
    for insym, outsym in twex.symbol_pair_set:
        input_symbols.add(insym)
        output_symbols.add(outsym)
    rulefile = open(rule_file_name, "r")
    parser = yacc.yacc()
    verbosity_level = verbosity
    input_lines = ""
    input_list = []
    for line in rulefile:
        input_lines += line
        input_list.append(line)
    if verbosity_level >= 5: print("input lines", input_lines) ##
    parser.parse(input_lines, debug=debugging, tracking=True)

    # print('all definitions:', definitions) ##
    # print('all rules:', twol_rules) ##
    return

if __name__ == "__main__":
    import argparse
    arpar = argparse.ArgumentParser("python3 plytw.py")
    arpar.add_argument("-e", "--examples", help="name of the examples file",
                       default="test.pairstr")
    arpar.add_argument("-r", "--rules", help="name of the rule file",
                       default="test.rules")
    arpar.add_argument("-v", "--verbosity",
                       help="level of  diagnostic output",
                       type=int, default=0)
    arpar.add_argument("-d", "--debug",
                       help="level of PLY debugging output",
                       type=int, default=0)
    args = arpar.parse_args()
    twex.read_examples(args.examples) ## read here if not already read
    # print(twex.symbol_pair_set) ##
    twrl.init()
    run(args.rules, args.verbosity, args.debug)
