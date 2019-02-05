"""Aligns multiple morphs according to phonological features
by adding zero symbols.
"""

import re, sys
import hfst
import cfg

vowel_features = {
    'j':('Semivowel','Front','Unrounded'),
    'i':('Close','Front','Unrounded'),
    'y':('Close','Front','Rounded'),
    'ü':('Close','Front','Rounded'),      # Estonian, IPA y
    'u':('Close','Back','Rounded'),
    'õ':('Mid','Back','Unrounded'),       # Estonian - IPA ɤ (Close-Mid, Back, Unrounded)
    'e':('Mid','Front','Unrounded'),
    'ö':('Mid','Front','Rounded'),        # IPA ø
    'o':('Mid','Back','Rounded'),
    'á':('Open','Front','Unrounded'),     # Inari Sami, IPA a
    'ä':('Open','Front','Unrounded'),     # Estonian, æ
    'â':('Open','Central','Unrounded'),   # Inari Saami, IPA ɐ
    'a':('Open','Back','Unrounded'),      # Finnish, IPA ɑ
    "´":('Length','Length','Length'),
    'Ø':('Zero','Zero','Zero')
    }

"""Phonological distinctive features of vowels which can be used of
estimating similarities between phonemes."""

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
    'd̕':('Dental','Voiced','Fricative'),
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
    'š':('Alveolar','Unvoiced','Sibilant'),   # IPA ʃ
    'ž':('Alveolar','Voiced','Sibilant'),
    'l':('Alveolar','Voiced','Lateral'),
    'r':('Alveolar','Voiced','Tremulant'),
    'j':('Palatal','Voiced','Approximant'),
    'ŋ':("Velar","Voiced","Nasalŋ"),      # Inari Sami
    'k':('Velar','Unvoiced','Stop'),
    'c':('Velar','Unvoiced','Stop'),
    'x':('Velar','Unvoiced','Stop'), ##
    'g':('Velar','Voiced','Stop'),
    'h':('Glottal','Unvoiced','Fricative'),
    '`':('Zero', 'Zero', 'Zero'),
    'Ø':('Zero', 'Zero', 'Zero')
}

"""Phonological distinctive features of consonants to be used when
estimating similarities between phonemes.  """

pos = {'Bilab':0.0, 'Labdent':1.0, 'Alveolar':2.0,
        'Postalveolar':2.5, 'Palatal':3.0, 'Velar':3.0, 'Glottal':4.0}
voic = {'Unvoiced':1, 'Voiced':2}
consonants = set(consonant_features.keys())

def cons_set_weight(subset):
    """Computes a weight for a subset of consonants."""
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
"""Separator used when forming names of raw morphophonemes"""

weight_cache = {}

def mphon_weight(mphon):
    """Computes a weight for a raw morphophoneme"""
    global  vowels, consonants, mphon_separator, weight_cache
    if mphon in weight_cache:
        return weight_cache[mphon]
    if mphon_separator == '':
        phon_list = list(mphon)
    else:
        phon_list = mphon.split(mphon_separator)
    phon_set = set(phon_list)
    if phon_set == {'Ø'}:
        weight = 100.0        # all-zero morphophonemes must be allowed
    elif len(phon_set) == 1:
        weight = 0.0
    elif phon_set <= consonants:
        weight = cons_set_weight(phon_set)
    elif phon_set <= vowels:
        weight = vowel_set_weight(phon_set)
    else:
        #weight = float('Infinity')
        weight = 1000000.0
    weight_cache[mphon] = weight
    if cfg.verbosity >= 35:
        print("mphon:", mphon, "weight:", weight)
    return weight

def mphon_is_valid(mphon):
    """Tests if a raw morphophoneme is all consonants or all vowels"""
    global  vowels, consonants, mphon_separator
    if mphon_separator == '':
        phon_list = list(mphon)
    else:
        phon_list = mphon.split(mphon_separator)
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

def remove_bad_transitions(fsa):
    """Copy the FSA excluding transitions with consonants and vowels"""
    old_bfsa = hfst.HfstBasicTransducer(fsa)
    new_bfsa = hfst.HfstBasicTransducer()
    for state in old_bfsa.states():
        new_bfsa.add_state(state)
        if old_bfsa.is_final_state(state):
            new_bfsa.set_final_weight(state, 0.0)
        for arc in old_bfsa.transitions(state):
            in_sym = arc.get_input_symbol()
            if mphon_is_valid(in_sym):
                target_st = arc.get_target_state()
                new_bfsa.add_transition(state, target_st, in_sym, in_sym, 0)
    result_fsa = hfst.HfstTransducer(new_bfsa)
    result_fsa.minimize()
    if cfg.verbosity >= 20:
        print("remove_bad_transitions:")
        print(result_fsa)
    return result_fsa

def shuffle_with_zeros(string, target_length):
    """Return a fsa where zeros are inserted in all possible ways
    
    string -- the string to which zero symbols are inserted

    target_length -- how long the strings after insertions must be

    Returns a fsa which accepts all the strings with the inserted zeros.
    All strings have exactly target_length symbols.
    """
    result_fsa = hfst.fst(string)
    l = len(string)
    if l < target_length:
        n = target_length - l
        n_zeros_fsa = hfst.regex(' '.join(n * 'Ø'))
        result_fsa.shuffle(n_zeros_fsa)
    result_fsa.minimize()
    result_fsa.set_name(string)
    if cfg.verbosity >= 30:
        print("shuffle_with_zeros:")
        print(result_fsa)
    return result_fsa

def set_weights(fsa):
    """Sets weights to transitions using mphon_weight()
    """
    bfsa = hfst.HfstBasicTransducer(fsa)
    for state in bfsa.states():
        for arc in bfsa.transitions(state):
            tostate = arc.get_target_state()
            insym = arc.get_input_symbol()
            outsym = arc.get_output_symbol()
            w = mphon_weight(insym)
            arc.set_weight(w)
    weighted_fsa = hfst.HfstTransducer(bfsa)
    if cfg.verbosity >=20:
        print("set_weights:\n", weighted_fsa)
    return weighted_fsa

def multialign(strings, target_length):
    """Align a list of strings by making them target_lenght long
    
    Zero symbols are added optimally so that the sets of corresponding
    phonemes are similar.  Note that the alignment need not be feasible
    if the target lenght is too small and also that there may be
    all-zero correspondences if the target length is too long.
    """
    s1 = strings[0]
    fsa = shuffle_with_zeros(s1, target_length)
    for string in strings[1:]:
        suf_fsa = shuffle_with_zeros(string, target_length)
        fsa.cross_product(suf_fsa)      # results in a transducer
        prod_fsa = fst_to_fsa(fsa)      # encodes the fst as a fsa
        fsa = remove_bad_transitions(prod_fsa)
        fsa.minimize()
    wfsa = set_weights(fsa)
    if cfg.verbosity >=20:
        print("multialign:\n", wfsa)
    return wfsa

def list_of_aligned_words(sym_lst):
    if not sym_lst:
        return []
    l = len(sym_lst[0])
    res = []
    for i in range(l):
        syms = [itm[i:i+1] for itm in sym_lst]
        res.append(''.join(syms))
    return res

def prefer_final_zeros(sym_lst_lst):
    """Select the symbol pair sequence where the zeros are near the end

    sym_lst_lst -- a list of results, each consisting of a list
    of symbols (already selected according to other criteria)

    Returns a sequence of (single) symbols where the zeros occur near
    the end.  This normalizes gemination and lengthening so that the
    latter component is the one which alternates with a zero.
    """
    best_bias = -1
    for sym_lst in sym_lst_lst:
        lst = [isym for isym in sym_lst]
        bias = 0
        i = 0
        for isym in lst:
            bias = bias + i * isym.count('Ø')
            i = i + 1
        #print('  '.join(lst), w, bias) ##
        if bias > best_bias:
            best_bias = bias
            best_sym_lst = lst
    return best_sym_lst

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
    """Selects alignments according to syllable structure and zero count

    results -- list of tuples (weight, sym_pair_seq) (out of which the
    result list is chosen).  The sym_pair_seq is in the format that
    hfst.extract_paths() produces.

    Returns a list the best alternatives, i.e. those getting the lowest
    scores of the sum of syllable count and the number of instances
    where the former component of a CC or VV corresponds to zero.
    Elements in the returned list are sequences of symbols.
    """
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

def aligner(words, max_zeros_in_longest, line):
    """Aligns a list of words according to similarity of their phonemes

    words -- a list of words (or morphs) to be aligned

    max_zeros_in_longest -- maximum number of zeros to be inserted into
    the longest word

    line -- the input line (used only in warning messages)

    Returns the best alignment as a list of raw morphophoneme.
    """
    max_length = max([len(x) for x in words])
    weighted_fsa = hfst.empty_fst()
    for m in range(max_length, max_length + max_zeros_in_longest + 1):
        R = multialign(words, m)
        if R.compare(hfst.empty_fst()):
            if cfg.verbosity > 1:
                print("target length", m, "failed")
            continue
        weighted_fsa.disjunct(R)
        weighted_fsa.minimize()
    weighted_fsa.n_best(10)
    weighted_fsa.minimize() # accepts 10 best results
    results = weighted_fsa.extract_paths(output='raw')
    if cfg.verbosity >= 5:
        for w, sym_pair_seq in results:
            lst = [isym for isym, outsym in sym_pair_seq]
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
    cfg.verbosity = args.verbosity
    
    for line in sys.stdin:
        words = line.strip().split(sep=' ')
        ##words = sorted(words, key=lambda w: -len(w))

        best = aligner(words, args.zeros, line)

        best2 = [re.sub(r'^([a-zšžŋđüd̕õåäöáâ`´])\1\1*$', r'\1', cc)
                 for cc in best]
        # print('best =', best2, "\n", ' '.join(best2)) ##
        if args.layout == "horizontal":
            print(' '.join(best2))
        elif args.layout == "vertical":
            print('\n'.join(list_of_aligned_words(best)))
        elif args.layout == 'list':
            print(' '.join(list_of_aligned_words(best)))
        # print('  '.join(best2), best_bias)
    
