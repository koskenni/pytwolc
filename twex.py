""" 
A module for reading two-level examples

The examples are assumed to be as space-separated one-level
representation and they are compiled into a single automaton. 
At the same time, the alphabet used in the examples is 
collected in several forms.

  all_ex_fst --   the transducer which accepts exactly the
                  examples
  alphabet --     a tuple of string pairs suitable for
                  e.g. hfst.rules.restriction
  alpha_in --     a set containing all input symbols occurring
                  in the examples
  alpha_out --    a set containing all output symbole occurring
                  in the examples
  alpha_labels -- a set of label strings, e.g. 'a', '{ij}:i'
"""
import hfst, re, twbt

def label2pair(label):
    m = re.match(r"^([^:]*):([^:]*)$", label)
    if m:
        return(m.group(1), m.group(2))
    else:
        return(label, label)

alpha_pairs = {('END','END')}
all_ex_fst = hfst.HfstTransducer()
alpha_in = set() # The set of all input symbols used in the examples
alpha_out = set()
alpha_labels = set()
alphabet = None

def read_examples(filename="test.pairstr"):
    """Reads the examples from the file whose name is 'filename'.

Use help(twex) in order to get more information.
"""
    global alphabet
    exfile = open(filename,"r")
    # line_list = []
    for line in exfile:
        lst = re.split(" +", line.strip())
        # line_list.append(l)
        line_tok = [label2pair(label) for label in lst ]
        # print(line_tok) ##
        line_fst = hfst.tokenized_fst(line_tok)
        # twbt.printfst(line_fst, True) ##
        all_ex_fst.disjunct(line_fst)
        for insym, outsym in line_tok:
            # print(insym, outsym, end="") ##
            alpha_pairs.add((insym, outsym))
    exfile.close()
    #print("List of alphabet symbols:", sorted(alpha_pairs)) ##
    #all_ex_fst = hfst.regex(twolctest.quote("|".join(line_list)))

    all_ex_fst.minimize()
    # twbt.printfst(all_ex_fst, False) ##

    for insym, outsym in alpha_pairs:
        alpha_in.add(insym)
        alpha_out.add(outsym)
        alpha_labels.add(insym if insym == outsym else insym + ':' + outsym)

    alpha_pair_list = sorted([pair for pair in alpha_pairs])
    alphabet = tuple(alpha_pair_list)
    alpha_label_list = list(sorted(alpha_labels))
    # print("alphabet symbol pair labels =", alphabet_label_list) ##

if __name__ == "__main__":
    read_examples()
    print("alphabet =", alphabet)
