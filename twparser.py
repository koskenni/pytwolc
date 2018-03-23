# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import sys, re, json
from codecs import open
from pprint import pprint

import tatsu
from tatsu.ast import AST
from tatsu.walkers import NodeWalker

from tatsu.exceptions import ParseException, FailedParse, ParseError, FailedSemantics

import cfg, hfst
import twexamp

class TwolRegexSemantics(object):

    def define(self, ast):
        cfg.definitions[ast.left] = ast.right
        return ("=", ast.left, ast.right)
    
    def identifier(self, ast):
        string = ast.token.strip()
        return string

    def right_arrow_rule(self, ast):
        result = ("=>", ast.left, ast.right)
        return result

    def left_arrow_rule(self, ast):
        result = ("<=", ast.left, ast.right)
        return result

    def double_arrow_rule(self, ast):
        result = ("<=>", ast.left, ast.right)
        return result

    def exclusion_rule(self, ast):
        result = ("/<=", ast.left, ast.right)
        return result

    def context_lst(self, ast):
        result = ast.left.extend(ast.right)
        return result

    def context(self, ast):
        lc = ast.left if ast.left else ""
        rc = ast.right if ast.right else ""
        result = [(lc, rc)]
        return result

    def union(self, ast):
        return "[{} | {}]".format(ast.left, ast.right)

    def intersection(self, ast):
        return "[{} & {}]".format(ast.left, ast.right)

    def difference(self, ast):
        return "[{} - {}]".format(ast.left, ast.right)

    def concatenation(self, ast):
        return "[{} {}]".format(ast.left, ast.right)

    def composition(self, ast):
        return "[{} .o. {}]".format(ast.left, ast.right)

    def crossproduct(self, ast):
        return "[{} .x. {}]".format(ast.left, ast.right)

    def Kleene_star(self, ast):
        return "[{}]*".format(ast.expr)

    def Kleene_plus(self, ast):
        return "[{}]+".format(ast.expr)

    def Upper(self, ast):
        return "[{}].u".format(ast.expr)

    def Lower(self, ast):
        return "[{}].l".format(ast.expr)

    def One_but_not(self, ast):
        return r"[PI - [{}]]".format(ast.expr)

    def optexpression(self, ast):
        return "({})".format(ast.expr)

    def subexpression(self, ast):
        return "[{}]".format(ast.expr)

    def symbol_or_pair(self, ast):
        string = ast.token.strip()
        failmsg = []
        pat = re.compile(r"""^
        (?P<up>[a-zšžåäöüõA-ZÅÄÖ0-9]*
         |
         \{[a-zåäöüõA-ZÅÄÖØ]+\})
        :
        (?P<lo>[a-zšžåäöüõA-ZÅÄÖØ]*)
        $""", re.X)
        m = re.match(pat, string)
        if m:                       # it is a pair with a colon
            up = m.group("up")
            up_quoted = re.sub(r"([{}])", r"%\1", up)
            lo = m.group("lo")
            if up and (up not in cfg.input_symbol_set):
                failmsg.append("input symbol '{}'".format(up))
            if lo and (lo not in cfg.output_symbol_set):
                failmsg.append("output symbol '{}'".format(lo))
            if up and lo and ((up, lo) not in cfg.symbol_pair_set):
                failmsg.append("symbol pair '{}'".format(string))
            if failmsg:
                cfg.error_message = " and ".join(failmsg) + " not in alphabet"
                raise FailedSemantics(cfg.error_message)
            elif up and lo:         # it is a valid pair with a colon
                return "{}:{}".format(up_quoted, lo)
            elif up and (not lo):
                return "[{} .o. PI]".format(up_quoted)
            elif (not up) and lo:
                return "[PI .o. {}]".format(lo)
            else:
                return "PI"
        m = re.fullmatch(r"[a-zåäöüõA-ZÅÄÖØ]+", string)
        if m:                       # its either a defined sym or a surf ch
            if string in cfg.definitions:
                return "{}".format(string)
            elif (string in cfg.output_symbol_set) and (string in cfg.input_symbol_set):
                return "{}:{}".format(string, string)
            elif string in {'BEGIN', 'END'}:
                return string
        cfg.error_message = "'" + string + "' is an invalid pair/definend symbol"
        raise FailedSemantics(cfg.error_message)

class TwolFstSemantics(object):

    def define(self, ast):
        expr_fst = ast.right.copy()
        def_name = ast.left
        cfg.definitions[def_name] = expr_fst
        return ("=", ast.left, ast.right)
    
    def identifier(self, ast):
        string = ast.token.strip()
        return string

    def right_arrow_rule(self, ast):
        result = ("=>", ast.left, ast.right)
        return result

    def left_arrow_rule(self, ast):
        result = ("<=", ast.left, ast.right)
        return result

    def double_arrow_rule(self, ast):
        result = ("<=>", ast.left, ast.right)
        return result

    def exclusion_rule(self, ast):
        result = ("/<=", ast.left, ast.right)
        return result

    def context_lst(self, ast):
        left_lst = ast.left.copy()
        right_lst = ast.right.copy()
        result = left_lst.copy()
        result.extend(right_lst) ## why this does not work?
        #result[len(result):len(result)] = right_lst
        return result

    def context(self, ast):
        lc = ast.left.copy() if ast.left else hfst.epsilon_fst()
        rc = ast.right.copy() if ast.right else hfst.epsilon_fst()
        #print(lc)###
        #print(rc)###
        result = [(lc, rc)]
        return result

    def union(self, ast):
        result = ast.left.copy()
        result.disjunct(ast.right)
        result.minimize()
        return result

    def intersection(self, ast):
        result = ast.left.copy()
        result.conjunct(ast.right)
        return result

    def difference(self, ast):
        result = ast.left.copy()
        result.minus(ast.right)
        return result

    def concatenation(self, ast):
        result = ast.left.copy()
        result.concatenate(ast.right)
        result.minimize()
        return result

    def composition(self, ast):
        result = ast.left.copy()
        result.compose(ast.right)
        return result

    def crossproduct(self, ast):
        result = ast.left.copy()
        result.cross_product(ast.right)
        return result

    def Kleene_star(self, ast):
        result = ast.expr.copy()
        result.repeat_star()
        result.minimize()
        return result

    def Kleene_plus(self, ast):
        result = ast.expr.copy()
        result.repeat_plus()
        result.minimize()
        return result

    def Upper(self, ast):
        result = ast.expr.copy()
        result.input_project()
        return result

    def Lower(self, ast):
        result = ast.expr.copy()
        result.output.project()
        return result

    def One_but_not(self, ast):
        result_fst = cfg.all_pairs_fst.copy()
        result_fst.minus(ast.expr)
        return result_fst

    def optexpression(self, ast):
        result_fst = ast.expr.copy()
        name = result_fst.get_name()
        result_fst.optionalize()
        result_fst.minimize()
        result_fst.set_name("({})".format(name))
        return result_fst

    def subexpression(self, ast):
        return ast.expr.copy()

    def symbol_or_pair(self, ast):
        string = ast.token.strip()
        failmsg = []
        pat = re.compile(r"""^
        (?P<up>[a-zšžåäöüõA-ZÅÄÖ0-9'´`]*
         |
         \{[a-zåäöüõA-ZÅÄÖØ'´`]+\})
        :
        (?P<lo>[a-zšžåäöüõA-ZÅÄÖØ'´`]*)
        $""", re.X)
        m = re.match(pat, string)
        if m:                       # it is a pair with a colon
            up = m.group("up")
            up_quoted = re.sub(r"([{}])", r"%\1", up)
            lo = m.group("lo")
            if up and (up not in cfg.input_symbol_set):
                failmsg.append("input symbol '{}'".format(up))
            if lo and (lo not in cfg.output_symbol_set):
                failmsg.append("output symbol '{}'".format(lo))
            if up and lo and ((up, lo) not in cfg.symbol_pair_set):
                failmsg.append("symbol pair '{}'".format(string))
            if failmsg:
                cfg.error_message = " and ".join(failmsg) + " not in alphabet"
                raise FailedSemantics(cfg.error_message)
            elif up and lo:         # it is a valid pair with a colon
                result_fst = hfst.regex(up_quoted + ':' + lo)
                result_fst.set_name(string)
                return result_fst
            elif up and (not lo):
                result_fst = hfst.regex(up_quoted)
                result_fst.compose(cfg.all_pairs_fst)
                result_fst.set_name(string)
                return result_fst
            elif (not up) and lo:
                result_fst = cfg.all_pairs_fst.copy()
                lo_fst = hfst.regex(lo)
                result_fst.compose(lo_fst)
                result_fst.set_name(string)
                return result_fst
            else:
                result_fst = cfg.all_pairs_fst.copy()
                result_fst.set_name("PI")
                return result_fst
        m = re.fullmatch(r"[a-zåäöüõA-ZÅÄÖØ]+", string)
        if m:                       # its either a defined sym or a surf ch
            if string in cfg.definitions:
                result_fst = cfg.definitions[string].copy()
                result_fst.set_name(string)
                return result_fst
            elif (string in cfg.output_symbol_set) and (string in cfg.input_symbol_set):
                result_fst =  hfst.regex(string)
                result_fst.set_name(string)
                return result_fst
            elif string in {'BEGIN', 'END'}:
                result_fst = hfst.regex(string)
                result_fst.set_name(string)
                return result_fst
        cfg.error_message = "'" + string + "' is an invalid pair/definend symbol"
        raise FailedSemantics(cfg.error_message)

def init(grammar_file='/Users/koskenni/github/pytwolc/twolcsyntax.ebnf'):
    grammar = open(grammar_file).read()
    parser = tatsu.compile(grammar)
    return parser

def parse_rule(parser, line_nl, start="expr_start"):
    """"Parse one rule or definiton or any constituent given as start
"""
    line = line_nl.strip()
    if (not line) or line[0] == '!':
        return "!", None, None, line  # it was a comment or an empty line
    rulepat = r"^.* +(=|<=|=>|<=>|/<=) +.*$"
    try:
        m = re.match(rulepat, line)
        if m:
            #print("groups:", m.groups())###
            if m.group(1) == '=':
                op, name, expr_fst = parser.parse(line, start='def_start',
                                                      semantics=TwolFstSemantics())
                return op, name, expr_fst, line
            elif m.group(1) in {'=>', '<=', '<=>', '/<='}:
                op, x_fst, contexts = parser.parse(line, start='rul_start',
                                                       semantics=TwolFstSemantics())
                return op, x_fst, contexts, line
        else:
             return "?", None, None, line
    except ParseException as e:
        msg = str(e)
        lst = msg.split("\n")
        if len(lst) >= 3:
            print(lst[1])
            print(lst[2], "<---", e.__class__.__name__, "ERROR HERE")
            if cfg.error_message:
                print("    ", cfg.error_message)
                cfg.error_message = ""
                return "?", None, None, line
        else:
            print(str(e))
            return "?", None, None, line

if __name__ == '__main__':
    import hfst
    parser = init()
    for line_nl in sys.stdin:
        line = line_nl.strip()
        #print(line)
        op, left, right, source = parse_rule(line)
        #result = parser.parse(line, start='expr_start', semantics=TwolRegexSemantics())
        #result = parser.parse(line, start='rul_start', semantics=TwolFstSemantics())
        #result = parser.parse(line, start='expr_start')
        if op == "=":
            print(left, op)
            print(right)
        elif op in {"=>", "<=", "<=>", "/<="}:
            print("left context:")
            print(left)
            print(op)
            #print(right)###
            for lc, rc in right:
                print("left context:")
                print(lc)
                print("right context:")
                print(rc)
        elif op == "!":
            print("Comment: " + line)
        elif op == "?":
            print("Incorrect: " + line)

            
    
