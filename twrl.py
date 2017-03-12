"""Module for building two-level rule components and rules.
"""
import re, hfst
import twbt, twex
from twex import label2pair

XRC = hfst.XreCompiler()

verboxity_level = 0

def init(verbosity):
    global in_symbol_set, out_symbol_set, pair_symbol_set
    global XRC, verbosity_level
    global PISTAR, PISTAR_FSA, diamond, DIAMOND
    global PRE, POST
    verbosity_level = verbosity
    in_symbol_set = set() # The set of all input symbols used in the examples
    out_symbol_set = set()
    pair_symbol_set = set()
    for insym, outsym in twex.symbol_pair_set:
        in_symbol_set.add(insym)
        out_symbol_set.add(outsym)
        pair_symbol_set.add(insym if insym == outsym
                            else insym + ':' + outsym)
    if not XRC:
        print('*** not XRC - why? ***') ##
        XRC = hfst.XreCompiler()
    XRC.set_expand_definitions(True)
    PI_re = quote(" | ".join(sorted(pair_symbol_set)))
    XRC.define_xre("PI", PI_re)
    if verbosity_level >= 1:
        twbt.ppdef(XRC, "PI", PI_re) ##
    diamond = 'DIAMOND'
    DIAMOND = hfst.regex(diamond)
    PISTAR = XRC.compile("PI*")
    PISTAR_FSA = twbt.fst_to_fsa(PISTAR)
    PRE =  XRC.compile("[[ZERO .x. [PI].u]* ZERO:BEGIN]* [[PI].u]* [ZERO:END [ZERO .x. [PI].u]*]*")
    POST = XRC.compile("[[[PI].l .x. ZERO]* BEGIN:ZERO]* [[PI].l]* [END:ZERO [[PI].l .x. ZERO]*]*")
    # twbt.ppfst(PRE, True) ##
    return

def begin_end(FST):
    global PRE, POST
    RES = PRE.copy()
    RES.compose(FST)
    # twbt.ppfst(RES, True) ##
    RES.compose(POST)
    # twbt.ppfst(RES, True) ##
    RES.substitute('ZERO', "@_EPSILON_SYMBOL_@")
    RES.minimize()
    # twbt.ppfst(RES, True) ##
    return(RES)


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
    return

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
    # twbt.ppfst(FST, True) ##
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
    CTX.minimize()
    CTX1 = begin_end(CTX)
    CTX1.concatenate(DIAMOND)
    CTX1.concatenate(PISTAR)
    CTX1.concatenate(DIAMOND)
    RC = e(rightc)
    RC.concatenate(PISTAR)
    RC.minimize()
    CTX2 = begin_end(RC)
    CTX1.concatenate(CTX2)
    CTX1.minimize()
    return(CTX1)

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

def mix(x):
    X1 = e("[[" + x + "].u .o. PI+]")
    X1.minimize()
    Xe = twbt.fst_to_fsa(X1)
    # twbt.ppfst(Xe, True) ##
    return Xe

def correct_to_incorrect(x, X):
    global PISTAR, PISTAR_FSA
    X1 = twbt.fst_to_fsa(X)
    Xe = mix(x)
    X1.cross_product(Xe)
    # twbt.ppfst(X1, True) ##
    MIXe = PISTAR_FSA.copy()
    MIXe.concatenate(X1)
    MIXe.concatenate(PISTAR_FSA)
    MIXe.minimize()
    MIXe.set_name("Correct to incorrect ")
    SEL = e("[PI* [[[" + x + "].u .o. [PI*]] - [" + x + "]] PI*]")
    SEL.set_name("Select other than " + x)
    return SEL, MIXe

def incorrect_to_correct(x, X):
    global PISTAR, PISTAR_FSA
    X1 = twbt.fst_to_fsa(X)
    X2 = mix(x)
    X2.cross_product(X1)
    MIXe = PISTAR_FSA.copy()
    MIXe.concatenate(X2)
    MIXe.concatenate(PISTAR_FSA)
    MIXe.minimize()
    MIXe.set_name("Incorrect to correct ")
    SEL = e("[PI* [" + x + "] PI*]")
    SEL.set_name("Select " + x)
    return SEL, MIXe

def rightarrow(name, x, *contexts):
    X = e(x)
    PRECOND = x_to_condition(X)
    POSTCOND = contexts_to_condition(*contexts)
    RULE = generalized_restriction(PRECOND, POSTCOND)
    RULE.set_name(name)
    # twbt.ppfst(RULE, True) ##
    SEL, MIXe = incorrect_to_correct(x, X)
    # twbt.ppfst(MIXe, True) ##
    return RULE, SEL, MIXe

def leftarrow(name, x, *contexts):
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
    RULE.set_name(name)
    # twbt.ppfst(RULE, True) ##
    SEL, MIXe = correct_to_incorrect(x, X)
    return RULE, SEL, MIXe

def doublearrow(name, x, *contexts):
    RULE, SEL, MIXe = rightarrow(name, x, *contexts)
    R2, S2, M2 = leftarrow(name, x, *contexts)
    RULE.intersect(R2)
    RULE.minimize()
    RULE.set_name(name)
    MIXe.disjunct(M2)
    MIXe.minimize()
    SEL.disjunct(S2)
    SEL.minimize()
    # twbt.ppfst(RULE, True) ##
    return RULE, SEL, MIXe

def center_exclusion(name, x, *contexts):
    CC = contexts_to_condition(*contexts)
    X = e(x)
    XX = x_to_condition(X)
    CC.intersect(XX)
    NULL = hfst.HfstTransducer()
    RULE = generalized_restriction(CC, NULL)
    RULE.set_name(name)
    # twbt.ppfst(RULE, True) ##
    SEL = e("[PI* [" + x + "] PI*]")
    MIXe = hfst.empty_fst()
    return RULE, SEL, MIXe

if __name__ == "__main__":
    twex.read_examples()
    init(1)
    define("V", "PI .o.[a|e|i|o|ä|ö]")
    define("C", "[PI .o. [h|l|n|s|t|v]] | %{ij%}:j")
    R1 = doublearrow("{ao}:o <=> _ {ij}:",
                     "%{ao%}:o",
                     ("[]", "[%{ij%} .o. PI]"))
    twbt.ppfst(R1, True)
    R2 = doublearrow("{ij}:j <=> V :Ø* _ :Ø* V",
                     "%{ij%}:j",
                     ("V [PI .o. Ø]*", "[PI .o. Ø]* V"))
    twbt.ppfst(R2, True)
    R3 = doublearrow("{tl}:l <=> _ CLOSED",
                     "%{tl%}:l",
                     ("[]", "V %{ij%}:i* C [C | [PI .o. Ø]* END]"))
    twbt.ppfst(R3, True)
