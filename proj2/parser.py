from sys import argv
from reglex import getTokens

def parseSourceCode(file, table):
 
    tokens = getTokens(file)

    parseStack = ['$', 'PROGRAM']
    tokens.append(['$','$'])

    while True:
        if parseStack and tokens:
            if parseStack[-1] == '$' and tokens[0][0] == '$':
                print 'ACCEPT'
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
                tokens.pop(0)
            else:
                print 'REJECT'
                break
        else:
            print 'REJECT'
            break

def getTable():
    parsingTable = {}
    file = open('Table','r')
    for line in file:
        rule, token, production = line.strip().split('?')
        parsingTable[(rule, token)] = production
    return parsingTable

parseSourceCode(argv[1], getTable())
