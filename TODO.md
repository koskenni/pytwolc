Possible things to do
=====================

- Compiling each context separately so that one may use expressions combining contexts and their negations. (Straight forward)

- Writing the compiled rules into a file as HFST sequence of transducers. (Trivial)

- Testing rules stepping one character at time in order to be able to report an exact location of a failure. (Straight forward using the HfstBasicTransducer representation)

- Discovering rule contexts automatically. The set of morphophonemes needing a rule is implied by the alignment. An initial set of contexts is implied by the positive examples. Negative examples serve as a criterion for generalising the initial contexts by shortening and collapsing them. (Experiments and testing is needed.)

- Compiling two-level rule contexts and centres into Python regular expressions. (Trivial for the simple rules, progressively complicated for complex rules)

- Implementing the fully separate compilation of rules and the two-level harmonisation of rule alphabets (which is distinct from the harmonisation of standard HFST transducers). Principle is understood. Straight forward to implement using HfstBasicTransducer representation. Not necessary for the other tasks.

Already done
============

- Implementing the rule which forbids occurrences (/<=) was missing in the Python HFST library. (Feb 2017)

- Parsing two-level grammars using the PLY parser generator. Expressions are parsed and syntax checked which provides better diagnostics of syntax errors. Syntactically correct expressions are compiled with hfst.regex() and the compiled FSTs are combined into rule FSTs via hfst.rules.restriction() and hfst.rules.surface_coercion(). (Nov 2016)

- Creating the set of negative examples out of the positive examples, and testing the rules against them. (Nov 2016, revised Mar 2017)

- Testing the compiled rules against the set of positive examples (Oct 2016)

- Using the HFST two-level rule compilation functions in Python (and the XreCompiler and definitions) in conjunction with a set of examples (Oct 2016)
