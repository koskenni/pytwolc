=============================================
Open Finnish two-level morphological analyzer
=============================================

This article describes a plan and a project *OFITWOL* to build an open source two-level morphological analyzer for Finnish as it is described in *Nykysuomen Sanakirja* [NS]_.  During the past decades, several morphological analyzers have been built for Finnish, including

* FINTWOL, originally in [koskenniemi1983]_ and later developed int a commercial product by Lingsoft
* MORFO developed by Kielikone
* Mint by Olli Blåberg and later on adopted by Xerox into the XFST framework
* OMORFI by Tommi Pirinen using the HFST tools
* Voikko based on the Malaga platform



Goals
=====

The goals of OFITWOL are:

1. OFITWOL aims to be *descriptive* rather than normative.  In particular, it is intended to accept inflectional word forms which were used in the 20th century but which are rarely used any more.  Most other Finnish morphological analyzers are more normative and try to allow only those forms which sound unmarked today.  The normative approach has also been the guideline for describing the inflection in more recent dictionaries such as *Kielitoimiston sanakirja* or its predecessor *Suomen kielen perussanakirja*.

2. The building of OFITWOL aims to demonstrate the application of the *simplified two-level model* into building a full-scale morphological analyzer in order to validate the principles and methods and to make it easier for other projects to learn from the expriences of this project.

3. OFITWOL aims to be *flexible* enough to be adapted for various purposes including the analysis of literary and newspaper texts from the 19th and 20th centuries, using it in the description of Finnsh dialects and in the comparison of Finnish with those, Old Literary Finnish and with languages closely related to Finnish.

4. Adopt disciplined methods for creating *lexical entries* either from word-lists such as Nykysyomen sanalista, interactively using a human informant or assisted by corpus data.

5. *Document* the various components well enough so that other scholars can understand how it is built and how it can be modified and improved.  As much as possible, the steps and components are documented prior to their building.

6. Make all rules, lexicons, scripts and programs freely available and extensible so that they can be used for any purpose.

   
Existing language resources
===========================

1. The tables for inflected word forms for paradigms given in *Nykysuomen sanakirja* [NS]_ and in *Suomen kielen käänteissanakirja* [KSK]_ which reflect the same sets of defined inflection classes.  These two are used as a primary resource when determining the morphophonemic shapes of lexical entries.

2. Nykysuomen sanalista [NSSL]_ which is a word list with inflectional coded and can be used under the LGPL license.  The inflection codes in NSSL are those used in Kielitoimiston sanakirja.

3. Suomen kielen tekstipankki, which is a collection of several million words of Finnish texts and is stored in the Kielipankki.  The texts themselves cannot be included in the results but they may be used as a primary resouce of occurrences of word forms and thus for determining the inflectional properties of tentative lexical entries.  Some proofread newspaper texts from early 1900s are also available.

4. Helsinki Finite-State Transducer Tools (HFST) for building the further tools needed at various stages of the project.  The finite-state tools are used both as standalone programs and as embedded in Python 3.

5. An initial version of nominal and verbal affixes as a CSV table which can be used for producing LEXC lexicons for affixes of Finnish.


Overview of the stages
======================

1. Completing the paradigm tables and sets of word form examples.  Word forms in the tables are segmented so that morphs are separated from each other by a boundary.  Establishing the morphophonemes through alignment as is explained in :ref:`representations`.  This is done separately for nouns, (adjectives) and for verbs.  The result of this stage is a collection of examples as space-separated pair symbol strings.  The result is free.

2. Writing and testing the two-level rules as is explained in :ref:`discovery`, :ref:`formalism` and :ref:`compiling`.  The result of this stage is a two-level grammar which covers all relevant phoneme alternations of the language as they are present in the examples.  The result is free.  The tuning of the rules might result in some revisions in the sets of examples (such as correcting mistakes in the examples and adding missing examples).

3. Writing and testing regular expression patterns for NS/KSK inflection types as described in :ref:`lexguessing`.  The patterns can be tested against the KSK word list by converting the word list into a LEXC lexicon.  A script checks whether it covers the KSK vocabulary and reports items not covered.  The patterns are used for determining the underlying lexicon entry from a set of word forms.  The patterns may be complete in the above sense but still too permissive which results in too many possible lexical entries for sets of inflected word forms.  The patterns need to be made strict enough to exclude most of the extra entries.  This is achieved by making the patterns reflect the phonological patterns present in inflection classes.  The result of this stage is a set of patterns which can be used both for converting the KSK word list into a LEXC lexicon and for guessing lexicon entries from scratch or with the aid of a corpus.  The result is free.

4. Build a LEXC lexicon out of the verb, noun and adjective entries of KSK which together with the two-level rules is a morphological analyzer for Finnish.  The result of this stage is a CSV list giving each KSK verb, noun and adjective, a  two-level lexicon entry using morphophonemes associated with its base form and inflection code in KSK.  This result cannot be published as such, but it can be used for processing further results.  From this CSV file, the affixes and the two-level rules one produces a KSK morphological ananlyzator KSKTWOL1 in a straight-forward manner, and this is also project internal.  Note that KSKTWOL1 is not prepared to analyze compound words.

5. Use KSKTWOL1 against various corpora, e.g. NSSL, SKTP, lexeme inventory of OMORFI, in order to collect sets of (non-compound) lexeme entries which occur in them.  The restriction of KSKTWOL to such a subset is taken and closed class entries (pronouns, conjunctions, numerals) are added.  The results are of type OFITWOL1.  These are free lexicons (a seprarate one for each corpus) which can be published and combined according to needs.

6. Augment OFITWOL1 with a mechanism for compounding (two part compounds) resulting in OFITWOL2 (which is again free).  OFITWOL2 is used for collecting tentative sets of compound entries from corpora.  Compound words with a sufficient frequency are (after at least superficial human checking) added to the lexicon resulting in OFITWOL3 (which is free).

7. One can guess more entries by using the patterns as an entry guesser which uses a word form list out of a corpus.  This time it would be useful to use a word form list from which all word forms recognized by OFITWOL2 or OFITWOL3 have been removed.  
