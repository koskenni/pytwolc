import hfst

def expr(e):
    res = hfst.regex(e)
    res.minimize()
    return res

def concat(f, g):
    res = f.copy()
    res.concatenate(g)
    res.minimize()
    return res

def star(f):
    res = f.copy()
    res.repeat_star()
    res.minimize()
    return res

def plus(f):
    res = f.copy()
    res.repeat_plus()
    res.minimize()
    return res

def crossprod(f, g):
    res = f.copy()
    res.cross_product(g)
    res.minimize()
    return res

def compose(f, g):
    res = f.copy()
    res.compose(g)
    res.minimize()
    return res

def union(f, g):
    res = f.copy()
    res.disjunct(g)
    res.minimize()
    return res

def intersect(f, g):
    res = f.copy()
    res.conjunct(g)
    res.minimize()
    return res

def upper(f):
    res = f.copy()
    res.input_project()
    res.minimize()
    return res

def lower(f):
    res = f.copy()
    res.output_project()
    res.minimize()
    return res
