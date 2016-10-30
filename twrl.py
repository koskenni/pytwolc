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
    alphabet = tuple(sorted(twex.symbol_pair_set | {('.#.', '.#.')}))

    XRC = hfst.XreCompiler()
    XRC.set_expand_definitions(True)
    PI_re = quote(" | ".join(sorted(pair_symbol_set | {'.#.'})))
    XRC.define_xre("PI", PI_re)
    twbt.ppdef(XRC, "PI")


def quote(str):
    """Protect '{' and '}' with a % in xerox regular expressions.

>>> quote('a {ij}:j [a:c | b]')
'a %{ij%}:j [a:c | b]'
"""
    return(re.sub(r"([{}])", r"%\1", str))

def fix_symbol(sym):
    """Augment pair symbols with respect to the global set of pairs.
"""
    global in_symbol_set, out_symbol_set
    if re.match(r"^([-\[\]|*+\\$ ])*$", sym) or sym == "":
        return(sym) # not a symbol
    elif sym in pair_symbol_set or sym in defined_symbols or sym == ".#.":
        return(sym) # a plain pairsymbol or a definition or .#.
    else:
        (insym, outsym) = label2pair(sym)
        if insym in {"?", ""} and outsym in {"?", ""}:
            return("PI")
        elif insym in {"?", ""}:
            if outsym not in out_symbol_set:
                print("Warning: ", outsym, "not in output alphabet")
            return("[PI .o. " + outsym + "]")
        elif outsym in {"?", ""}:
            if insym not in in_symbol_set:
                print("Warning: ", insym, "not in input alphabet")
            return("[" + insym + " .o. PI]")
        else:
            if insym not in in_symbol_set:
                print("Warning: ", insym, "not in input alphabet")
            if outsym not in out_symbol_set:
                print("Warning: ", outsym, "not in output alphabet")
            return("[" + insym + " .o. PI .o. " + outsym + "]")

def fix_symbols(rex):
    lst = re.split("([-\\[\\]|*+\\$ ]+)", rex)
    lst = [fix_symbol(item) for item in lst]
    rex = quote("".join(lst))
    return(rex)

defined_symbols = {'PI'}

def define(name, rex):
    global XRC        
    defined_symbols.add(name)
    # frex = fix_symbols(rex)
    frex = quote(rex)
    # print("frex = '{}'".format(frex)) ##
    XRC.define_xre(name, "PI & [{}]".format(frex))

def define_out_set(name, set):
    global XRC
    defined_symbols.add(name)
    rex = " | ".join(sorted(set))
    # frex = fix_symbols(rex)
    frex = quote(rex)
    # print("frex = '{}'".format(frex)) ##
    XRC.define_xre(name, "PI .o. [{}].l".format(frex))
    twbt.ppdef(XRC, name)

def define_in_set(name, set):
    global XRC
    defined_symbols.add(name)
    rex = " | ".join(sorted(set))
    # frex = fix_symbols(rex)
    frex = quote(rex)
    # print("frex = '{}'".format(frex)) ##
    # XRC.define_xre(name, "PI .o. [{}].u .o. PI".format(frex))
    XRC.define_xre(name, "[PI .o. [{}].l].u .o. PI".format(frex))
    twbt.ppdef(XRC, name)

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
    # print("Split using: ", "([-\\[\\]|*+\\\\$ ]+)") ##
    if str == "":
        return(XRC.compile("[]"))
    rex = fix_symbols(str)
    # print("Augmented regex string:", rex) ##
    F = XRC.compile(rex)
    F.minimize()
    F.set_name(str)
    # twbt.ppfst(F, True) ##
    return(F)

def rule_name(x, op, *contexts):
    return(x + " " +op + " " +
           " ;  ".join([lc + " _ " + rc for lc, rc in contexts]) +
           " ;")

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
    R = leftarrow(x, *ctx)
    RAR = rightarrow(x, *ctx)
    R.intersect(RAR)
    R.minimize()
    R.set_name(rule_name(x, "<=>", *ctx))
    twbt.ppfst(R, True) ##
    return(R)

if __name__ == "__main__":
    twex.read_examples()
    init()
    define_out_set("V", {'a', 'e', 'i', 'o', 'ä', 'ö'})
    define_in_set("C", {'h', 'l', 'n', 's', 't', 'v'})
    R1 = doublearrow("{ao}:o", ("[]", "{ij}:"))
    R2 = doublearrow("{ij}:j",("V :Ø*", ":Ø* V"))
    R3 = doublearrow("{tl}:l", ("[]", "V {ij}:i* C [C | :Ø* .#.]"))
