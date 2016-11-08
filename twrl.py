"""Module for building two-level rule components and rules.
"""
import re, hfst
import twbt, twex
from twex import label2pair


def init():
    global in_symbol_set, out_symbol_set, pair_symbol_set, XRC, alphabet
    in_symbol_set = set() # The set of all input symbols used in the examples
    out_symbol_set = set()
    pair_symbol_set = set()
    for insym, outsym in twex.symbol_pair_set:
        in_symbol_set.add(insym)
        out_symbol_set.add(outsym)
        pair_symbol_set.add(insym if insym == outsym
                            else insym + ':' + outsym)
    alphabet = tuple(sorted(twex.symbol_pair_set | {('§', '§')}))

    XRC = hfst.XreCompiler()
    XRC.set_expand_definitions(True)
    PI_re = quote(" | ".join(sorted(pair_symbol_set | {'§'})))
    XRC.define_xre("PI", PI_re)
    # twbt.ppdef(XRC, "PI")


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
corresponding to the expression.  In particular, certain
wild-card pair symbols are expanded so that they represent 
only pairs in the global set of pairs (so called PI).
"""
    global XRC
    # print("Regex string:", str) ##
    if str == "":
        return(XRC.compile("[]"))
    F = XRC.compile(str)
    F.minimize()
    F.set_name(str)
    # twbt.ppfst(F, True) ##
    return(F)

def rule_name(x, op, *contexts):
    return(x + " " +op + " " +
           " ; ".join([lc + " _ " + rc for lc, rc in contexts]))

def rightarrow(x, *ctx):
    ctx_tuple = tuple([(e(l),e(r)) for (l,r) in ctx])
    R = hfst.rules.restriction(ctx_tuple, e(x), alphabet)
    R.minimize()
    R.set_name(rule_name(x, "=>", *ctx))
    # twbt.ppfst(R, True) ##
    return(R)

def leftarrow(x, *ctx):
    ctx_tuple = tuple([(e(l),e(r)) for (l,r) in ctx])
    R = hfst.rules.surface_coercion(ctx_tuple, e(x), alphabet)
    R.set_name(rule_name(x, "<=", *ctx))
    R.minimize()
    # twbt.ppfst(R, True) ##
    return(R)

def doublearrow(x, *ctx):
    # print(x, *ctx) ##
    R = leftarrow(x, *ctx)
    RAR = rightarrow(x, *ctx)
    R.intersect(RAR)
    R.minimize()
    R.set_name(rule_name(x, "<=>", *ctx))
    # twbt.ppfst(R, True) ##
    return(R)

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
