"""fs.py: A wrapper module for basic finite-state operations

The HFST engine used for accomplishing the operations but all functions make copies of their arguments when it is necessary to avoid side-effects.

© Kimmo Koskenniemi, 2018. This is free code under the GPL 3 license."""

import hfst

def expr(e):
    """Return an FST corresponding to a XFST regular expression"""
    res = hfst.regex(e)
    res.minimize()
    return res

def concat(f, g):
    """Return the concatenation of two FSTs"""
    res = f.copy()
    res.concatenate(g)
    res.minimize()
    return res

def star(f):
    """Return the Kleene star iteration of an FST"""
    res = f.copy()
    res.repeat_star()
    res.minimize()
    return res

def plus(f):
    """Return the Kleene plus iteration of an FST"""
    res = f.copy()
    res.repeat_plus()
    res.minimize()
    return res

def crossprod(f, g):
    """Return the cross-product of two FSAs"""
    res = f.copy()
    res.cross_product(g)
    res.minimize()
    return res

def compose(f, g):
    """Return the composition of two FSTs"""
    res = f.copy()
    res.compose(g)
    res.minimize()
    return res

def union(f, g):
    """Return the union of two FSTs"""
    res = f.copy()
    res.disjunct(g)
    res.minimize()
    return res

def intersect(f, g):
    """Return the intersection of two FSTs

Both arguments are assumed to be length preserving mappings.
"""
    res = f.copy()
    res.conjunct(g)
    res.minimize()
    return res

def upper(f):
    """Return the input projection of an FST"""
    res = f.copy()
    res.input_project()
    res.minimize()
    return res

def lower(f):
    """Return the output projectio of an FST"""
    res = f.copy()
    res.output_project()
    res.minimize()
    return res
