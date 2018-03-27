==========================
Simplified two-level model
==========================

------------------------
Changes since hfst-twolc
------------------------

The simplified two-level morphology differs in a few respects from the standard model as described in publications and as implemented in the
TWOLC compiler by Karttunen and Beesley and later on in the HFST finite-state transducer tools, see e.g.  [karttunen1987]_ The differences consist of:

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
       
       

------------------------------------------------
Rule formalism in the simplified two-level model
------------------------------------------------

The simplified two-level grammar consists of one or more lines where a line may be either a definition or a rule.  In addition there may be comment lines or empty lines neither of which are ignored when the grammar is compiled.

Definitions
===========

A definition assigns a name for a regular two-level expressionn.

.. warning:: The program may tilt!
	     But it was ignored

.. note:: this was different in hfst-twolc
	  at least probably so.


--------
Glossary
--------

.. _glossary:

.. glossary::

   morph
     A part of the surface form which is said to correspond to a morpheme, e.g. in ``kadulla`` the part ``kadu`` (street) and the part ``lla`` (on) are morphs.

   morphophoneme
     An abstract symbol which denotes the alternation of surface characters in a position within a morpheme. E.g. ``{td}`` could denote the alternation between ``t`` and ``d``.  The names of the morphophonemes are chosen by the linguist who writes a two-level grammar.

   zero
     A placeholder which indicates that in other allomorphs there is some phoneme in this position.  By inserting zeros, one makes the allomorphs same length.  Zero is not a morphophoneme and it never occurs in morphophonemic representations.

   morphophomenic representation
     An abtract representation which is a kind of summary of the concrete surface morphs.  Two-level rules describe the relation between the lexical and the surface level.  Corresponds to the *lexical level* of two-level rules.

   surface representation
     The concrete representation of of word forms as a sequence of phonemes or letters (possibly with some zeros inserted).

   alignment
     The process of making allomorphs equal length and make them to correspond each other phoneme by phoneme.  Alignment consists of adding zero symbols as needed so that the phonemes in the same position are phonologically similar.

   deletion
     Deletion is said to occur when a phoneme in a in a morph corresponds to zero in another morph of the same morpheme.  Cf. epenthesis.

   epenthesis
     Epenthesis is said to occur when a zero in a morph corresponds to a phoneme in another morphp of the same morpheme.  In the simplified two-level framework, epenthesis and deletion are equivalent. 

----------
References
----------

.. [karttunen1987] Lauri Karttunen and Kimmo Koskenniemi and Ronald M. Kaplan, 1987: "A compiler for two-level phonological rules", in M. Dalrymple, R. Kaplan, L. Karttunen, K. Koskenniemi, S. Shaio and M. Wescoat, editors, *Tools for Morphological Analysis*, pp. 1-61, Center for the Study of Language and Information, Stanford University, Vol. 87-108, CSLI Reports, Palo Alto, California, USA


..
    bibliography:: kmkbib.bib
