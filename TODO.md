Possible things to do
=====================

- Writing the compiled rules as HFST sequence of transducers

- Compiling two-level rule contexts and centres into Python regular expressions

- Testing rules stepping one character at time in order to be able to report an exact location of a failure

- Discovering rule contexts automatically

- Implementing the fully separate compilation of rules and the two-level harmonisation of rule alphabets (which is distinct from the harmonisation of standard HFST transducers)

Already done
============

- Parsing two-level grammars using the PLY parser generator. Expressions are parsed and syntax checked which provides better diagnostics of syntax errors. Syntactically correct expressions are compiled with hfst.regex()

- Creating the set of negative examples out of the positive examples, and testing the rules against them

- Testing the compiled rules against the set of positive examples (Oct 2016)

- Using the HFST two-level rule compilation functions in Python (and the XreCompiler and definitions) in conjunction with a set of examples (Oct 2016)
