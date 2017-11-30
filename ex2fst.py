import hfst, twex, argparse

arpar = argparse.ArgumentParser("python3 ex2fst.py")
arpar.add_argument("-e", "--examples", help="name of the examples file",
                   default="examples.pairstr")
arpar.add_argument("-o", "--output",
                    help="name of the fst file to be written",
                    default="examples.fst")
arpar.add_argument("-v", "--verbosity",
                   help="level of  diagnostic output",
                   type=int, default=0)
args = arpar.parse_args()

twex.read_examples(filename=args.examples)

print("--- all examples read from ", args.examples ," ---")

exfile = hfst.HfstOutputStream(filename=args.output)
exfile.write(twex.EXAMPLES)
exfile.flush()
exfile.close()

print("--- example fst written to ", args.output ," ---")
