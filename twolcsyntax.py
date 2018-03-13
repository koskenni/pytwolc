# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import sys, re, json
from codecs import open
from pprint import pprint

import tatsu
from tatsu.ast import AST
from tatsu.walkers import NodeWalker

from tatsu.exceptions import ParseException, FailedParse, ParseError, FailedSemantics

definitions = {"PAIRS": "PAIRS", "PI": "PAIRS"}
import twex
twex.read_examples("nounex.pairstr")

error_message = ""

class TwolcsyntaxSemantics(object):

    def define(self, ast):
        global definitions
        definitions[ast.left] = ast.right
        return "{} = {} ;".format(ast.left, ast.right)
    
    def identifier(self, ast):
        string = ast.token.strip()
        return string

    def right_arrow_rule(self, ast):
        string = "{} => {} ;".format(ast.left, ast.right)
        return string

    def left_arrow_rule(self, ast):
        string = "{} <= {} ;".format(ast.left, ast.right)
        return string

    def double_arrow_rule(self, ast):
        string = "{} <=> {} ;".format(ast.left, ast.right)
        return string

    def exclusion_rule(self, ast):
        string = "{} /<= {} ;".format(ast.left, ast.right)
        return string

    def context(self, ast):
        lc = ast.left if ast.left else ""
        rc = ast.right if ast.right else ""
        string = "?:?* {} _ {} ?:?*".format(lc, rc)
        return string

    def context_lst(self, ast):
        string = "{} , {}".format(ast.left, ast.right)
        return string

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
            else:
                up = up if up else "?"
                lo = lo if lo else "?"
                return "{}:{}".format(up, lo)
        m = re.fullmatch(r"[a-zåäöüõA-ZÅÄÖØ]+", string)
        if m:                       # its either a defined sym or a surf ch
            if string in definitions:
                return "<{}>".format(string)
            elif (string in twex.output_symbol_set) and (string in twex.input_symbol_set):
                return "{}:{}".format(string, string)
            elif string in {'BEGIN', 'END'}:
                return "<"+string+">"
        error_message = "'" + string + "' is an invalid pair/definend symbol"
        raise FailedSemantics(error_message)

    def optexpression(self, ast):
        return "({})".format(ast.expr)

    def subexpression(self, ast):
        return ast.expr

    def Kleene_star(self, ast):
        return "[{}]*".format(ast.expr)

    def Kleene_plus(self, ast):
        return "[{}]+".format(ast.expr)

    def Upper(self, ast):
        return "[{}].u".format(ast.expr)

    def Lower(self, ast):
        return "[{}].l".format(ast.expr)

    def One_but_not(self, ast):
        return "\\[{}]".format(ast.expr)

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

def main():
    global error_message
    grammar = open('twolcsyntax.ebnf').read()
    parser = tatsu.compile(grammar)
    rulepat = r"^.* +(=|<=|=>|<=>|/<=) +.*$"
    for line in sys.stdin:
        if line.lstrip() and line.lstrip()[0] == "!":
            continue
        try:
            m = re.match(rulepat, line)
            if m:
                #print(m.groups())###
                if m.group(1) == '=':
                    ast = parser.parse(line, start='def_start',
                                           semantics=TwolcsyntaxSemantics())
                    #print("{} {} {} ;".format(ast.left, ast.op, ast.right))
                    print(ast)
                elif m.group(1) in {'=>', '<=', '<=>', '/<='}:
                    ast = parser.parse(line, start='rul_start',
                                           semantics=TwolcsyntaxSemantics())
                    #print("{} {} {} ;".format(ast.left, ast.op, ast.right))
                    print(ast)
                else:
                    print("????", line)
                    continue
                print()
                #print("definitons:", definitions)###
        except ParseException as e:
            msg = str(e)
            #print("str(e):", msg)
            lst = msg.split("\n")
            if len(lst) >= 3:
                print(lst[1])
                print(lst[2], "<---", e.__class__.__name__, "ERROR HERE")
                if error_message:
                    print("    ", error_message)
                    error_message = ""
            else:
                print(str(e))

if __name__ == '__main__':
    main()
    
