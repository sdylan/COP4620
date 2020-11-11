from sys import argv
from display import printRules, printTokensUgly, printTokens
from recursion import removeImmediateLR
from IOstuff import getRules, menu, exportTable
from factoring import removeImmediateLF, removeFurtherLF
from firstfollow import firstSets, followSets
from parse import buildParseTree, makeParsingTable, parseSourceCode


def editOrder(rules, order):
    """
    This method is called after the single production substitutions
    take place. A new list with only rules that have more than one 
    production.The goal is such that we do not consider them for 
    further grammar fixing techniques.

    parameters:
      rules (dict): grammar rule:list of productions (key:value)
      order (list of strings): the order of rules by name as 
             demonstrated in the original grammar

    returns:
      newlist (list of strings): the newly truncated list of rules
    """
    newlist = []

    #Checks starting rule and adds to newlist if only 1 production

    if len(rules[order[0]]) == 1:
        newlist.append(order[0])

    #Iterates order list and adds rules to newlist with >1 production

    for key in order:
        if len(rules[key]) > 1:
            newlist.append(key)
    return newlist
            

rules = {}
order = []

getRules(argv[1], rules, order)

removeImmediateLR(rules, order)

for i in range(10):
    removeImmediateLF(rules, order)

order = editOrder(rules, order)
rulesFirst = firstSets(rules, order)

for i in range(10):
    removeFurtherLF(rules, order, rulesFirst)
    rulesFirst = firstSets(rules, order)

rulesFollow = {}

for key in order:
    rulesFollow[key] = set()

for i in range(100):
    followSets(rulesFirst, order, rulesFollow)

parsingTable = makeParsingTable(rulesFirst, rulesFollow)

exportTable(parsingTable)

parse, displist, success =  parseSourceCode(argv[2], parsingTable)

parseTree = buildParseTree(parsingTable, parse[:])

#printTokensUgly(displist)

print success

menu(rulesFirst, rulesFollow, order, parseTree, parse, parsingTable, displist)
