===============================
Discovering raw two-level rules
===============================

The ``twdiscov.py`` program reads in a set of two-level examples which consist of space-separated pair symbols and the program produces a tentative two-level rules for all morphophophpnemes in the examples or just for a given morphophoneme.  The method is based on producing positive and negative examples which are specific to one morphophoneme.  The positive examples consist of the examples which contain the morphophoneme being processed.  The negative examples are made from the positive ones by distorting the occurrences of the morphophoneme.

The initial set of context is made out of the examples as such.  Such a rule trivially accepts all examples and rejects all negative examples.  The idea of the algorithm is to shorten the contexts step by step.  The shorter contexts always accept the positive examples but the do not necessarily reject the negative ones.  As long as they do, the process goes on.  One side is shortened first and then the other.

The program suggests reasonable raw rules for phenomena where the condition is strictly local, e.g. stem-final vowel alternations and also for consonant gradation in Finnish.  On the other hand, e.g. vowel harmony cannot be summarized properly by this method.  (There will be a long list of contexts which would not work for other instances which are not present in the set of examples.)

The program only produces ``=>`` and ``/<=`` types of rules.  This is not a limitation which would restrict the phenomena which can be expressed.  Indeed, if some phenomena are even partly optional, the use of just these two types of rules makes it easy to allow variation.

Enven in the best case, the rules can be as good as the set of examples. If the examples are chosen in a disciplined and balanced manner, the program is expected to be useful and practical.  If alternations are only partly present in the set of examples, the proposed raw rules will be poor and may even be misleading.

The set of examples is given to the program as a file of lines with a sequence of space separated pair symbols, e.g. as the following::
  
  a r k {kØ}:k u
  a r k {kØ}:Ø u n

The program collects the input and the output alphabets and the allowed symbol pairs from the examples, thus no other definitions are needed.


Functions of the ``twdiscov`` module
====================================

.. automodule:: twdiscov
   :members:
