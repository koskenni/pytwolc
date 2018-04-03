"""Global values for twol modules.
"""
import hfst, re
hfst.set_default_fst_type(hfst.ImplementationType.FOMA_TYPE)

verbosity = 0
definitions = {}

error_message = ""

all_pairs_fst = hfst.empty_fst() # accepts any one symbol pair

symbol_pair_set = set() # all symbol pairs (e.g. ('{aä}', 'a'))
input_symbol_set = set()
output_symbol_set = set()
pair_symbol_set = set() # all pair symbols (e.g. '{aä}:a')

examples_fst = None # consists of all correspondences in the examples 

def pairsym2sympair(pairsym):
    m = re.match(r"^([^:]*):([^:]*)$", pairsym)
    if m:
        return(m.group(1), m.group(2))
    else:
        return(pairsym, pairsym)

def sympair2pairsym(insym, outsym):
    if insym == outsym:
        return(insym)
    else:
        return(insym + ':' + outsym)
