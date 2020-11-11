from reglex import getTokens

def printChildren(node, depth):
    for i in node.children:
        for j in range(depth):
            print ' ',
        print i
        printChildren(i, depth + 1)

class Tree:
    
    def __init__(self, root):
        self.root = root

    def printTree(self):
        root = self.root
        print
        print
        print root
        printChildren(root, 1)

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
            
def makeParsingTable(firstSets, followSets):
    parseTable = {}
    for key in firstSets:
        for rule in firstSets[key]:
            if rule[0] == '@':
                for follow in followSets[key]:
                    if (key, follow) not in parseTable:
                        parseTable[(key, follow)] = rule[0]
            else:
                for first in rule[1]:
                    if first == '@':
                        for follow in followSets[key]:
                            parseTable[(key, follow)] = rule[0]
                    parseTable[(key, first)] = rule[0]
    return parseTable

def parseSourceCode(file, table):
 
    tokens, displist = getTokens(file)

    parseStack = ['$', 'PROGRAM']
    tokens.append(['$','$'])
    parse = []
    success = ''

    while True:
        keytuple = ''
        acceptTok = []
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
                acceptTok = tokens.pop(0)
            else:
                success = 'REJECT'
                break
        else:
            success = 'REJECT'
            break
        if keytuple:
            parse.append(keytuple)
        if acceptTok:
            parse.append(acceptTok)

    return parse, displist, success
   
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

