import sys, re
import twex

import argparse
arpar = argparse.ArgumentParser("python3 plytw.py")
arpar.add_argument("-e", "--examples", help="name of the examples file",
                   default="test.pairstr")
#arpar.add_argument("-r", "--rules", help="name of the rule file",
#                   default="test.rules")
arpar.add_argument("-v", "--verbosity",
                   help="level of  diagnostic output",
                   type=int, default=0)
arpar.add_argument("-d", "--debug",
                   help="level of PLY debugging output",
                   type=int, default=0)
args = arpar.parse_args()

def ppcontexts(ctxs):
    for lc, rc in sorted(ctxs):
        print(lc, '_', rc)

def print_rule(pair_symbol, contexts):
    print(pair_symbol, "=>")
    for lc, rc in contexts:
        print("   ", lc, "_", rc, ";")

def shorten_contexts(contexts, left_length, right_length):
    # print("left and right length:", left_length, right_length) ##
    # ppcontexts(contexts) ##
    new_contexts = set()
    for left_context, right_context in contexts:
        left_lst = left_context.split(' ')
        start = max(0, len(left_lst) - left_length)
        new_lc = ' '.join(left_lst[start:])
        # print("start:", start, "new_lc:", new_lc)
        right_lst = right_context.split(' ')
        new_rc = ' '.join(right_lst[0:right_length])
        new_contexts.add((new_lc, new_rc))
    return(new_contexts)

twex.read_examples(filename=args.examples) # if not already read
print("--- all examples read in ---")

def minimal_contexts(pair_symbol):
    pos_contexts, neg_contexts = twex.relevant_contexts(pair_symbol)
    # ppcontexts(pos_contexts) ##
    # ppcontexts(neg_contexts) ##
    # find maximum lengths (in psyms) of left and right contexts
    left_len = 0
    right_len = 0
    for left_context, right_context in pos_contexts:
        lcount = left_context.count(' ')
        if lcount >= left_len: left_len = lcount + 1
        rcount = right_context.count(' ')
        if rcount >= right_len: right_len = rcount + 1
    for left_context, right_context in neg_contexts:
        lcount = left_context.count(' ')
        if lcount >= left_len: left_len = lcount + 1
        rcount = right_context.count(' ')
        if rcount >= right_len: right_len = rcount + 1

    # shorten the contexts stepwise while the positive and
    # the negative contexts stay disjoint
    p_contexts = pos_contexts.copy()
    n_contexts = neg_contexts.copy()
    left_incomplete = True
    right_incomplete = True
    while left_incomplete or right_incomplete:
        # print(left_len, right_len) ##
        if left_incomplete and left_len > 0:
            new_p_contexts = shorten_contexts(p_contexts, left_len-1, right_len)
            new_n_contexts = shorten_contexts(n_contexts, left_len-1, right_len)
            if new_p_contexts.isdisjoint(new_n_contexts):
                # print("still disjoint") ##
                p_contexts = new_p_contexts
                n_contexts = new_n_contexts
                left_len = left_len - 1
            else:
                # print("left side now complete") ##
                # ppcontexts(new_p_contexts & new_n_contexts)
                left_incomplete = False
        elif right_incomplete and right_len > 0:
            new_p_contexts = shorten_contexts(p_contexts, left_len, right_len-1)
            new_n_contexts = shorten_contexts(n_contexts, left_len, right_len-1)
            if new_p_contexts.isdisjoint(new_n_contexts):
                # print("still disjoint") ##
                p_contexts = new_p_contexts
                n_contexts = new_n_contexts
                right_len = right_len - 1
            else:
                # print("left side now complete") ##
                right_incomplete = False
        else:
            # print("everything now complete") ##
            break

    # print("positive contexts:")
    ## ppcontexts(p_contexts)
    print_rule(pair_symbol, p_contexts)
    # print("negative contexts:")
    # ppcontexts(n_contexts)
    return

for insym, outsym in sorted(twex.symbol_pair_set):
# for insym, outsym in sorted({('{ao}', 'o')}):
    if len(twex.pair_symbols_for_input[insym]) <= 1: continue
    psym = twex.pair2psym(insym, outsym)
    ## print("--- ", psym, " ---")
    minimal_contexts(psym)

