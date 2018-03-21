import sys, re, hfst
import twbt, twex, twrl

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

import argparse

arpar = argparse.ArgumentParser("python3 twolcomp.py")
arpar.add_argument("-e", "--examples", help="name of the examples fst",
                   default="examples.fst")
arpar.add_argument("-r", "--rules", help="name of the rule file",
                   default="test.rules")
arpar.add_argument("-l", "--lost",
                    help="file to which write the examples not accepted by all rules",
                    default="")
arpar.add_argument("-w", "--wrong",
                    help="file to which write the wrong strings accepted by all rules as a fst",
                    default="")
arpar.add_argument("-t", "--thorough",
                   help="test each rule separately, values: 0, 1 or 2",
                   type=int, default=0)
arpar.add_argument("-v", "--verbosity",
                   help="level of  diagnostic output",
                   type=int, default=0)
arpar.add_argument("-d", "--debug",
                   help="level of PLY debugging output",
                   type=int, default=0)
arpar.add_argument("-p", "--parser",
                    help="which parser to use: ply or tatsu", default="ply")
args = arpar.parse_args()

print('Reading examples from:', args.examples)
twex.read_fst(args.examples)

examples_fsa = twex.EXAMPLES.copy()
examples_fsa = hfst.fst_to_fsa(examples_fsa, separator="^")

examples_up_fsa = twex.EXAMPLES.copy()
examples_up_fsa.input_project()

twrl.init(args.verbosity)

if args.parser == "ply":
    import plytw
    plytw.init(args.verbosity)
elif args.parser == "tatsu":
    import twolcsyntax
    twolcsyntax.init()
else:
    print("--parser must be either 'tatsu' or 'ply', not", args.parser)

if args.lost or args.wrong:
    all_rules_fst_lst = []
rule_file = open(args.rules, 'r')
for line in rule_file:
    line = line.strip()
    if line == "STOP":
        break
    if line == "" or line[0] == '!':
        continue
    if args.parser == "ply":
        result = plytw.parse_rule(line)
    elif args.parser == "tatsu":
        result = twolcsyntax.parse_rule(line)
    if not result:
        print("ERROR:", line)
        continue
    op = result[0]
    if op == "=":
        op, id, expr, title = result
        print(title)
        twrl.define(id, expr)
        continue
    op, x_expr, ctx_expr_list, title = result
    if args.thorough > 0:
        print("\n--------------------\n")
    print(title)
    #print(result) ##
    if op == "=>":
        R, SEL, MIXe = twrl.rightarrow(title, x_expr, *ctx_expr_list)
    elif op == "<=":
        R, SEL, MIXe = twrl.leftarrow(title, x_expr, *ctx_expr_list)
    elif op == "<=>":
        R, SEL, MIXe = twrl.doublearrow(title, x_expr, *ctx_expr_list)
    elif op == "/<=":
        R, SEL, MIXe = twrl.center_exclusion(title, x_expr, *ctx_expr_list)
    else:
        print("Error: not a valid type of a rule", op)
        continue
    if args.lost or args.wrong:
        all_rules_fst_lst.append(R)
    if args.thorough > 0:
        SEL.intersect(twex.EXAMPLES)
        # SEL.n_best(5)
        SEL.minimize()
        if args.verbosity > 1:
            paths = SEL.extract_paths(output='raw')
            print_raw_paths(paths[0:20])
        passed_pos_examples_fst = SEL.copy()
        passed_pos_examples_fst.intersect(R)
        if args.thorough > 0:
            if passed_pos_examples_fst.compare(SEL):
                print("All positive examples accepted")
            else:
                lost_examples_fst = SEL.copy()
                lost_examples_fst.minus(passed_pos_examples_fst)
                lost_examples_fst.minimize()
                print("** Some positive examples were rejected:")
                lost_paths = lost_examples_fst.extract_paths(output='raw')
                print_raw_paths(lost_paths)
    if args.thorough > 1:
        neg_examples_fsa = examples_fsa.copy()
        neg_examples_fsa.compose(MIXe)
        neg_examples_fsa.output_project()
        neg_examples_fst = hfst.fsa_to_fst(neg_examples_fsa, separator="^")
        neg_examples_fst.minus(twex.EXAMPLES)
        NG = examples_up_fsa.copy()
        NG.compose(neg_examples_fst)
        npaths = NG.extract_paths(output='raw')
        print_raw_paths(npaths)
        passed_neg_examples_fst = NG.copy()
        passed_neg_examples_fst.intersect(R)
        if args.verbosity > 0:
            if passed_neg_examples_fst.compare(hfst.empty_fst()):
                print("All negative examples rejected")
            else:
                print("Some negative examples accepted:")
                npaths = passed_neg_examples_fst.extract_paths(output='raw')
                print_raw_paths(npaths)

if args.lost or args.wrong:
    RESU = examples_up_fsa.copy()
    print(RESU.number_of_arcs(), "arcs in RESU")
    RESU.compose_intersect(tuple(all_rules_fst_lst))
    RESU.minimize()
if args.lost:
    lost_positive_examples_fst = twex.EXAMPLES.copy()
    lost_positive_examples_fst.minus(RESU)
    lost_positive_examples_fst.minimize()
    lost_stream = hfst.HfstOutputStream(filename=args.lost)
    lost_stream.write(lost_positive_examples_fst)
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
