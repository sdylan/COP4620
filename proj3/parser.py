from sys import argv
from reglex import getTokens
from semanalyzer import semanalysisDriver

class Tree:

    def __init__(self, root):
        self.root = root

    def printTree(self):
        root = self.root
        print
        print
        print root
        self.printChildren(root, 1)

    def printChildren(self, node, depth):
        for i in node.children:
            for j in range(depth):
                print ' ',
            print i
            self.printChildren(i, depth + 1)

class Node:

    def __init__(self, name, parent, depth):
        self.name = name
        self.parent = parent
        self.depth = depth
        self.token = ''
        self.isLeaf = False
        self.children = []

    def __str__(self):
        if self.token:
            return '{} : {} accepted {}'.format(self.depth, self.name, self.token)
        else:
            return '{} : {}'.format(self.depth, self.name)

def parseSourceCode(file, table):
 
    tokens = getTokens(file)

    parseStack = ['$', 'PROGRAM']
    tokens.append(['$','$'])
    parse = []
    success = ''

    while True:
        keytuple = ''
        acceptedToken = []
        if parseStack and tokens:
            if parseStack[-1] == '$' and tokens[0][0] == '$':
                success = 'ACCEPT'
                break
            elif (parseStack[-1], tokens[0][0]) in table:
                topStack = parseStack.pop()
                keytuple = (topStack, tokens[0][0])
                for token in reversed(table[keytuple].split()):
                    if token is not '@':
                        parseStack.append(token)
            elif (parseStack[-1], tokens[0][1]) in table:
                topStack = parseStack.pop()
                keytuple = (topStack, tokens[0][1])
                for token in reversed(table[keytuple].split()):
                    if token is not '@':
                        parseStack.append(token)
            elif parseStack[-1] == tokens[0][0] or parseStack[-1] == tokens[0][1]:
                parseStack.pop()
                acceptedToken = tokens.pop(0)
            else:
                success = 'REJECT'
                break
        else:
            success = 'REJECT'
            break
        if keytuple:
            parse.append(keytuple)
        if acceptedToken:
            parse.append(acceptedToken)

    return parse, success

def buildParseTree(parsingTable, parse):
    tree = Tree(Node('PROGRAM', 'root', 0))
    getChild(tree.root, parse, parsingTable)
    return tree

def getChild(node, parse, parsingTable):
    if parse:
        step = parse[0]
        if isinstance(step, tuple):
            if node.name is not '@':
                parse.pop(0)
                for item in parsingTable[step].split():
                    child = Node(item, node, node.depth + 1)
                    node.children.append(child)
                    getChild(child, parse, parsingTable)
        elif isinstance(step, list):
            if node.name is not '@':
                node.token = step
                node.isLeaf = True
                parse.pop(0)

def getTable():
    parsingTable = {}
    file = open('Table','r')
    for line in file:
        rule, token, production = line.strip().split('?')
        parsingTable[(rule, token)] = production
    return parsingTable

parseTable = getTable()
parse, success = parseSourceCode(argv[1], parseTable)
parseTree = buildParseTree(parseTable, parse[:])
if success == 'ACCEPT':
    semanalysisDriver(parseTree)
else:
    print 'Did not parse.'
