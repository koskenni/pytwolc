# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import sys, re, json
from codecs import open
from pprint import pprint

import tatsu
from tatsu.ast import AST
from tatsu.walkers import NodeWalker

from tatsu.exceptions import ParseException, FailedParse, ParseError, FailedSemantics

import twex

definitions = {"PAIRS": "PAIRS", "PI": "PAIRS"}

error_message = ""

class TwolcRegexSemantics(object):

    def define(self, ast):
        global definitions
        definitions[ast.left] = ast.right
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

    def context(self, ast):
        lc = ast.left if ast.left else ""
        rc = ast.right if ast.right else ""
        result = [(lc, rc)]
        return result

    def context_lst(self, ast):
        #result = ast.left.extend(ast.right)
        left = ast.left.copy()
        right = ast.right.copy()
        right[0:0] = left 
        return right

    def symbol_or_pair(self, ast):
        global error_message, definitions
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
            if up and (up not in twex.input_symbol_set):
                failmsg.append("input symbol '{}'".format(up))
            if lo and (lo not in twex.output_symbol_set):
                failmsg.append("output symbol '{}'".format(lo))
            if up and lo and ((up, lo) not in twex.symbol_pair_set):
                failmsg.append("symbol pair '{}'".format(string))
            if failmsg:
                error_message = " and ".join(failmsg) + " not in alphabet"
                raise FailedSemantics(error_message)
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
            if string in definitions:
                return "{}".format(string)
            elif (string in twex.output_symbol_set) and (string in twex.input_symbol_set):
                return "{}:{}".format(string, string)
            elif string in {'BEGIN', 'END'}:
                return string
        error_message = "'" + string + "' is an invalid pair/definend symbol"
        raise FailedSemantics(error_message)

    def optexpression(self, ast):
        return "({})".format(ast.expr)

    def subexpression(self, ast):
        return "[{}]".format(ast.expr)

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

    def concatenation(self, ast):
        return "[{} {}]".format(ast.left, ast.right)

    def composition(self, ast):
        return "[{} .o. {}]".format(ast.left, ast.right)

    def crossproduct(self, ast):
        return "[{} .x. {}]".format(ast.left, ast.right)

    def intersection(self, ast):
        return "[{} & {}]".format(ast.left, ast.right)

    def union(self, ast):
        return "[{} | {}]".format(ast.left, ast.right)

    def difference(self, ast):
        return "[{} - {}]".format(ast.left, ast.right)

def init(grammar_file='twolcsyntax.ebnf'):
    global parser, error_message
    grammar = open(grammar_file).read()
    parser = tatsu.compile(grammar)
    error_message = ''
    return

def parse_rule(line_nl):
    global parser, error_message
    line = line_nl.strip()
    if (not line) or line[0] == '!':
        return False                # it was a comment or an empty line
    rulepat = r"^.* +(=|<=|=>|<=>|/<=) +.*$"
    try:
        m = re.match(rulepat, line)
        if m:
            #print("groups:", m.groups())###
            if m.group(1) == '=':
                ast = parser.parse(line, start='def_start',
                                   semantics=TwolcRegexSemantics())
                #print(ast)###
            elif m.group(1) in {'=>', '<=', '<=>', '/<='}:
                ast = parser.parse(line, start='rul_start',
                                       semantics=TwolcRegexSemantics())
                #print(ast)###
        else:
            print("????", line)
            return False
    except ParseException as e:
        msg = str(e)
        lst = msg.split("\n")
        if len(lst) >= 3:
            print(lst[1])
            print(lst[2], "<---", e.__class__.__name__, "ERROR HERE")
            if error_message:
                print("    ", error_message)
                error_message = ""
                return False
        else:
            print(str(e))
            return False
    
    ast_lst = list(ast)
    ast_lst.append(line)
    return tuple(ast_lst)

if __name__ == '__main__':
    twex.read_fst("nounex.fst")
    init(grammar_file='twolcsyntax.ebnf')
    for line in sys.stdin:
        res = parse_rule(line)
        print(res)

