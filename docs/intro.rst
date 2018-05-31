==========================
Simplified two-level model
==========================

.. warning:: The PYTWOL program is still under development and so is this documentation

The morphological two-level model dates back to [koskenniemi1983]_ and
is characterized by the descritpion of phonological or
morphophonological alternations as a direct relation between the
surface forms and their underlying lexical or morphophonemic forms.
It differs from the classical generative phonology by explaining the
alternations using parallel rules rather than as a cascade of
successive rules, see [karttunen1993]_ for a demonstration of this
difference.

------------
Overall plan
------------

Various methods and programs programs have been developed in order to simplify the whole process of creating a morphological two-level grammar.  It can be summarized using the following steps:

1. A linguist selects a representative set of example words.

2. The linguist marks the morph boundaries in the example words.

3. A program aligns the morphs in the examples by adding zero symbols.  The zero-filled morphs are the same length and phonemes in corresponding positions are phonologically similar.

4. A program produces example words as sequences of pair-strings where the left component of each pair is a raw morphophoneme implied by the alignment.  This is the initial version of the example file for designing and testing rules.

5. Using a version of the example file, one selects one morphophoneme at a time and:

   a. Lets a program produce tentative raw two-level rules for the morphophoneme.

   b. The linguists renames the raw morphophoneme and possibly merges it with some similar raw morphophonemes, and thus produces a revised version of the example file.

   c. The linguist tunes the raw two-level rule into a more general version when there appears to be need.

   d. A program compiles the rule and produces a set of positive and a set of negative test cases.  The program checks that all positive examples pass the rule and that all negative examples are rejected.  The program reports any failures.

   e. If all tests passed for this morphophoneme, proceed to the next morphophoneme.  If rejected positive or accepted negative examples were reported, check and revise the rules (or possibly the examples) and repeat from step (c).

When the process is complete, we have a set of two-level rules which accept all our examples and probably a large set of other word forms with similar morphophonemic alternatilns.



------------------------
Changes since hfst-twolc
------------------------

The simplified two-level morphology differs in a few respects from the standard model as described in publications and as implemented in the
TWOLC compiler by Karttunen and Beesley and later on in the HFST finite-state transducer tools, see e.g.  [karttunen1987]_.

.. note:: If you are not familiar with those earlier versions, you may skip this section and continue from :ref:`examples`.

The simplified two-level model differs from the standard model in the follwing respects:

1. The *lexical* (or morphophonemic or upper) *level* consists of phonemes and morphophonemes.  By convention, morphophonemes clearly indicate what phonemes are alternating in that position and by convention, they are denoted by symbols in braces, e.g. ``{aä}`` stands for a morphophoneme which can be realized on the *surface level* either as an ``a`` or as an ``ä``.

2. The simplified model bases heavily on *examples*.  No rules can be written without a set of examples.  The examples are given as a sequences of of symbol pairs such as::
     
     k a u p {pØ}:Ø {ao}:a s s {aä}:a
     
.. index:: deletion

3. *Deletion* and *epenthesis* are not treated as epsilons.  Instead, a deletion is represented as a concete *zero symbol*, e.g. ``Ø`` on the surface level.  The corresponding lexical symbol is then a morphophoneme, e.g. ``{pØ}``.  In the lexical representations, epenthesis is also represented as a morphophoneme, e.g. as ``{Øh}`` if, in the surface forms, an ``h`` alternates with nothing according to the context.  In such cases, the surface form of the examples has a zero ``Ø`` in that position.  Different surface allomorphs are made equally long by inserting zeros as needed.

.. index:: HFST, hfst-twolc
   pair: rule; compiler

4. *Rule formalism* is different and there is a different compiler written in Python and using the embedded HFST finite-state tools.
   
   .. index:: alphabet
   
  a. *Alphabet* is not declared in the grammar.  The set of lexical and surface symbols and the set of feasible pairs is extracted from the examples.
     
     .. index:: sets
     
  b. There is no separate way for declaring *sets of symbols*.  They are handled in a concise way by definitions.
     
     .. index:: definitons
     
  c. Definitions are identified just by an equal sign, (i.e. no heading for definitions), e.g.::
       
       Glide = {ij}: | j ;
       
  d. Rules have no *titles*.  The left-hand side serves as the identification, e.g.::
       
       {ij}:j <=> SurfVowel _ SurfVowel ;
       
  e. There is a separate rule *for each morphophoneme* or sometimes a couple of rules.
     
     .. index::
	pair: conflict; detection
	pair: conflict; resolution
	
  f. Neither *conflict detection* nor *conflict resolution* exists.  They are not needed because each morphophoneme gets a rule of its own.  There is no point in merging contexts of separate rules.
     
     .. index::
	pair: curly; braces
	
  g. Some restrictions in the regular pair expressions: Curly braces ``{}`` are ordinary characters and they are used in morphophonemes without quotation.  Some operators may be missing.

  h. Rules may have several contexts but contexts are *separated by a comma* instead of a semicolon, e.g.::
       
       {ij}:i => SurfCons _ , _ SurfCons ;
       


.. _examples:

-----------------------------------
Examples as strings of pair symbols
-----------------------------------

The simplified two-level model is heavily based on examples which are selected and edited before any rules are considered and before one starts to write the first rule.  The set of examples defines the possible correspondences or possible phoneme alternations; even the possible surface symbols and the set of morphophonemes is defined implicitly by the set of examples.

The examples are given as a file where each line is a string of *pair symbols*, e.g.::

  k a t {tØ}:Ø o l l {aä}:a

Here we have eight pair symbols, six of them are abbreviations, e.g. ``k`` stands for ``k:k`` and ``a`` for ``a:a``.  The remaining two pair symbols consist each of two symbols: a morphophonemic symbol ``{tØ}`` or ``{aä}`` combined with a surface symbol ``Ø`` or ``a``.  Another way of representing the examples would be them on two rows::

  k  a  t {tØ} o  l  l  {aä}
  k  a  t   Ø  o  l  l   a

The upper line is the morphophonemic representation of the example word form, and the lower line is the surface representation of it.  Note that in the examples, the two representations always are of the same length and a zero symbol (Ø) is inserted when necessary.  In the above example, the ultimate surface form consists of only seven sybols: ``k a t o l l a``.  Within the examples and in the rules, these zeros always expliciltly present.

There is yet another form in which the examples are represented, i.e. as a pair of strings and then the strings are given without spaces, e.g.::

  ka{tØ}oll{aä}:katØolla

One can readily see that the three ways to represent examples are equivalent.  Examples are edited as a text file, but for further processing, they are compiled into a FST using the ``ex2fst`` module.


.. _rule-formalism:

------------------------------------------------
Rule formalism in the simplified two-level model
------------------------------------------------

The simplified two-level grammar consists of one or more lines where each line may be either a *definition*, a *rule* or just a *comment*.  Definitions and rules are made out of *regular two-level expressions*.  Comment lines or empty lines are ignored when the grammar is compiled into finite-state transducers (FSTs).  Comment lines start with an exclamation mark (!) at the first non-blank column, e.g.::

  ! trisyllabic word structure
 
Regular two-level expressions
=============================

The set of possible symbol pairs comes from the set of previously edited examples.  The rules and the two-level regular expressions introduce no correspondences beyond those which occur in the examples.

The two-level regular expressions (TLREs) can be:



Definitions
===========

A definition assigns a name for a regular two-level expressionn.

.. warning:: The program is under development and it may tilt!


----------
References
----------

.. [koskenniemi1983] Kimmo Koskenniemi, 1983,
		     *Two-level Morphology: A General Computational
		     Model for Word-Form Recognition and Production*,
		     University of Helsinki, Department of General Linguistics,
		     Publications, Number 11.  160 pages.

.. [karttunen1987] Lauri Karttunen and Kimmo Koskenniemi and
		   Ronald M. Kaplan, 1987:
		   "A compiler for two-level phonological rules",
		   in M. Dalrymple, R. Kaplan, L. Karttunen,
		   K. Koskenniemi, S. Shaio and M. Wescoat, editors,
		   *Tools for Morphological Analysis*, pp. 1-61,
		   Center for the Study of Language and Information,
		   Stanford University, Vol. 87-108, CSLI Reports,
		   Palo Alto, California, USA.

.. [karttunen1993] Lauri Karttunen, 1993: "Finite-state Constraints",
		   in *Proceedings of the International Conference on
		   Current Issues in Computational Linguistics*, June
		   10-14, 1991.  Universiti Sains Malaysia, Penang,
		   Malaysia, pp. 173-194.

.. [koskenniemi2013b] Kimmo Koskenniemi, 2013: "Finite-state relations
		      between two historically closely related
		      languages" in *Proceedings of the workshop on
		      computational historical linguistics at NODALIDA
		      2013*, May 22-24, 2013, Oslo, Norway, NEALT
		      Proceedings Series 18, number 87, pages 53-53,
		      Linköping University Electronic Press, ISSN
		      1650-3740,
		      http://www.ep.liu.se/ecp/article.asp?issue=087\&article=004

.. [koskenniemi2017] Kimmo Koskenniemi, 2017: "Aligning phonemes using
                  finte-state methods", in *Proceedings of the 21st
                  Nordic Conference on Computational Linguistics*,
                  May, 2017, Gothenburg, Sweden, Association for
                  Computational Linguistics, pages 56-64,
                  http://www.aclweb.org/anthology/W17-0207

..
    bibliography:: kmkbib.bib
