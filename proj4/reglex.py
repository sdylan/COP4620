import re

keywords = ['else','if','int','return','void','while','float']
pattern = [ re.compile(r'/\*'),                    
            re.compile(r'\*/'),                          
            re.compile(r'//'),                   
            re.compile(r'[a-zA-Z]+'),                 
            re.compile(r'<=|>=|==|!='),                
            re.compile(r'\+|-|\*|/|<|>|=|;|,|\(|\)|\[|\]|\{|\}'),            
            re.compile(r'(\d+(\.\d+)?)([E][+|-]?\d+)?') ]
intpat = re.compile(r'\d+')

def getType(str, index):
    if index is 3:
        if str in keywords:
            return 'kw'
        return 'id'
    elif index is 4:
        return str
    elif index is 5:
        return str
    elif index is 6:
        if intpat.match(str).group(0) is str:
            return 'int'
        else: 
            return 'float'

def getTokens(file):
    tokens = []
    lines = open(file)
    comDepth = 0
    lineNum = 0
    for line in lines:
        lineNum += 1
        str = line.strip()
        while (str):
            matchStr = ''
            for pat, index in zip(pattern, range(7)):
                matchStr = pat.match(str)
                if matchStr:
                    break
            if not matchStr:
                str = str[1:].strip()
            elif matchStr:
                if index is 0:
                    comDepth += 1
                if index is 1 and comDepth:
                    comDepth -=1
                elif index is 1:
                    tokens.append(['*','*'])
                    tokens.append(['/','/'])
                if index is 2 and not comDepth:
                    str = ''
                    break 
                mstr = matchStr.group(0)
                str = str.replace(mstr, '', 1).strip()
                if index not in {0,1,2} and not comDepth:
                    tokType = getType(mstr,index)
                    if tokType in {'int', 'float'}:
                        tokens.append([mstr,'num',tokType, lineNum, line.strip()])
                    else:
                        tokens.append([mstr,tokType, lineNum, line.strip()])
    return tokens   
