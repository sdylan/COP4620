def firstSets(adict, order):
    newdict = {}
    for key in order:
        newlist = []
        for string in adict[key]:
            firstTok = string.split()[0]
            tempset = set()
            if not firstTok.isupper():
                tempset = {firstTok}
            else:
                tempset = set(findfirstsfornonterminals(adict, string))    
            newlist.append([string, tempset])
        newdict[key] = newlist
    return newdict    

def findfirstsfornonterminals(adict, rule):
    firstTok = rule.split()[0]
    templist = []
    if not firstTok.isupper():
        templist.append(firstTok)
        return templist
    else: 
        for string in adict[firstTok]:
            if string == '@':
                rulepart = rule.replace(firstTok, '').strip()
                if rulepart != '':
                    templist.extend(findfirstsfornonterminals(adict, rulepart))        
            templist.extend(findfirstsfornonterminals(adict, string))
    return templist            

def followSets(adict, order, rulesFollow):
    
    rulesFollow[order[0]].add('$')

    for key in order:
        for str in adict[key]: 
            tokens = str[0].split()
            i = len(tokens)
            for token, index in zip(reversed(tokens), range(i-1,-1,-1)):
                if token.isupper() and index == i - 1:
                    for tok in rulesFollow[key]:
                        rulesFollow[token].add(tok)
                elif token.isupper() and index < i - 1:
                    if tokens[index + 1].isupper():
                        for firstSet in adict[tokens[index + 1]]:
                            for first in firstSet[1]:
                                if first == '@':
                                    for follow in rulesFollow[tokens[index+1]]:
                                        rulesFollow[token].add(follow)
                                else:
                                    rulesFollow[token].add(first)
                    else:
                        rulesFollow[token].add(tokens[index + 1])

