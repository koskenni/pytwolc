.. _lexguessing:

========================
Guessing lexicon entries
========================

Here we assume that we already know quite a lot of the morphology and phonology of a language.  It is logical to first study the phonological alternations and the combining of affixes with a smaller set of examples.  Using such examples, we can construct the morphophonological representations that are needed for lexicon entries, see :ref:`representations` and :ref:`compiling`.

Populating the lexicon with enough adequate lexeme entries may often be a laborious task.  A native speaker might be able to inflect any given base form of a lexeme.  Many human-readable dictionaries provide numerical or other codes of :term:`inflection classes <inflection class>` for headwords or :term:`lemmas <lemma>`.  Such a code defines (more or less precisely) how the word must be inflected.  But, very few speakers can correctly give the inflection code for a given word.

This section discusses and presents methods for creating lexicon entries in two ways: (1) interactively in a dialogye between a speaker of the language and a program that is aware of the rules of morphophonemic alternations and inflectional patterns, and (2) blindly or in a batch mode combining the inflectional information with the occurrences of word forms in a large corpus.  Both approaches are based on regular expression patterns which describe the constraints that determine what shapes words in each inflection class may have.

Human-readable dictionaries often use quite large numbers of distinct inflection classes, e.g. Nykysuomen sanakirja (Dictionary of Modern Standard Finnish) uses 82 classes for nominal inflection and 45 for verbs.  The high numbers of classes comes from two independent factors: (a) stem final alternations (which depend on the shape of the end of the stem) and (b) constraints for affixing different allomorph endings (which depend on the syllable structure).


Patterns for inflection classes
===============================



Compiling a guessing FST
========================



Interactive guessing
====================



Batch guessing with a corpus
============================

