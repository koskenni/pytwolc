==============================
Morphophonemic representations
==============================

In linguistics, we say that word forms consist of :term:`morphs <morph>`, which are sequences of :term:`phonemes <phoneme>` and which have a meaning, e.g.: a Finnish word form ``kaloja`` could be broken into three morphs::

  kalo - 'a fish' - KALA
  j    - plural
  a    - partitive

Another word form ``kalassa`` could be segmented as::

  kala - 'a fish' - KALA
  ssa  - inessive

Our goal is to find a common representation for morphs of the same :term:`morpheme`.  E.g. for ``kala`` and ``kalo`` we could establish a single form ``k a l {ao}`` which could serve as the lexical entry for the morpheme KALA, 'a fish'.

The :term:`morphophonemic representation` can be built from a table of segmented word forms by a set of scripts.  The process is mostly automatic but human intervention is needed in:

- collecting model words and arranging as a table with columns for different relevant forms and rows for different lexemes

- segmenting the word forms so that their morphs are separated e.g. with a period

- renaming the automatically produced raw morphophonemes

The process consists of four scripts:

1. ``paratab2segcsv.py`` which reads in a paradigm table of word forms and writes the data in a format where each word form is on line of its own.  Both the input table and the output file are in the CSV format.

2. ``segm2zerofilled.py`` which reads the data in one word form per line CSV format and aligns each morpheme and writes a CSV file augmented with the aligned i.e. zero-filled example word forms.  The :doc:`alignment` is accomplished by the ``multialign.py`` module, see :py:mod:`multialign`.

3. ``zerofilled2rawmphon.py`` which reads in the aligned example words and constructs a raw morphophonemic representation for each example word.  The construction is made according to a user given set of *principal forms* i.e. a subset of inflected forms.  If one knows the principal forms, one can mechanically produce all other inflected forms.

4. ``raw2named.py`` which renames some raw morphophonemes of the example word forms and writes a file of examples where each example is a line of blank separated string of :term:`pair symbols <pair-symbol>`.  Pair symbols are the newly renamed ones or if the raw symbol is not yet renamed, the pair symbol is the original raw one.

Assigning names to raw morphophonemes is usually done incrementally with the aid of ``twdiscov.py``, see :doc:`/twdiscov`.  The rule discovery module helps to identify similar raw morphophonemes and to give a common name to them.  One may also write a two-level rule for such tentatively final morphophoneme and test the validity of the rule using ``twol`` rule compiler.  See separate documents for them.
