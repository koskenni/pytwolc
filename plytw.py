#
# plytw.py
#
import re

tokens = (
    'SYMBOL', 'BEGIN', 'END',
    'BACKSLASH', 'SLASH', 'DOLLAR',
    'PLUS', 'STAR', 'OR', 'AND', 'MINUS',
    'UPPER', 'LOWER', 'INVERSE', 'COMPOSE',
    'LPAREN', 'RPAREN',
    'LBRACKET', 'RBRACKET',
    'EQUALS', 'LEFTARROW', 'RIGHTARROW', 'DOUBLEARROW', 'EXCLUSION',
    'UNDERSCORE', 'SEMICOLON', 'COMMA'
)

# Tokens

#t_BOUND     = r'[.][#][.]'
t_BEGIN   = r'BEGIN'
t_END     = r'END' 
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
t_EXCLUSION = r'/<='
t_UNDERSCORE = r'\_'
t_SEMICOLON = r';'
t_COMMA = r','

# t_NAME = r'<[A-ZÅÄÖa-zåäöØ][A-ZÅÄÖa-zåäØö0-9]*>'

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
    #print("Illegal character '%s'" % t.value[0])
    print(input_line)
    print(" "*(t.lexpos-1), "*", "Illegal token",  t.value)
    t.lexer.skip(1)
    
# Build the lexer
import ply.lex as lex
lexer = lex.lex()

# Parsing rules

precedence = (
    ('left', 'SEMICOLON'),
    ('left', 'COMMA'),
    ('nonassoc', 'UNDERSCORE'),
    ('left', 'COMPOSE'),
    ('left', 'OR','MINUS'),
    ('left', 'AND'),
    ('left', 'CONCAT'),
    ('left', 'STAR','PLUS','UPPER','LOWER','INVERSE'),
    ('right', 'SLASH', 'BACKSLASH')
)

import twex

verbosity_level = 0
definitions = {'PI': ':' }
twol_rules = {}

input_symbols = {'BEGIN', 'END'}
output_symbols = {'BEGIN', 'END'}

def rule_name(x, op, *contexts):
    return(x + " " +op + " " +
           " ; ".join([lc + " _ " + rc for lc, rc in contexts]))

def p_grammar_statement(p):
    '''grammar : grammar statement
               | statement'''
    p[0] = p[1]

def p_statement_definition(p):
    '''statement : SYMBOL EQUALS expression SEMICOLON'''
    global definitions
    defined_name = p[1]
    if not re.fullmatch(r'[a-zåäöA-ZÅÄÖ][a-zåäöA-ZÅÄÖ0-9]*', defined_name):
        print_error(p, "Incorrect name for a defined expression: ", p[1])
    rexp3, orig3 = p[3]
    definitions[defined_name] = orig3 # store for display purposes and testing
    p[0] = ("=", defined_name, rexp3, defined_name + " = " + orig3)

def p_statement_left_arrow_rule(p):
    'statement : expression LEFTARROW contexts SEMICOLON'
    global twol_rules
    x_expr, x_orig = p[1]
    ctx_expr_lst, ctx_orig_lst = p[3]
    name = rule_name(x_orig, "<=", *ctx_orig_lst)
    p[0] = ("<=", x_expr, ctx_expr_lst, name)

def p_statement_right_arrow_rule(p):
    'statement : expression RIGHTARROW contexts SEMICOLON'
    global twol_rules
    x_expr, x_orig = p[1]
    ctx_expr_lst, ctx_orig_lst = p[3]
    name = rule_name(x_orig, "=>", *ctx_orig_lst)
    p[0] = ("=>", x_expr, ctx_expr_lst, name)

def p_statement_double_arrow_rule(p):
    'statement : expression DOUBLEARROW contexts SEMICOLON'
    global twol_rules
    x_expr, x_orig = p[1]
    ctx_expr_lst, ctx_orig_lst = p[3]
    name = rule_name(x_orig, "<=>", *ctx_orig_lst)
    p[0] = ("<=>", x_expr, ctx_expr_lst, name)
    if verbosity_level >= 2: print(p[0]) ##

def p_statement_exclusion_rule(p):
    'statement : expression EXCLUSION contexts SEMICOLON'
    global twol_rules
    x_expr, x_orig = p[1]
    ctx_expr_lst, ctx_orig_lst = p[3]
    name = rule_name(x_orig, "/<=", *ctx_orig_lst)
    p[0] = ("/<=", x_expr, ctx_expr_lst, name)


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

def p_empty(p):
    'empty :'
    pass

def p_context_lcontext_rcontext(p):
    'context : expression UNDERSCORE expression'
    rexp1, orig1 = p[1]
    rexp3, orig3 = p[3]
    p[0] = ((rexp1, rexp3), (orig1, orig3))
    if verbosity_level >= 3: print(p[0]) ##

def p_context_rcontext(p):
    'context : UNDERSCORE expression'
    rexp2, orig2 = p[2]
    p[0] = (("[]", rexp2), ("", orig2))
    if verbosity_level >= 3: print(p[0]) ##

def p_context_lcontext(p):
    'context : expression UNDERSCORE'
    rexp1, orig1 = p[1]
    p[0] = ((rexp1, "[]"), (orig1, ""))
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
         rexp1, orig1 = p[1]
         rexp3, orig3 = p[3]
         p[0] = ("[{} {} {}]".format(rexp1, p[2], rexp3),
                 "{} {} {}".format(orig1, p[2], orig3))

def p_expression2_or(p):
    '''expression2 : expression2 OR expression3
                   | expression2 MINUS expression3
                   | expression3'''
    if len(p) == 2:
         p[0] = p[1]
    else:
         rexp1, orig1 = p[1]
         rexp3, orig3 = p[3]
         p[0] = ("[{} {} {}]".format(rexp1, p[2], rexp3),
                 "{}{}{}".format(orig1, p[2], orig3))

def p_expression3_and(p):
    '''expression3 : expression3 AND expression4
                   | expression4'''
    if len(p) == 2:
         p[0] = p[1]
    else:
         rexp1, orig1 = p[1]
         rexp3, orig3 = p[3]
         p[0] = ("[{} {} {}]".format(rexp1, p[2], rexp3),
                 "{}{}{}".format(orig1, p[2], orig3))

def p_expression4_concat(p):
    '''expression4 : expression4 expression5 %prec CONCAT
                   | expression5'''
    if len(p) == 2:
         p[0] = p[1]
    else:
         rexp1, orig1 = p[1]
         rexp2, orig2 = p[2]
         p[0] = ("[{} {}]".format(rexp1, rexp2),
                 "{} {}".format(orig1, orig2))

def p_expression5_ignore(p):
    '''expression5 : SLASH expression6
                   | expression6'''
    if len(p) == 2:
         p[0] = p[1]
    else:
         rexp, orig = p[2]
         p[0] = ("[PI-[{}]]".format(rexp), "\\{}".format(orig))

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
         rexp, orig = p[1]
         p[0] = ("[{}{}]".format(rexp, p[2]),
                 "{}{}".format(orig, p[2]))

def p_expression7_group(p):
    '''expression7 : LBRACKET expression RBRACKET
                   | LPAREN expression RPAREN'''
    rexp, orig = p[2]
    p[0] = ("{}{}{}".format(p[1],rexp,p[3]), "{}{}{}".format(p[1],orig,p[3]))

def p_expression7_term(p):
    '''expression7 : BACKSLASH expression7
                   | DOLLAR expression7
                   | term'''
    if len(p) == 2:
         p[0] = p[1]
    elif p[1] == '\\':
         rexp, orig = p[2]
         p[0] = ("[PI-[{}]]".format(rexp),
                 "\\{}".format(orig))
    elif p[1] == '$':
         rexp, orig = p[2]
         p[0] = ("[{}[{}] & PI]".format(p[1], rexp),
                 "{}{}".format(p[1], orig))

def p_term_begin(p):
    '''term : BEGIN'''
    p[0] = ("BEGIN", "BEGIN")

def p_term_end(p):
    '''term : END'''
    p[0] = ("END", "END")

def p_term_single_symbol(p):
    '''term : SYMBOL'''
    global input_symbols, output_symbols
    m = re.match(r"^([{}a-zåäöA-ZÅÄÖØ]*)([:]?)([a-zåäöA-ZÅÄÖØ]*)$",
                 p[1])
    if not m:
        print_error(p, "Incorrectly formed token", p[1])
        raise SyntaxError
    ins, colo, outs = m.groups()
    inq = re.sub(r"([{}])", r"%\1", ins)
    outq = re.sub(r"([{}])", r"%\1", outs)
    if colo == ":":
        if ins == "" and outs == "":
            rexp = "PI"
        elif ins in input_symbols and outs in output_symbols:
            if (ins, outs) not in twex.symbol_pair_set:
                print_error(p, "Warning: invalid pair of valid input and output symbols", p[1])
            rexp = "{}:{}".format(inq, outq)
        elif ins == "" and outs in output_symbols:
            rexp = "[PI .o. {}]".format(outq)
        elif outs == "" and ins in input_symbols:
            rexp = "[{} .o. PI]".format(inq)
        else:
            rexp = inq
            print_error(p, "Warning: an undeclared symbol pair", p[1])
            ### raise SyntaxError
    elif colo == "":
        if ins in definitions and outs == "":
            rexp = "[{}]".format(ins)
        elif ins in input_symbols and ins in output_symbols:
            rexp = inq
        else:
            rexp = inq 
            print_error(p, "Warning: symbol not valid both for input and output", p[1])
            ### raise SyntaxError
    else:
        print_error(p, "Error: unrecognized symbol", p[1])
        ### raise SyntaxError
    p[0] = (rexp, p[1])

input_line = []

def print_error(p, explanation, sym):
    print(input_line)
    print(" "*(p.lexpos(0)-1), "*", explanation, sym)

def p_error(t):
    global parser, input_line
    if not t:
        # print('EOF') ##
        return
    print(input_line)
    print(" "*(t.lexpos-1), "*",
          "Syntax error at '{}' in line {}".format(t.value, t.lineno))

import ply.yacc as yacc

def parse_rule(line, debugging=False):
    global parser, input_line
    input_line = line.strip()
    result = parser.parse(input_line, debug=debugging, tracking=True)
    return(result)
    
def init(verbosity):
    global parser, verbosity_level, input_symbols, output_symbols
    for insym, outsym in twex.symbol_pair_set:
        input_symbols.add(insym)
        output_symbols.add(outsym)
    parser = yacc.yacc()
    verbosity_level = verbosity
    return(parser)

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

    init(args.verbosity)
    rule_file = open(args.rules, 'r')
    for line in rule_file:
        res = parse_rule(line, debugging=args.debug)
        print(res)
