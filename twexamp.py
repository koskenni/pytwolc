"""A module for reading two-level examples

The examples are assumed to be as space-separated one-level
representation and they are compiled into a single automaton. 
At the same time, the alphabet used in the examples is 
collected in several forms.

    EXAMPLES -- the transducer which accepts exactly the examples

    symbol_pair_set -- a tuple of string pairs suitable for
        e.g. hfst.rules.restriction

"""
import hfst, re, twbt, cfg

pair_symbols_for_input = {} # key: input symbol, value: set of pair symbols
pair_symbols_for_output = {}

example_set = set()
example_list = []

def read_fst(filename="examples.fst"):
    exfile = hfst.HfstInputStream(filename)
    cfg.examples_fst = exfile.read()
    pair_symbols = cfg.examples_fst.get_property("x-pair_symbols")
    # print("pair_symbols", pair_symbols) ##
    pair_symbol_lst = re.split(r" +", pair_symbols)
    for pair in pair_symbol_lst:
        cfg.pair_symbol_set.add(pair)
        (insym, outsym) = cfg.pairsym2sympair(pair)
        cfg.symbol_pair_set.add((insym, outsym))
        cfg.input_symbol_set.add(insym)
        cfg.output_symbol_set.add(outsym)
    cfg.all_pairs_fst = hfst.empty_fst()
    for insym, outsym in cfg.symbol_pair_set:
        in_quoted = re.sub(r"([{}])", r"%\1", insym)
        pair_fst = hfst.regex(in_quoted + ':' + outsym)
        cfg.all_pairs_fst.disjunct(pair_fst)
    cfg.all_pairs_fst.remove_epsilons()
    cfg.all_pairs_fst.minimize()
    if cfg.verbosity_level >= 30:
        twbt.ppfst(cfg.all_pairs_fst, title="cfg.all_pairs_fst")
    return
    
def read_examples(filename="test.pairstr"):
    """Reads the examples from the file whose name is 'filename'.

Use help(twex) in order to get more information.
"""
    global pair_symbols_for_input, example_list, example_set
    examples_bfst = hfst.HfstBasicTransducer()
    exfile = open(filename,"r")
    for line in exfile:
        lin = line.strip()
        if lin == "" or lin[0] == '!': continue
        lst = re.split(" +", lin)
        line_tok = [cfg.pairsym2sympair(pairsym) for pairsym in lst]
        # print("line_tok:", line_tok) ##
        psymlst = " ".join([cfg.sympair2pairsym(insym, outsym)
                            for insym,outsym
                            in line_tok])
        # print("psymlst:", psymlst) ##
        example_set.add(psymlst) # spaces normalized
        example_list.append(psymlst)
        # print(line_tok) ##
        #LINE_FST = hfst.tokenized_fst(line_tok)
        # twbt.printfst(LINE_FST, True) ##
        examples_bfst.disjunct(line_tok, 0)
        for insym, outsym in line_tok:
            # print(insym, outsym, end="") ##
            cfg.symbol_pair_set.add((insym, outsym))
    exfile.close()
    # print("List of alphabet symbols:", sorted(cfg.symbol_pair_set)) ##
    cfg.examples_fst = hfst.HfstTransducer(examples_bfst)
    cfg.examples_fst.set_name(filename)
    cfg.examples_fst.minimize()
    # twbt.printfst(cfg.examples_fst, False) ##
    for insym, outsym in cfg.symbol_pair_set:
        cfg.input_symbol_set.add(insym)
        cfg.output_symbol_set.add(outsym)
    for insym in cfg.input_symbol_set:
        pair_symbols_for_input[insym] = set()
    for outsym in cfg.output_symbol_set:
        pair_symbols_for_output[outsym] = set()
    for insym, outsym in cfg.symbol_pair_set:
        pair_symbol = cfg.sympair2pairsym(insym, outsym)
        cfg.pair_symbol_set.add(pair_symbol)
        pair_symbols_for_input[insym].add(pair_symbol)
        pair_symbols_for_output[outsym].add(pair_symbol)
    pair_symbol_lst = [insym+':'+outsym for insym, outsym in cfg.symbol_pair_set]
    pair_symbols = " ".join(sorted(pair_symbol_lst))
    # print("symbol pairs:", pair_symbols) ##
    cfg.examples_fst.set_property("x-pair_symbols", pair_symbols)
    return

def relevant_contexts(pair_symbol):
    global pair_symbols_for_input, example_set
    input_symbol, output_symbol = cfg.pairsym2sympair(pair_symbol)
    positive_context_set = set()
    negative_context_set = set()
    pairsymlist = [re.sub(r'([}{])', r'\\\1', psym)
                   for psym
                   in pair_symbols_for_input[input_symbol]]
    # print("pairsymlist:", pairsymlist) ##
    pattern = re.compile("|".join(pairsymlist))
    for example in example_set:
        for m in pattern.finditer(example):
            i1 = m.start()
            i2 = m.end()
            # print('"' + example[0:i1] +'"', '"' + example[i2:] + '"') ##
            left_context = ".#. " + example[0:i1-1]
            centre = example[i1:i2]
            if i2 >= len(example):
                right_context = ".#."
            else:
                right_context = example[i2+1:] + " .#."
            context = (left_context, right_context)
            # print(centre, context) ##
            if centre == pair_symbol:
                positive_context_set.add(context)
            else:
                negative_context_set.add(context)
    negative_context_set = negative_context_set - positive_context_set
    return(positive_context_set, negative_context_set)
    
def positive_examples(input_symbols):
    global pair_symbols_for_input, example_set
    result = set()
    insyms = set()
    for insym in input_symbols:
        # print("insym:", insym) ##
        insyms = insyms | pair_symbols_for_input[insym]
    pairsymlist = [re.sub(r'([}{])', r'\\\1', psym)
                   for psym
                   in insyms]
    # print("pairsymlist:", pairsymlist)
    pattern = re.compile("|".join(pairsymlist))
    # print("pattern:", "|".join(pairsymlist)) ##
    for example in example_set:
        if pattern.search(example):
            result.add(example)
    # print("positive_examples returns:", result) ##
    return(result)

negative_example_set = set()

def blur_output_symbol(input_symbols, result_list, remaining_list):
    global negative_example_set
    # print("result/remaining list;", result_list, remaining_list) ##
    if not remaining_list:
        negative_example_set.add(" ".join(result_list))
        return
    else:
        resl = result_list.copy()
        reml = remaining_list.copy()
        pairsym = reml[0]
        insym, outsym = cfg.pairsym2sympair(pairsym)
        if insym not in input_symbols:
            resl.append(pairsym)
            # print("res, remain:", resl, reml) ##
            blur_output_symbol(input_symbols, resl, reml[1:])
        else:
            for pairsym in pair_symbols_for_input[insym]:
                resl = result_list.copy()
                resl.append(pairsym)
                # print("res, remain:", resl, reml) ##
                blur_output_symbol(input_symbols, resl, reml[1:])
                
def negative_examples(input_symbols):
    global negative_example_set
    pos_exs = positive_examples(input_symbols)
    negative_example_set = set()
    for example in pos_exs:
        ex_as_list = re.split(" ", example)
        blur_output_symbol(input_symbols, [], ex_as_list)
    for example in pos_exs:
        negative_example_set.discard(example)
    return(negative_example_set)
    

if __name__ == "__main__":
    read_examples()
    print("symbol_pair_set =", cfg.symbol_pair_set)
    # for ex in example_set: ##
    #     print(ex) ##
    print("pair_symbols_for_input:", pair_symbols_for_input) ##
    print("positive examples:")
    for ex in positive_examples({"{ao}", "{ij}"}):
        print(ex)
    print("negative examples:")
    for ex in negative_examples({"{ao}", "{ij}"}):
        print(ex)
