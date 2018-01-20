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
arpar.add_argument("-e", "--examples", help="name of the examples fst",
                   default="examples.fst")
arpar.add_argument("-r", "--rules", help="name of the rule file",
                   default="test.rules")
arpar.add_argument("-l", "--lost",
                    help="examples not accepted by all rules",
                    default="")
arpar.add_argument("-w", "--wrong",
                    help="wrong strings accepted by all rules",
                    default="")
arpar.add_argument("-t", "--thorough",
                   help="test each rule separately",
                   type=int, default=0)
arpar.add_argument("-v", "--verbosity",
                   help="level of  diagnostic output",
                   type=int, default=0)
arpar.add_argument("-d", "--debug",
                   help="level of PLY debugging output",
                   type=int, default=0)
args = arpar.parse_args()

print('Reading examples from:', args.examples)
twex.read_fst(args.examples)

EXAMP_FSA = twbt.fst_to_fsa(twex.EXAMPLES)
EXAMP_IN = twex.EXAMPLES.copy()
EXAMP_IN.input_project()

twrl.init(args.verbosity)

plytw.init(args.verbosity)

if args.lost or args.wrong:
    ALLR = []
rule_file = open(args.rules, 'r')
for line in rule_file:
    line = line.strip()
    if line == "STOP":
        break
    if line == "" or line[0] == '!':
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
    if args.thorough > 0:
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
    if args.lost or args.wrong:
        ALLR.append(R)
    if args.thorough > 0:
        SEL.intersect(twex.EXAMPLES)
        # SEL.n_best(5)
        SEL.minimize()
        if args.verbosity > 1:
            paths = SEL.extract_paths(output='raw')
            print_raw_paths(paths[0:20])
        TEST = SEL.copy()
        TEST.intersect(R)
        if args.thorough > 0:
            if TEST.compare(SEL):
                print("All positive examples accepted")
            else:
                DIFF = SEL.copy()
                DIFF.minus(TEST)
                DIFF.minimize()
                print("** Some positive examples were rejected:")
                paths = DIFF.extract_paths(output='raw')
                print_raw_paths(paths)
    if args.thorough > 1:
        NEGe = EXAMP_FSA.copy()
        NEGe.compose(MIXe)
        NEGe.output_project()
        NEG = twbt.fsa_to_fst(NEGe)
        NEG.minus(twex.EXAMPLES)
        NG = EXAMP_IN.copy()
        NG.compose(NEG)
        npaths = NG.extract_paths(output='raw')
        print_raw_paths(npaths)
        TEST = NG.copy()
        TEST.intersect(R)
        if args.verbosity > 0:
            if TEST.compare(hfst.empty_fst()):
                print("All negative examples rejected")
            else:
                print("Some negative examples accepted:")
                npaths = TEST.extract_paths(output='raw')
                print_raw_paths(npaths)

if args.lost or args.wrong:
    RESU = EXAMP_IN.copy()
    print(RESU.number_of_arcs(), "arcs in RESU")
    RESU.compose_intersect(tuple(ALLR))
    RESU.minimize()
if args.lost:
    LOST = twex.EXAMPLES.copy()
    LOST.minus(RESU)
    LOST.minimize()
    lost_stream = hfst.HfstOutputStream(filename=args.lost)
    lost_stream.write(LOST)
    lost_stream.flush()
    lost_stream.close()
    print("wrote lost examples to", args.lost)
if args.wrong:
    WRONG = RESU.copy()
    WRONG.subtract(twex.EXAMPLES)
    WRONG.minimize()
    wrong_stream = hfst.HfstOutputStream(filename=args.wrong)
    wrong_stream.write(WRONG)
    wrong_stream.flush()
    wrong_stream.close()
    print("wrote wrongly accepted examples to", args.wrong)
