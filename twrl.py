"""Module for building two-level rule components and rules.
"""
import re, hfst
import twbt

import twex
from twex import label2pair, alpha_in, alpha_out
if __name__ == "__main__":
    twex.read_examples()

def quote(str):
    """Protect '{' and '}' with a % in xerox regular expressions.

>>> quote('a {ij}:j [a:c | b]')
'a %{ij%}:j [a:c | b]'
"""
    return(re.sub(r"([{}])", r"%\1", str))

def fix_symbol(sym):
    """Augment pair symbols with respect to the global set of pairs.
"""
    if re.match(r"^([-\[\]|*+\\$ ])*$", sym) or sym == "":
        return(sym) # not a symbol
    elif sym in twex.alpha_labels or sym in defined_symbols or sym == "END":
        return(sym) # a plain symbol or a definition or .#.
    else:
        (insym, outsym) = label2pair(sym)
        if insym in {"?", ""} and outsym in {"?", ""}:
            return("PI")
        elif insym in {"?", ""}:
            if outsym not in alpha_out:
                print("Warning: ", outsym, "not in output alphabet")
            return("[PI .o. " + outsym + "]")
        elif outsym in {"?", ""}:
            if insym not in alpha_in:
                print("Warning: ", insym, "not in input alphabet")
            return("[" + insym + " .o. PI]")
        else:
            if insym not in alpha_in:
                print("Warning: ", insym, "not in input alphabet")
            if outsym not in alpha_out:
                print("Warning: ", outsym, "not in output alphabet")
            return("[" + insym + " .o. PI .o. " + outsym + "]")

def fix_symbols(rex):
    lst = re.split("([-\\[\\]|*+\\$ ]+)", rex)
    lst = [fix_symbol(item) for item in lst]
    rex = quote("".join(lst))
    return(rex)

        
XRC = hfst.XreCompiler()
XRC.set_expand_definitions(True)
PI_re = quote(" | ".join(sorted(twex.alpha_labels)))
XRC.define_xre("PI", PI_re)

defined_symbols = {'PI'}

def define(name, rex):
    defined_symbols.add(name)
    frex = fix_symbols(rex)
    print("frex = '{}'".format(frex)) ##
    XRC.define_xre(name, "PI & [{}]".format(frex))

def define_out_set(name, set):
    defined_symbols.add(name)
    rex = " | ".join(sorted(set))
    frex = fix_symbols(rex)
    print("frex = '{}'".format(frex)) ##
    XRC.define_xre(name, "PI .o. [{}]".format(frex))


# XRC.define_xre("V", "[PI .o. [a|e|i|o|ä]]")
# XRC.define_xre("C", "[PI .o. [h|l|n|t|s|v]].u .o. PI")
# twbt.printfst(XRC.compile("C"), True) ##

def e(str):
    """Convert a two-level component expression into a FST.

str -- a string containing a (two-level) regular expression

Returns a HfstTransducer which performs the mapping 
corresponding to the expression.  In particular, certain
wild-card pair symbols are expanded so that they represent 
only pairs in the global set of pairs (so called PI).
"""
    # print("Regex string:", str) ##
    # print("Split using: ", "([-\\[\\]|*+\\\\$ ]+)") ##
    if str == "":
        return(XRC.compile("[]"))
    rex = fix_symbols(str)
    # print("Augmented regex string:", rex) ##
    F = XRC.compile(rex)
    F.minimize()
    F.set_name(str)
    # twbt.printfst(F, True) ##
    return(F)

def rule_name(x, op, *contexts):
    return(x + " " +op + " " +
           " ;  ".join([lc + " _ " + rc for lc, rc in contexts]) +
           " ;")

def rightarrow(x, *ctx):
    ctx_tuple = tuple([(e(l),e(r)) for (l,r) in ctx])
    R = hfst.rules.restriction(ctx_tuple, e(x), twex.alphabet)
    R.minimize()
    R.set_name(rule_name(x, "=>", *ctx))
    # twbt.printfst(R, True) ##
    return(R)

def leftarrow(x, *ctx):
    ctx_tuple = tuple([(e(l),e(r)) for (l,r) in ctx])
    R = hfst.rules.surface_coercion(ctx_tuple, e(x), twex.alphabet)
    R.set_name(rule_name(x, "<=", *ctx))
    R.minimize()
    # twbt.printfst(R, True) ##
    return(R)

def doublearrow(x, *ctx):
    R = leftarrow(x, *ctx)
    RAR = rightarrow(x, *ctx)
    R.intersect(RAR)
    R.minimize()
    R.set_name(rule_name(x, "<=>", *ctx))
    twbt.printfst(R, True) ##
    return(R)

if __name__ == "__main__":
    # print("sorted alpha_labels", " | ".join(sorted(twex.alpha_labels)))
    # print("PI_re", PI_re) ##
    # twbt.printfst(XRC.compile("PI"), True) ##
    define_out_set("V", {'a', 'e', 'i', 'ä'})
    twbt.printfst(XRC.compile("V*"), True) ##
    R1 = doublearrow("{ao}:o", ("[]", "{ij}:"))
    R2 = doublearrow("{ij}:j",("V :Ø*", ":Ø* V"))
