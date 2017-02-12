"""Module for building two-level rule components and rules.
"""
import re, hfst
import twbt, twex
from twex import label2pair

XRC = hfst.XreCompiler()

verboxity_level = 0

def init(verbosity):
    global in_symbol_set, out_symbol_set, pair_symbol_set
    global XRC, alphabet, verbosity_level
    global PISTAR, diamond, DIAMOND
    verbosity_level = verbosity
    in_symbol_set = set() # The set of all input symbols used in the examples
    out_symbol_set = set()
    pair_symbol_set = set()
    for insym, outsym in twex.symbol_pair_set:
        in_symbol_set.add(insym)
        out_symbol_set.add(outsym)
        pair_symbol_set.add(insym if insym == outsym
                            else insym + ':' + outsym)
    alphabet = tuple(sorted(twex.symbol_pair_set | {('§', '§')}))
    if not XRC:
        print('*** not XRC - why? ***') ##
        XRC = hfst.XreCompiler()
    XRC.set_expand_definitions(True)
    PI_re = quote(" | ".join(sorted(pair_symbol_set | {'§'})))
    XRC.define_xre("PI", PI_re)
    if verbosity_level >= 1:
        twbt.ppdef(XRC, "PI", PI_re) ##
    diamond = '¤'
    DIAMOND = hfst.regex(diamond)
    PISTAR = XRC.compile("PI*")    
    return


def quote(str):
    """Protect '{' and '}' with a % in xerox regular expressions.

>>> quote('a {ij}:j [a:c | b]')
'a %{ij%}:j [a:c | b]'
"""
    return(re.sub(r"([{}])", r"%\1", str))

defined_symbols = {'PI'}

def define(name, rex):
    global XRC        
    defined_symbols.add(name)
    XRC.define_xre(name, rex)

def e(str):
    """Convert a two-level component expression into a FST.

str -- a string containing a (two-level) regular expression

Returns a HfstTransducer which performs the mapping 
corresponding to the expression. 
"""
    global XRC, verbosity_level
    # print("Regex string:", str) ##
    if str == "":
        return(XRC.compile("[]"))
    F = XRC.compile(str)
    F.minimize()
    F.set_name(str)
    if verbosity_level >= 5:
        twbt.ppfst(F, True) ##
    return(F)

def rule_name(x, op, *contexts):
    return(x + " " +op + " " +
           " ; ".join([lc + " _ " + rc for lc, rc in contexts]))

def generalized_restriction(PRECONDITION, POSTCONDITION):
    global PISTAR, diamond
    WW = hfst.HfstTransducer(PRECONDITION)
    WW.subtract(POSTCONDITION)
    WW.minimize()
    WW.set_name("PRECOND-POSTCOND")
    # twbt.ppfst(WW, True) ##
    WW.substitute(diamond, "@_EPSILON_SYMBOL_@")
    # WW.substitute(diamond, "@0@")
    # print(WW.get_properties().items()) ##
    WW.minimize()
    WW.set_name("Diamonds removed")
    # twbt.ppfst(WW, True) ##
    FST = hfst.HfstTransducer(PISTAR)
    FST.minus(WW)
    FST.minimize()
    FST.set_name("Doubly negated")
    # twbt.ppfst(FST, True) ##
    return(FST)

def x_to_condition(X):
    global PISTAR, DIAMOND
    RES = hfst.HfstTransducer(PISTAR)
    RES.concatenate(DIAMOND)
    RES.concatenate(X)
    RES.concatenate(DIAMOND)
    RES.concatenate(PISTAR)
    RES.minimize()
    RES.set_name("PISTAR ¤ X ¤ PISTAR")
    # twbt.ppfst(RES, True) ##
    return(RES)

def context_to_condition(leftc, rightc):
    global PISTAR, DIAMOND
    CTX = hfst.HfstTransducer(PISTAR)
    LC = e(leftc)
    CTX.concatenate(LC)
    CTX.concatenate(DIAMOND)
    CTX.concatenate(PISTAR)
    CTX.concatenate(DIAMOND)
    RC = e(rightc)
    CTX.concatenate(RC)
    CTX.concatenate(PISTAR)
    CTX.minimize()
    return(CTX)

def contexts_to_condition(*contexts):
    global PISTAR
    RES = hfst.HfstTransducer()
    for leftc, rightc in contexts:
        CTX = context_to_condition(leftc, rightc)
        # twbt.ppfst(CTX, True) ##
        RES.disjunct(CTX)
        RES.minimize()
        RES.set_name(leftc + '_' + rightc)
        # twbt.ppfst(RES, True) ##
    return(RES)

def rightarrow(x, *contexts):
    X = e(x)
    PRECOND = x_to_condition(X)
    POSTCOND = contexts_to_condition(*contexts)
    RULE = generalized_restriction(PRECOND, POSTCOND)
    RULE.set_name(rule_name(x, '=>', *contexts))
    # twbt.ppfst(RULE, True) ##
    return RULE

def leftarrow(x, *contexts):
    global PISTAR
    X = e(x)
    POSTCOND = x_to_condition(X)
    XALL = e(x)
    XALL.input_project()
    XALL.compose(PISTAR)
    PRECOND = x_to_condition(XALL)
    CC = contexts_to_condition(*contexts)
    PRECOND.intersect(CC)
    RULE = generalized_restriction(PRECOND, POSTCOND)
    RULE.set_name(rule_name(x, '<=', *contexts))
    # twbt.ppfst(RULE, True) ##
    return RULE

def doublearrow(x, *contexts):
    RULE = rightarrow(x, *contexts)
    R2 = leftarrow(x, *contexts)
    RULE.intersect(R2)
    RULE.set_name(rule_name(x, '<=>', *contexts))
    # twbt.ppfst(RULE, True) ##
    return RULE

def center_exclusion(x, *contexts):
    CC = contexts_to_condition(*contexts)
    X = e(x)
    XX = x_to_condition(X)
    CC.intersect(XX)
    NULL = hfst.HfstTransducer()
    RULE = generalized_restriction(CC, NULL)
    RULE.set_name(rule_name(x, '/<=', *contexts))
    # twbt.ppfst(RULE, True) ##
    return(RULE)

if __name__ == "__main__":
    twex.read_examples()
    init()
    define("V", "PI .o.[a|e|i|o|ä|ö]")
    define("C", "[PI .o. [h|l|n|s|t|v]] | %{ij%}:j")
    R1 = doublearrow("%{ao%}:o", ("[]", "[%{ij%} .o. PI]"))
    twbt.ppfst(R1, True)
    R2 = doublearrow("%{ij%}:j",("V [PI .o. Ø]*", "[PI .o. Ø]* V"))
    twbt.ppfst(R2, True)
    R3 = doublearrow("%{tl%}:l", ("[]", "V %{ij%}:i* C [C | [PI .o. Ø]* §]"))
    twbt.ppfst(R3, True)
