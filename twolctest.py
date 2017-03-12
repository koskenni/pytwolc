import sys, re, hfst
import twbt, twex, twrl, plytw
import argparse

def apply_rule(psymlist, dicrule):
    # print(rule_name) ##
    state = 0
    state_seq = []
    final, dtrans = drule[state]
    for psym in psymlist:
        if psym in dtrans:
            state = dtrans[psym]
            final, dtrans = drule[state]
            state_seq.append("{} -> {}{}".
                             format(psym, state,(':' if final else '.')))
        else:
            state_seq.append("{} -> ??".
                             format(psym))

            return(False, state_seq)
    if not final:
        return(False, state_seq)
    else:
        return(True, state_seq)

def clean_comb_sym(sym):
    insym, outsym = sym.split('^')
    if insym == outsym:
        return insym
    else:
        return insym + ':' + outsym

def print_raw_paths(paths):
    for path in paths:
        weight, sym_pairs = path
        sym_list = [(insym if insym == outsym else insym + ":" + outsym)
                    for insym, outsym in sym_pairs]
        print(' '.join(sym_list))
    return

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

twex.read_examples(filename=args.examples)
print("--- all examples read from ", args.examples ," ---")
EXAMP_FSA = twbt.fst_to_fsa(twex.EXAMPLES)
EXAMP_IN = twex.EXAMPLES.copy()
EXAMP_IN.input_project()

twrl.init(args.verbosity)

plytw.init(args.verbosity)

rule_file = open(args.rules, 'r')
for line in rule_file:
    line = line.strip()
    if line[0] == '!' or line == "":
        continue
    result = plytw.parse_rule(line)
    if not result:
        print("ERROR")
        continue
    op = result[0]
    # print(result) ##
    if op == "=":
        op, id, expr, clean = result
        print(clean)
        twrl.define(id, expr)
        continue
    op, x_expr, ctx_expr_list, clean = result
    print("\n--------------------\n")
    print(clean)
    if op == "=>":
        R, SEL, MIXe = twrl.rightarrow(clean, x_expr, *ctx_expr_list)
    elif op == "<=":
        R, SEL, MIXe = twrl.leftarrow(clean, x_expr, *ctx_expr_list)
    elif op == "<=>":
        R, SEL, MIXe = twrl.doublearrow(clean, x_expr, *ctx_expr_list)
    elif op == "/<=":
        R, SEL, MIXe = twrl.center_exclusion(clean, x_expr, *ctx_expr_list)
    else:
        print("Error: not a valid type of a rule", op)
        continue
    print("\nPositive examples")
    twbt.ppfst(R) ##
    # twbt.ppfst(SEL, True) ##
    SEL.intersect(twex.EXAMPLES)
    # twbt.ppfst(SEL, True) ##
    # SEL.n_best(5)
    # twbt.ppfst(SEL, True) ##
    SEL.minimize()
    # twbt.ppfst(SEL, True) ##
    if args.verbosity > 0:
        paths = SEL.extract_paths(output='raw')
        print_raw_paths(paths[0:20])
    TEST = SEL.copy()
    TEST.intersect(R)
    if TEST.compare(SEL):
        print("All positive examples accepted")
    else:
        DIFF = SEL.copy()
        DIFF.minus(TEST)
        DIFF.minimize()
        print("** Rejected positive examples:")
        paths = DIFF.extract_paths(output='raw')
        print_raw_paths(paths)

    print("\nNegative examples")
    # twbt.ppfst(MIXe) ##
    NEGe = EXAMP_FSA.copy()
    NEGe.compose(MIXe)
    NEGe.output_project()
    # twbt.ppfst(NEGe, True) ##
    NEG = twbt.fsa_to_fst(NEGe)
    # twbt.ppfst(NEG) ##
    NEG.minus(twex.EXAMPLES)
    NG = EXAMP_IN.copy()
    NG.compose(NEG)
    # twbt.ppfst(NG) ##
    if args.verbosity > 0:
        npaths = NG.extract_paths(output='raw')
        print_raw_paths(npaths)
    TEST = NG.copy()
    TEST.intersect(R)
    if TEST.compare(hfst.empty_fst()):
        print("All negative examples rejected")
    else:
        print("Some negative examples accepted:")
        npaths = TEST.extract_paths(output='raw')
        print_raw_paths(npaths)
    
