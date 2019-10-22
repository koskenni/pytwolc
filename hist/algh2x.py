import hfst
import argparse

arpar = argparse.ArgumentParser(
    description="Build trivial FSTs which map"
    " the aligned language to its daughter languages")
arpar.add_argument(
    "input",
    help="A horizontally aligned file of examples")
arpar.add_argument(
    "languages",
    help="List of language ids of the daughter languages, e.g. 'fi,et'"
)
arpar.add_argument(
    "-v", "--verbosity",
    help="level of diagnostic output",
    type=int, default=0
)
args = arpar.parse_args()

correspondences = set()

corr_file = open(args.input, "r")

for line_nl in corr_file:
    line = line_nl.split("!")[0]
    #print(line) ###
    lst = line.strip().split()
    #print(lst) ###
    for corr in lst:
        correspondences.add(corr)
if args.verbosity > 10:
    print("correspondences:", correspondences)

alig_width = max([len(corr) for corr in correspondences])
if args.verbosity > 10:
    print("alig_width:", alig_width)

lang_lst = [itm.strip() for itm in args.languages.split(",")]
if args.verbosity > 10:
    print("lang_lst", lang_lst)

file_prefix = args.input.partition(".")[0]

for pos, lang in zip(range(alig_width), lang_lst):
    bfst = hfst.HfstBasicTransducer()
    for corr in correspondences:
        if len(corr) == 1:
            phoneme = corr
        else:
            phoneme = corr[pos:pos+1]
        pth = ((corr, phoneme),)
        bfst.disjunct(pth, 0.0)
    fst = hfst.HfstTransducer(bfst)
    fst.repeat_star()
    fst.minimize()
    outfilename = file_prefix + "2" + lang + ".fst"
    ostream = hfst.HfstOutputStream(filename=outfilename)
    fst.write(ostream)
    ostream.close
    
    if args.verbosity > 0:
        print(outfilename, "written")

        fst.invert()
    outfilename = lang + "2" + file_prefix + ".fst"
    ostream = hfst.HfstOutputStream(filename=outfilename)
    fst.write(ostream)
    ostream.close
    
    if args.verbosity > 0:
        print(outfilename, "written")
    
