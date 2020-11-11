import re

keywords = ['else','if','int','return','void','while','float']
pattern = [] 

pattern.append(re.compile(r'/\*'))                    
pattern.append(re.compile(r'\*/'))                          
pattern.append(re.compile(r'//'))                    
pattern.append(re.compile(r'[a-zA-Z]+'))                 
pattern.append(re.compile(r'<=|>=|==|!='))                
pattern.append(re.compile(r'\+|-|\*|/|<|>|=|;|,|\(|\)|\[|\]|\{|\}'))            
pattern.append(re.compile(r'(\d+(\.\d+)?)([E][+|-]?\d+)?'))        
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
    displist = []
    lines = open(file)

    comDepth = 0

    for line in lines:
	linetoks = []
        str = line.strip()
        while (str):
            matchStr = ''
            for pat, index in zip(pattern, range(7)):
                matchStr = pat.match(str)
                if matchStr:
                    break
            if not matchStr:
                if not comDepth:
                    linetoks.append(['','::ERROR:: Input not in language:  ' + str[0],''])    
                str = str[1:].strip()
            elif matchStr:
                if index is 0:
                    comDepth += 1
                if index is 1 and comDepth:
                    comDepth -=1
                elif index is 1:
                    tokens.append(['*','*'])
                    linetoks.append(['*','*']) 
                    tokens.append(['/','/'])
                    linetoks.append(['/','/']) 
                if index is 2 and not comDepth:
                    str = ''
                    break 
                mstr = matchStr.group(0)
                str = str.replace(mstr, '', 1).strip()
                if index not in {0,1,2} and not comDepth:
                    tokType = getType(mstr,index)
                    if tokType in {'int', 'float'}:
                        tokens.append([mstr,'num',tokType])
                        linetoks.append([mstr,'num'])		#This line 
                    else:
                        tokens.append([mstr,tokType])
                        linetoks.append([mstr,tokType])		#This line 
        if not line.isspace():					#  
            if linetoks:
                displist.append([line.strip(),linetoks])
            else:
		displist.append(line.strip())
    if comDepth:
        displist.append('::ERROR:: Block comment never closed (use */ to close block comments)')
    return tokens, displist   

