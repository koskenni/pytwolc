import hfst
import re

pairs_with_insym = {}

def dict_rule(rule_fst):
    brule = hfst.HfstBasicTransducer(rule_fst)
    rule_dict = {}
    final_states = set()
    for state in brule.states():
        if brule.is_final_state(state):
            final_states.add(state)
        trans_dict = {}
        for transition in brule.transitions(state):
            insym = transition.get_input_symbol()
            outsym = transition.get_output_symbol()
            target = transition.get_target_state()
            trans_dict[(insym,outsym)] = target
            if insym not in pairs_with_insym:
                pairs_with_insym[insym] = set()
            pairs_with_insym[insym].add((insym, outsym))
        rule_dict[state] = trans_dict
    return rule_dict, final_states

istream = hfst.HfstInputStream("ofi-rules.fst")
rule_dict_lst = []
finality_dict_lst = []
while not (istream.is_eof()):
    fst = istream.read()
    rule_d, final_states = dict_rule(fst)
    rule_dict_lst.append(rule_d)
    finality_dict_lst.append(final_states)
istream.close()

result_lst = []

def search(state_lst, insym_lst, outsym_lst):
    global result_lst
    if not insym_lst:
        for state, finality in zip(state_lst, finality_dict_lst):
            if state not in finality:
                return
        res = "".join(outsym_lst)
        #print(res)
        result_lst.append(res)
        return
    insym = insym_lst[0]
    pair_set = pairs_with_insym[insym]
    for insym, outsym in pair_set:
        new_state_lst = []
        for state, rule_d in zip(state_lst, rule_dict_lst):
            if (insym, outsym) in rule_d[state]:
                new_state_lst.append(rule_d[state][(insym, outsym)])
            else:
                break
        else:
            new_outsym_lst = outsym_lst.copy()
            new_outsym_lst.append(outsym)
            search(new_state_lst, insym_lst[1:], new_outsym_lst)
        continue
    
    return
        

def generate(word):
    global result_lst
    result_lst = []
    insym_lst = re.findall(r"{[^{}]+}|[^{}]", word)
    start_state_lst = [0 for r in rule_dict_lst]
    search(start_state_lst, insym_lst, [])
    return result_lst

if __name__ == "__main__":
    import sys, re
    for line_nl in sys.stdin:
        line = line_nl.strip()
        res = generate(line)
        print("results:", res)
        print()
    
