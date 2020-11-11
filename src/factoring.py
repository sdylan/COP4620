def removeImmediateLF(adict, order):
    LFlist = []
    tempdict = {}
    findLF(adict, order, LFlist)
    for i in LFlist:
        createNewRule(i, adict, tempdict)
        editOldRule(adict, i)
    for key in tempdict:
        adict[key] = tempdict[key]
        order.insert(order.index(key[:-1])+1, key)
    for i in range(10):
        subSingles(adict, order)

def removeFurtherLF(adict, order, setdict):
    needsSubList = []
    for key in order:
        for str in adict[key]:
            for otherstr in adict[key]:
                if str is otherstr:
                    continue
                elif str.split()[0].isupper() and setdict[key][adict[key].index(str)][1] & setdict[key][adict[key].index(otherstr)][1]:
                    for item in adict[str.split()[0]]:
                        if item.startswith(otherstr.split()[0]): 
                            needsSubList.append((key, str))     
    substituteRules(adict, needsSubList)
    removeImmediateLF(adict, order)

def substituteRules(adict, needsSubList):
    for item in needsSubList:
        key, str = item
        adict[key].remove(str)
        nonTerminal = str.split()[0].strip()
        for rule in adict[nonTerminal]:
            adict[key].append(str.replace(nonTerminal, rule).strip())    
        
def findLF(adict, order, LFlist):
    for key in adict:
        if len(adict[key]) > 0:
            for item1 in adict[key]:
                start = adict[key].index(item1)
                for item2 in adict[key][start+1:]:
                    matchpart = commonStart(item1, item2)
                    if matchpart != '' and '<' not in matchpart and '>' not in matchpart:
                        LFlist.append((key, matchpart))

def editOldRule(adict, LFtuple):
    key, matchpart = LFtuple
    newkey = key + '`'
    newlist = []
    for item in adict[key]:
        if not item.startswith(matchpart):
            newlist.append(item)
    newlist.append(matchpart.strip() + ' ' + newkey.strip())
    adict[key] = newlist
            
        
def createNewRule(LFtuple, adict, tempdict):
    key, matchpart = LFtuple
    newkey = key + '`'
    newlist = []
    for item in adict[key]:
        if item.startswith(matchpart):
            str = item.replace(matchpart, '', 1).strip()
            if str == '':    
                str = '@'
            newlist.append(str)
    tempdict[newkey] = newlist
            

def terminating(cond):
    if cond:
        return True
    raise StopIteration

def commonStart(sa, sb):
    return ''.join(a for a, b in zip(sa, sb) if terminating(a == b))

def subSingles(adict, order):
    for key in order:
        for item in adict[key]:
            index = adict[key].index(item)
            tokens = item.split(' ')
            for token in tokens:
                if token in adict and len(adict[token]) == 1:
                    tokens[tokens.index(token)] = adict[token][0]
                    #adict[key][index] = item.replace(token, adict[token][0])
            adict[key][index] = ' '.join(tokens)
