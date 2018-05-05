
.. _pytwol-glossary:


========
Glossary
========

.. glossary::

   morph
     A part of the surface form which is said to correspond to a morpheme, e.g. in ``kadulla`` the part ``kadu`` (street) and the part ``lla`` (on) are morphs.

   morpheme
     A minimal unit with a meaning and which is manifeseted as morphs, e.g. we may have a morpheme ``KATU`` which has a meaning 'street' and is manifested as two possible morphs ``katu`` and ``kadu``.  E.g. stems of words may be morphemes as well as various affixes for inflection and derivation.  Some stems combine two or more morphemes, e.g. compounds and derived lexemes.

   input symbol
     In general, input symbols are the symbols that a FST reads in.  In two-level rules and examples, the input symbols belong to the underlying representation and they may be either phonemes or morphophonemes.  The input symbols in two-level rules and examples are sometines also called *lexical characters* or *upper characters*.

   output symbol
     In general, output symbols are the symbols that a FST writes as output.  In two-level rules and examples, the output symbols are the phonemes in actual word forms (or letters in a near phonemic writing system).  Output symbols are sometimes called *surface characters* or *lower characters*.

   surface symbol
     Surface symbols are phonemes or the symbols which are used to write word forms.  For two-level rules, surface symbols are output-symbols.

   morphophoneme
     An abstract symbol which denotes the alternation of surface characters in a position within a morpheme. E.g. ``{td}`` could denote the alternation between ``t`` and ``d``.  The names of the morphophonemes are chosen by the linguist who writes a two-level grammar.  Morphophonemes are always input-symbols to the two-level rules.

   zero
     A placeholder which indicates that in some other allomorphs there is some phoneme in this position.  By inserting zeros, one makes the allomorphs same length.  Zero is not a morphophoneme and it never occurs in morphophonemic representations.

   morphophomenic representation
     An abtract representation which is a kind of summary of the concrete surface morphs.  Two-level rules describe the relation between the lexical and the surface level.  Corresponds to the sequence of *input symbols* of two-level rules.  The morphophonemic representation is sometimes also called the *lexical level* or the *upper level*.

   surface representation
     The concrete representation of of word forms as a sequence of phonemes or letters (possibly with some zeros inserted).

   alignment
     The process of making allomorphs equal length and make them to correspond each other phoneme by phoneme.  Alignment consists of adding zero symbols as needed so that the phonemes in the same position are phonologically similar.  Onc could align, e.g. ``

   raw morphophoneme
     A combination of phonemes which correspond to each other as a result of alignment, e.g. if ``käsi``, ``käde``, ``käte``, ``käs`` and ``kät`` are aligned, we get raw morphophonemes such as ``kkkk`` or ``sdtst``.  Raw morhpphonemes are usually renamed to morphophonemes, e.g. ``k`` or ``{tds}``

   deletion
     Deletion is said to occur when a phoneme in a in a morph corresponds to zero in another morph of the same morpheme.  Cf. epenthesis.

   epenthesis
     Epenthesis is said to occur when a zero in a morph corresponds to a phoneme in another morphp of the same morpheme.  In the simplified two-level framework, epenthesis and deletion are equivalent. 

   symbol-pair
     A tuple consisting of an input and an output symbol, e.g. ``({aä}, a)``

   pair-symbol
     A string consisting either of an output symbol, e.g. ``a``, or an input symbol followed by a colon followed by an output symbol, e.g. ``{aä}:a``

   encoded FST
     A FST can be converted into an equivalent FSA by changing all its transition labels so that the new labels are combinations of the original input and output labels using functions *fst_to_fsa*.  If the original FST contained a transition ``{aä}:a`` then the encoded FSA will have a transition ``{aä}^a:{aä}^a``.  An encoded FSA can be made back to a normal FST by the function *fsa_to_fst*.  See the HFST documentation 

     
