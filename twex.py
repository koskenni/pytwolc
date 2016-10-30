"""A module for reading two-level examples

The examples are assumed to be as space-separated one-level
representation and they are compiled into a single automaton. 
At the same time, the alphabet used in the examples is 
collected in several forms.

    EXAMPLES_FST -- the transducer which accepts exactly the examples

    symbol_pair_set -- a tuple of string pairs suitable for
        e.g. hfst.rules.restriction

"""
import hfst, re, twbt

def label2pair(label):
    m = re.match(r"^([^:]*):([^:]*)$", label)
    if m:
        return(m.group(1), m.group(2))
    else:
        return(label, label)

symbol_pair_set = set()
EXAMPLES_FST = hfst.HfstTransducer()

def read_examples(filename="test.pairstr"):
    """Reads the examples from the file whose name is 'filename'.

Use help(twex) in order to get more information.
"""
    global symbol_pair_set, EXAMPLES_FST
    EXAMPLES_FST.set_name(filename)
    exfile = open(filename,"r")
    for line in exfile:
        lst = re.split(" +", line.strip())
        line_tok = [label2pair(label) for label in lst ]
        # print(line_tok) ##
        line_fst = hfst.tokenized_fst(line_tok)
        # twbt.printfst(line_fst, True) ##
        EXAMPLES_FST.disjunct(line_fst)
        for insym, outsym in line_tok:
            # print(insym, outsym, end="") ##
            symbol_pair_set.add((insym, outsym))
    exfile.close()
    #print("List of alphabet symbols:", sorted(symbol_pair_set)) ##

    EXAMPLES_FST.minimize()
    # twbt.printfst(EXAMPLES_FST, False) ##


if __name__ == "__main__":
    read_examples()
    print("symbol_pair_set =", symbol_pair_set)
