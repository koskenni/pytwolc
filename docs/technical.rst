==============================================================
How the two-level rule compilation and testing was implemented
==============================================================

See also  :ref:`pytwol-glossary` and [karttunen1987]_.

---------------------------
Parsing the two-level rules
---------------------------


-----------------------------
Compiling the two-level rules
-----------------------------

Each rule is compiled separately using the alphabet extracted from the fst containing the examples. The result of the compilation consists of a tuple of three FSTs:

- *rule_fst* which accepts any examples which conform to the rule.  The *rule_fst* accepts strings of symbol pairs.  All rules ought to accept all correct examples as symbol pair strings.

- *selector_fst* produces the relevant subset of the examples when intersected with *examples_fst*.  The selector is needed only for testing that the rule accepts all relevant positive examples.  The point is that not all examples are relevant for testing.  If an example does not contain the center (or the input part of the center) of a rule, the rule accepts such an example anyway.  The author of a rule gets no information if such an acceptance is reported.

- *scrambler_fsa* which is an encoded FSA which transforms a positive example into a negative example which ought to be rejected by the rule (and is also needed only for the testing of the rule).  The purpose of scrambling is to alter the output symbol in order to produce occurrences in wrong places for right-arrow rules or wrong correspondences in a context for left-arrow rules.

Compilation of the rule FST
===========================

Constructing the selector_fst
=============================

Constructing the scrambler_fsa
==============================

Let us suppose we have a rule: ``{ao}:o => _ {ij}: ;``  and an example::

  k a l {ao}:a s s {aä}:a

In order to produce negative examples for this rules, we have to change occurrences of ``{ao}:o`` into ``{ao}:a`` at least in one place of an example, e.g.::

  k a l {ao}:o s s {aä}:a

In order to make such changes, the original examples are encoded as FSAs where the original input and output symbols are separated by a '``^``'::

  k^k a^a l^l {ao}^a s^s s^s {aä}^a

Such sequences can be converted with appropriate FSTs if its input symbols are pairs (such as ``k^k`` or ``{ao}^a``).  In order not to lose information, the output symbols have to be similar pairs.

