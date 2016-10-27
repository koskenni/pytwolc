import hfst

def pairname(insym, outsym):
    if insym == outsym:
        return(insym)
    else:
        return(insym + ":" + outsym)

def equivpairs(bfst):
    transitions_for_pairsymbol = {} # {pairsym: list of trs, ..}
    for state in bfst.states():
        for arc in bfst.transitions(state):
            target = arc.get_target_state()
            pair_symbol = pairname(arc.get_input_symbol(),
                               arc.get_output_symbol())
            if pair_symbol not in transitions_for_pairsymbol:
                transitions_for_pairsymbol[pair_symbol] = set()
            transitions_for_pairsymbol[pair_symbol].add((state,target))
    pairsymbols_for_transition_sets = {} # {tr set: pair syms, ..}
    for pair_symbol, st in transitions_for_pairsymbol.items():
        froz = frozenset(st)
        if froz not in pairsymbols_for_transition_sets:
            pairsymbols_for_transition_sets[froz] = []
        pairsymbols_for_transition_sets[froz].append(pair_symbol)
    labelsym = {} # {sym: sym representing it in pprinting}
    for fs, sl in pairsymbols_for_transition_sets.items():
        sorted_sl = sorted(sl)
        model = sorted(sl)[0]
        for sym in sorted(sl):
            if len(sym) < len(model): model = sym 
        for sym in sorted(sl):
            labelsym[sym] = model
    #print("labelsym: ", labelsym) ##
    return(labelsym, pairsymbols_for_transition_sets)

def printfst(fst, print_equiv_classes):
    name = fst.get_name()
    print(name)
    bfst = hfst.HfstBasicTransducer(fst)
    labsy, transy = equivpairs(bfst)
    for state in bfst.states():
        d = {}
        for arc in bfst.transitions(state):
            target = arc.get_target_state()
            if target not in d: d[target] = []
            prnm = pairname(arc.get_input_symbol(),
                            arc.get_output_symbol())
            d[target].append(prnm)
        print(" ", state, (": " if bfst.is_final_state(state) else ". "), end="")
        for st, plist in d.items():
            ls = [p for p in plist if p == labsy[p]]
            print("-> " + str(st) + "  " + (" ".join(ls)), end=" ; " )
        print()
    #print(transy) ##
    if print_equiv_classes:
        print("Classes of equivalent symbols:")
        for ss, pl in transy.items():
            if len(pl) > 1:
                print(" ", " ".join(sorted(pl)))
    
