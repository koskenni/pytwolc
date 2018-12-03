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

Each inflection class can be described with one or more *patterns*.  Patterns are written as a CSV file, i.e. a table with a few columns:

    CONT
        Continuation class from which the affixes can be attached to the stems described by this pattern.  The continuation is the same thing as in LEXC entries.

    ICLASS
        Inflection class, e.g. the number used in a dictionary.

    MPHON
        A pattern which describes the lexicon entries may belong to this class (ICLASS).  The pattern resembles LEXC lexicon entries.  The pattern may be either a regular expression ``<...>`` or a single exceptional lexeme.  The regular expressions follow the XFST syntax used in LEXC except that curly braces ``{}`` are reserved for names of morphophonemes where they are not quoted with a percent sign ``%``, thus e.g. ``a:{ao}`` is just a symbol pair.  The input side of regular expressions is the base form of lexemes and the output side is the morphophonemic representation.  Epsilons **0** may be used when something in the base-form corresponds to nothing in the morphophonemic representation and vice versa.  (Be careful not to mix zero symbols ``Ø`` and epsilons **0**.  Remember that the zero symbol occurs olny as a part of morphophonemes, e.g. ``a:{aØ}`` in these patterns, never by itself)

    COMMENT
        Comments do not affect the results but they are otherwise useful for the developer or maintainer of the patterns.


Regular expressions may consist of concatenation, Kleene star and plus, brackets for grouping, parenthesis for optionality, disjunction and intersection.  In particular, one may define expressions and use them in other definitions or patterns.  In the first column of a definition is a keyword ``Define``, in the second column is the name of the defined expression, and in the third column is the expression.

Compiling a guessing FST
========================



Interactive guessing
====================



Batch guessing with a corpus
============================

