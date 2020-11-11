def printRulesObsolete(rules, order):
    print
    for item in order:
        ruleStr = ''
        for i in rules[item]:
            if rules[item].index(i) > 0:
                ruleStr += ' | '
            ruleStr += i
        print '{} {:>10} -> {}'.format(len(rules[item]), item, ruleStr)

def printTokens(displist):
    for i in displist:
        if isinstance(i, list):
            print 'INPUT: ',i[0]
            print '    {:8}{:11}'.format('Type','Lexeme') 
            print '    -------------------'
            for j in i[1]:
                print '    {:8}{:11}'.format(j[1],j[0])   
            print
        elif i.startswith('::'):
            print i
        else:
            print 'INPUT: ',i

def printTokensUgly(displist):
    for i in displist:
        if isinstance(i, list):
            print 'INPUT: ',i[0]
            for j in i[1]:
                print '{:4}'.format(j[1]), (j[0] if j[0] != j[1] else '')   
            print
        elif i.startswith('::'):
            print i
        else:
            print 'INPUT: ',i

def printRules(firstSets, followSets, order):
    print
    for item in order:
        ruleStr = ''
        firstSetStr = ''
        followSetStr = ''
        for i in firstSets[item]:
            if firstSets[item].index(i) > 0:
                ruleStr += ' | '
                firstSetStr += ' | '
            firstSetStr += ' '.join(i[1])
            ruleStr += i[0]    
        followSetStr = " ".join(followSets[item])
        print '{} {:>10} -> {:100} {:38} {}'.format(len(firstSets[item]), item, ruleStr, firstSetStr, followSetStr)
