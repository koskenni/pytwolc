# pytwolc
Experimental two-level rule compilation using Python HFST. For more information, see https://github.com/hfst/python


## Rule compiler: twol.py

The Python program `twol.py` is a rule compiler and tester for rules of simplified two-level model, see https://pytwolc.readthedocs.io/en/latest/formalism.html for more information on the rule formalism and the compiler.  The HST package can be loaded using the command:

  $ python3 -m pip install hfst

The program twol.py uses and depend on the 'tatsu' Python parser generator by Juancarlo Añez, seee http://tatsu.readthedocs.io/en/stable/index.html for detailed documentation. You can load and install TaTsu from the net using a command:

   $ python3 -m pip install tatsu

The compiler needs two files: (1) examples as a FST and (2) a rule file.  The human readable examples must be converted into a FST using `twexamp.py` program.

The compiler is normally executed as follows:

  $ python3 twol.py examples.fst rules.twolc

One can get more information by using the `--help` parameter.  More documentation on twol.py can be found at https://pytwolc.readthedocs.io/en/latest/compiletest.html

## Converting examples from pair string format into a FST: twexamp.py

The module `twexamp.py` handles various tasks for the compiler during the compilation process.  It is also needed for converting human readable examples into a FST so that ti is not necessary recompile it at every step of testing rules.  A recompilation is only needed when the examples are changed.  In order to convert examples from a pair string format into a fst you can e.g.:

  $ python3 twexamp.py examples.pstr examples.fst


## Morphophonemic representations

The sequence of programs `parad2words.py`, `words2zerofilled.py`, `zerofilled2raw.py` and `raw2named.py` is intended for determining the underlying or morphophonemic representations for word stems.  It starts from a table of word forms or paradigms where morphs are separated from each other e.g. by a period (`.`).  See https://pytwolc.readthedocs.io/en/latest/morphophon.html for more information on their use.  Each program is run from the command line, and one can get detailed information on the parameters by running the command with a `--help` argument, e.g.

  $ python3 words2zerofilled.py --help

Some of the programs of this sequence need the package `orderedset` which one can get from the net by

  $ python3 -m pip install orderedset


## Discovering raw rules: twdiscov.py

This program builds tentative or raw rules out of a set of examples.  The examples must be given one example per line as a space-separated list of symbol pairs.  See https://pytwolc.readthedocs.io/en/latest/twdiscov.html for more information.
