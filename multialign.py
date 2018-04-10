import re, sys, hfst

verbosity = 0

vowel_features = {
    'j':('Semivowel','Front','Unrounded'),
    'i':('Close','Front','Unrounded'),
    'y':('Close','Front','Rounded'),
    'u':('Close','Back','Rounded'),
    'e':('Mid','Front','Unrounded'),
    'ö':('Mid','Front','Rounded'),
    'o':('Mid','Back','Rounded'),
    'á':('Open','Front','Unrounded'),
    'ä':('Open','Central','Unrounded'),
    'â':('Open','Central','Unrounded'),
    'a':('Open','Back','Unrounded'),
    "´":('Length','Length','Length'),
    'Ø':('Zero','Zero','Zero')
    }

#cmo = {'Semivowel':0.0, 'Close':1.0, 'Mid':2.0, 'Open':3.0}
#fb = {'Front':1, 'Back':2}
#ur = {'Unrounded':1, 'Rounded':2}
vowels = set(vowel_features.keys())

semivowels = set('j')
semivowel_vowels = {'j': frozenset(['i', 'j', 'Ø'])}

def vowel_set_weight(subset):
    w = len(subset)
    svs = subset.intersection(semivowels)
    if svs:
        for sv in svs:
            if not subset <= semivowel_vowels[sv]:
                w += 10
    if ('Ø' in subset): w -= 0.6
    return float(w)

consonant_features = {
    'm':('Bilab','Voiced','Nasal'),
    'p':('Bilab','Unvoiced','Stop'),
    'b':('Bilab','Voiced','Stop'),
    'v':('Labdent','Voiced','Fricative'),
    'f':('Labdent','Unvoiced','Fricative'),
    'w':('Labdent','Voiced','Fricative'),
    'đ':('Dental','Voiced','Fricative'),
    'n':('Alveolar','Voiced','Nasal'),
    'z':('Alveolar','Voiced','Affricate'),
    'c':('Alveolar','Unvoiced','Affricate'),
    't':('Alveolar','Unvoiced','Stop'),
    'z':('Alveolar','Unvoiced','Stop'),
    'ž':('Alveolar','Unvoiced','Stop'),
    'd':('Alveolar','Voiced','Stop'),
    'š':('Postalveolar','Unvoiced','Fricative'),
    'č':('Postalveolar','Unvoiced','Affricate'),
    's':('Alveolar','Unvoiced','Sibilant'),
    'š':('Alveolar','Unvoiced','Sibilant'),
    'ž':('Alveolar','Voiced','Sibilant'),
    'l':('Alveolar','Voiced','Lateral'),
    'r':('Alveolar','Voiced','Tremulant'),
    'j':('Palatal','Voiced','Approximant'),
    'ŋ':("Velar","Voiced","Nasalŋ"),
    'k':('Velar','Unvoiced','Stop'),
    'c':('Velar','Unvoiced','Stop'),
    'x':('Velar','Unvoiced','Stop'), ##
    'g':('Velar','Voiced','Stop'),
    'h':('Glottal','Unvoiced','Fricative'),
    '`':('Zero', 'Zero', 'Zero'),
    'Ø':('Zero', 'Zero', 'Zero')
}

pos = {'Bilab':0.0, 'Labdent':1.0, 'Alveolar':2.0,
        'Postalveolar':2.5, 'Palatal':3.0, 'Velar':3.0, 'Glottal':4.0}
voic = {'Unvoiced':1, 'Voiced':2}
consonants = set(consonant_features.keys())

def cons_set_weight(subset):
    w = 0.0
    pmin, pmax = 100.0, 0.0
    vmin, vmax = 100.0, 0.0
    mm= set()
    for x in subset:
        if x in {'Ø', '`'}:
            #w += 2.6
            w += 1.5
        else:
            p, v, m = consonant_features[x]
            pval = pos[p]
            pmin = min(pval, pmin)
            pmax = max(pval, pmax)
            vval = voic[v]
            vmin = min(vval, vmin)
            vmax = max(vval, vmax)
            mm.add(m)
    #w += (len(mm) - 1.0)
    w += len(mm) * 0.5
    w += (pmax - pmin) * 0.6
    w += (vmax - vmin)
    # print(subset, w, pmin, pmax, vmin, vmax, mm) ###
    return w

mphon_separator = ''
weight_cache = {}

def mphon_weight(mphon):
    global  vowels, consonants, mphon_separator, weight_cache
    if mphon in weight_cache:
        return weight_cache[mphon]
    if mphon_separator == '':
        phon_list = list(mphon)
    else: phon_list = mphon.split(mphon_separator)
    phon_set = set(phon_list)
    if len(phon_set) == 1 and 'Ø' in phon_set:
        weight = 100.0
    elif len(phon_set) == 1:
        weight = 0.0
    elif phon_set <= consonants:
        # return float(len(phon_set))
        weight = cons_set_weight(phon_set)
    elif phon_set <= vowels:
        # return float(len(phon_set))
        weight = vowel_set_weight(phon_set)
    else:
        #weight = float('Infinity')
        weight = 1000000.0
    weight_cache[mphon] = weight
    return weight

def mphon_is_valid(mphon):
    global  vowels, consonants, mphon_separator
    if mphon_separator == '':
        phon_list = list(mphon)
    else: phon_list = mphon.split(mphon_separator)
    phon_set = set(phon_list)
    if phon_set <= vowels:
        return True
    elif phon_set <= consonants:
        return True
    else:
        return False

def fst_to_fsa(FST):
    global mphon_separator
    FB = hfst.HfstBasicTransducer(FST)
    sym_pairs = FB.get_transition_pairs()
    dict = {}
    for sym_pair in sym_pairs:
        in_sym, out_sym = sym_pair
        joint_sym = in_sym + mphon_separator + out_sym
        dict[sym_pair] = (joint_sym, joint_sym)
    FB.substitute(dict)
    RES = hfst.HfstTransducer(FB)
    return RES

def remove_bad_transitions(FST, weighting, max_weight_allowed):
    OLD = hfst.HfstBasicTransducer(FST)
    NEW = hfst.HfstBasicTransducer()
    for state in OLD.states():
        NEW.add_state(state)
        if OLD.is_final_state(state):
            NEW.set_final_weight(state, 0.0)
        for arc in OLD.transitions(state):
            in_sym = arc.get_input_symbol()
            if mphon_is_valid(in_sym):
                target_st = arc.get_target_state()
                NEW.add_transition(state, target_st, in_sym, in_sym, 0)
    RES = hfst.HfstTransducer(NEW)
    RES.minimize()
    return RES

def shuffle_with_zeros(string, target_length):
    S = hfst.fst(string)
    l = len(string)
    if l < target_length:
        n = target_length - l
        Z = hfst.regex(' '.join(n * 'Ø'))
        S.shuffle(Z)
    S.minimize()
    S.set_name(string)
    return S

def set_weights(FST, weighting):
    global verbosity
    B = hfst.HfstBasicTransducer(FST)
    for state in B.states():
        for arc in B.transitions(state):
            tostate = arc.get_target_state()
            insym = arc.get_input_symbol()
            outsym = arc.get_output_symbol()
            w = weighting(insym)
            arc.set_weight(w)
    RES = hfst.HfstTransducer(B)
    if verbosity >=20:
        print("set_weights:\n", RES)
    return RES

def multialign(strings, target_length, max_weight_allowed=1000.0):
    global verbosity
    s1 = strings[0]
    R = shuffle_with_zeros(s1, target_length)
    for string in strings[1:]:
        S = shuffle_with_zeros(string, target_length)
        R.cross_product(S)
        T = fst_to_fsa(R)
        R = remove_bad_transitions(T, mphon_weight, max_weight_allowed)
        R.minimize()
    RES = set_weights(R, mphon_weight)
    if verbosity >=20:
        print("multialign:\n", RES)
    return RES

def list_of_aligned_words(sym_lst):
    if not sym_lst: return ''
    l = len(sym_lst[0])
    res = []
    for i in range(l):
        syms = [itm[i:i+1] for itm in sym_lst]
        res.append(''.join(syms))
    return res

def prefer_final_zeros(results):
    best_weight = results[0][0]
    best_bias = -1
    for sym_pair_seq in results:
        lst = [isym for isym in sym_pair_seq]
        bias = 0
        i = 0
        for isym in lst:
            bias = bias + i * isym.count('Ø')
            i = i + 1
        #print('  '.join(lst), w, bias) ##
        if bias > best_bias:
            best_bias = bias
            best = lst
    return best

def classify_sym(sym):
    char_set = set(sym)
    if char_set <= consonants:
        if 'Ø' in char_set:
            return 'c'
        else: return 'C'
    elif 'Ø' in char_set:
        return 'v'
    else: return 'V'

consonant_lst = sorted(list(consonants))
vowel_lst =sorted(list(vowels))
consonant_re = '(' + '|'.join(consonant_lst) + ')'
vowel_re = '(' + '|'.join(vowel_lst) + ')'

def prefer_syl_struct(results):
    best_weight = results[0][0]
    best_bias = 99999
    best_lst = []
    for weight, sym_pair_seq in results:
        if weight > best_weight: break
        sym_lst = [isym for isym,outsym in sym_pair_seq]
        #print('sym_lst:', '  '.join(sym_lst)) ##
        csym_lst = [classify_sym(sym) for sym in sym_lst]
        csym_str = ''.join(csym_lst)
        #print('csym_lst:', '  '.join(csym_lst)) ##
        syl_bias = len(re.findall(r'(C|c)+|(V|v)+', csym_str))
        #print('syl_bias:', syl_bias)###
        zero_bias = len(re.findall(r'(cC|vV)', csym_str))
        #print('zero_bias:', zero_bias)###
        bias = syl_bias + zero_bias
        if bias < best_bias:
            best_bias = bias
            best_lst.append(sym_lst)
    #print('best:', best, '\n')####
    return best_lst

def aligner(words, max_zeros_in_longest, line, verbosity=0,
                max_weight_allowed=1000.0):
    max_length = max([len(x) for x in words])
    RES = hfst.empty_fst()
    for m in range(max_length, max_length + max_zeros_in_longest):
        R = multialign(words, m)
        if R.compare(hfst.empty_fst()):
            if verbosity > 1:
                print("target length", m, "failed")
            continue
        RES.disjunct(R)
        RES.minimize()
    RES.n_best(10)
    RES.minimize() # accepts 10 best results
    results = RES.extract_paths(output='raw')
    for w, sym_pair_seq in results:
        lst = [isym for isym, outsym in sym_pair_seq]
        if verbosity >= 5:
            mpw = ["{}::{:.2f}".format(x, mphon_weight(x)) for x in lst]
            print(" ".join(mpw), "total weight = {:.3f}".format(w))
    if len(results) < 1:
        print("*** NO ALIGNMENTS FOR:", line, "***", results)
        return([])
    best_syl_struct = prefer_syl_struct(results)
    best = prefer_final_zeros(best_syl_struct)
    return best

if __name__ == "__main__":
    import argparse
    arpar = argparse.ArgumentParser("python3 multialign.py")
    arpar.add_argument("-l", "--layout",
                       choices=['vertical','list','horizontal'],
                       help="output layout",
                       default="vertical")
    arpar.add_argument("-v", "--verbosity",
                       help="level of diagnostic output",
                       type=int, default=0)
    arpar.add_argument("-z", "--zeros",
                       help="number of extra zeros beyond the minimum",
                       type=int, default=1)
    args = arpar.parse_args()
    verbosity = args.verbosity
    
    for line in sys.stdin:
        words = line.strip().split(sep=' ')
        ##words = sorted(words, key=lambda w: -len(w))

        best = aligner(words, args.zeros, line, args.verbosity)

        best2 = [re.sub(r'^([a-zšžŋđüõåäöáâ`´])\1\1*$', r'\1', cc) for cc in best]
        # print('best =', best2, "\n", ' '.join(best2)) ##
        if args.layout == "horizontal":
            print(' '.join(best2))
        elif args.layout == "vertical":
            print('\n'.join(list_of_aligned_words(best)))
        elif args.layout == 'list':
            print(' '.join(list_of_aligned_words(best)))
        # print('  '.join(best2), best_bias)
    
