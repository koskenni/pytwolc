.. _differences:

==========================================
Differences between twol.py and hfst-twolc
==========================================

The simplified two-level morphology differs in several respects from the standard model as described in publications and as implemented in the TWOLC compiler by Karttunen and Beesley and later on in the HFST finite-state transducer tools, see e.g.  [karttunen1987]_.  There are changes in the formalism (i.e. syntax of expressions and rules) and there are some strongly recommended practises which the author of the rules are expected to follow:

.. index:: alphabet

1. The simplified model bases heavily on *examples*.  No rules can be written without a set of examples.  The examples are given as a sequences of of :term:`pair symbols <pair symbol>` such as::
     
     k a u p {pØ}:Ø {ao}:a s s {aä}:a

   The alphabet (morphophonemes or input symbols, surface phonemes or output symbols and the set of allowed symbol pairs) is deduced from the examples.  The twol.py compiler neither needs nor accepts alphabet or character set definitions.

2. The *lexical* (or morphophonemic or upper) *level* consists of phonemes and morphophonemes.  By convention, morphophonemes clearly indicate what phonemes are alternating in that position and by convention, they are denoted by symbols in braces, e.g. ``{aä}`` stands for a morphophoneme which can be realized on the *surface level* either as an ``a`` or as an ``ä``.

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
       


