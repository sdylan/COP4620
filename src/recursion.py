def createNewRule(oldict, key, tempdict):
    newkey = key + '`'
    newlist = []
    for item in oldict[key]:
        if item.startswith(key):
            str = item.replace(key, '')+' '+newkey
            newlist.append(str.strip())
    newlist.append('@')
    tempdict[newkey] = newlist

def editOldRule(aDict, key):
    newkey = key + '`'
    newlist = []
    for item in aDict[key]:
        if not item.startswith(key):
            if item == '@':
                str = newkey
            else:
                str = item + ' ' + newkey
            newlist.append(str.strip())
    aDict[key] = newlist

def removeImmediateLR(aDict, order):
    needMod = False

    newrules = {}

    for key in aDict:
        for i in aDict[key]:
            if i.startswith(key):
                needMod = True
    
    
        if needMod:
            createNewRule(aDict, key, newrules)
            editOldRule(aDict, key)

        needMod = False

    for key in newrules:
        aDict[key] = newrules[key]    
        order.insert(order.index(key[:-1])+1, key)
