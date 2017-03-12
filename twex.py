"""A module for reading two-level examples

The examples are assumed to be as space-separated one-level
representation and they are compiled into a single automaton. 
At the same time, the alphabet used in the examples is 
collected in several forms.

    EXAMPLES -- the transducer which accepts exactly the examples

    symbol_pair_set -- a tuple of string pairs suitable for
        e.g. hfst.rules.restriction

"""
import hfst, re, twbt

symbol_pair_set = set()
input_symbol_set = set()
output_symbol_set = set()
pair_symbols_for_input = {}
pair_symbols_for_output = {}

example_set = set()
example_list = []
EXAMPLES = hfst.HfstTransducer()

def label2pair(label):
    m = re.match(r"^([^:]*):([^:]*)$", label)
    if m:
        return(m.group(1), m.group(2))
    else:
        return(label, label)

def pair2psym(insym, outsym):
    if insym == outsym:
        return(insym)
    else:
        return(insym + ':' + outsym)

def read_examples(filename="test.pairstr"):
    """Reads the examples from the file whose name is 'filename'.

Use help(twex) in order to get more information.
"""
    global symbol_pair_set, EXAMPLES, pair_symbols_for_input, example_list, example_set
    EXAMPLES.set_name(filename)
    exfile = open(filename,"r")
    for line in exfile:
        lin = line.strip()
        lst = re.split(" +", lin)
        line_tok = [label2pair(label) for label in lst]
        # print("line_tok:", line_tok) ##
        psymlst = " ".join([pair2psym(insym, outsym)
                            for insym,outsym
                            in line_tok])
        # print("psymlst:", psymlst) ##
        example_set.add(psymlst) # spaces normalized
        example_list.append(psymlst)
        # print(line_tok) ##
        LINE_FST = hfst.tokenized_fst(line_tok)
        # twbt.printfst(LINE_FST, True) ##
        EXAMPLES.disjunct(LINE_FST)
        for insym, outsym in line_tok:
            # print(insym, outsym, end="") ##
            symbol_pair_set.add((insym, outsym))
    exfile.close()
    # symbol_pair_set.add(('Ø', 'Ø')) ### ?
    # print("List of alphabet symbols:", sorted(symbol_pair_set)) ##
    EXAMPLES.minimize()
    # twbt.printfst(EXAMPLES, False) ##
    for insym, outsym in symbol_pair_set:
        input_symbol_set.add(insym)
        output_symbol_set.add(outsym)
    for insym in input_symbol_set:
        pair_symbols_for_input[insym] = set()
    for outsym in output_symbol_set:
        pair_symbols_for_output[outsym] = set()
    for insym, outsym in symbol_pair_set:
        pair_symbol = insym if insym == outsym else insym + ":" + outsym
        pair_symbols_for_input[insym].add(pair_symbol)
        pair_symbols_for_output[outsym].add(pair_symbol)
    return

def relevant_contexts(pair_symbol):
    global pair_symbols_for_input, example_set
    input_symbol, output_symbol = label2pair(pair_symbol)
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
            # print(i1, i2, example) ##
            left_context = example[0:i1-1]
            centre = example[i1:i2]
            right_context = example[i2+1:]
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
        insym, outsym = label2pair(pairsym)
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
    print("symbol_pair_set =", symbol_pair_set)
    # for ex in example_set: ##
    #     print(ex) ##
    print("pair_symbols_for_input:", pair_symbols_for_input) ##
    print("positive examples:")
    for ex in positive_examples({"{ao}", "{ij}"}):
        print(ex)
    print("negative examples:")
    for ex in negative_examples({"{ao}", "{ij}"}):
        print(ex)
