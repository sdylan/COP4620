import sys

poppedScopes = []

class Scope:
    def __init__(self, name, level):
        self.name = name
        self.level = level
        self.variables = {}
        self.functions = []
        self.hasMain = False

class Symbol:
    def __init__(self, name, dType, isArr=False, arrSize='0'):
        self.name = name
        self.dType = dType
        self.isArr = isArr
        if isArr:
            self.arrSize = arrSize
            self.arr = []

class Function(Symbol):
    def __init__(self, name, dType, headerLineNum, headerLine):
        Symbol.__init__(self, name, dType)
        self.hasReturn = False
        self.paramList = []
        self.headerLineNum = headerLineNum
        self.headerLine = headerLine

class Error:
    def __init__(self, lineNum, line, errNum, id=''):
        self.lineNum = lineNum
        self.line = line
        self.errNum = errNum
        self.id = id

    def __str__(self):
        errorMessage = 'Error in line ' + str(self.lineNum) + ': "' + self.line +'"\n'
        errorMessage += '\t' + Error.getErrorMessage(self.errNum, self.id)
        return errorMessage    

    @staticmethod
    def getErrorMessage(errNum, id=''):
        if errNum == 1:
            return 'Variables may not be declared as type, void. Must be int or float.'
        if errNum == 2:
            return 'Array Size must be of type, int. Found a float in size definition.'
        if errNum == 3:
            return 'Parameters must be of type int or float. Or void must be the only parameter, signifying no parameters.'
        if errNum == 4:
            return 'Duplicate name found in scope. Only use each identifier once per scope.'
        if errNum == 5:
            return 'Duplicate function name found. Overloading is not permitted in C Minus.'
        if errNum == 6:
            return "Declaration after 'main' found. The function, 'main', must be the last declaration."
        if errNum == 7:
            return "Missing function, 'main'. It must be the last declaration with signature 'void main (void)'."
        if errNum == 8:
            return "The return type for 'main' must be type, void."
        if errNum == 9:
            return "The parameter list for 'main' must be 'void'."
        if errNum == 10:
            return 'Function does not have a return statement, int and float functions must return something of their return type.'
        if errNum == 11:
            return 'The identifier "{}" must be declared before it is used.'.format(id)
        if errNum == 12:
            return 'The function "{}" must be defined before it is used.'.format(id)
        if errNum == 13:
            return 'The types do not match.'
        if errNum == 14:
            return 'Symbol used for int when expecting array or vice-versa'
        if errNum == 15:
            return 'The array index must be of type int.'
        if errNum == 16:
            return 'The args and params are different lengths.'
        if errNum == 17:
            return 'The args and params dont match.' 
        if errNum == 18:
            return "Can not index non-array id's."
        if errNum == 19:
            return 'return type does not match' 

def semanalysisDriver(parseTree):
    global poppedScopes
    node = parseTree.root
    stack = []
    stack.append(node)
    scopes = []
    scopes.append(Scope('global', 0))
    errors = []
    semanalyze(node, stack, scopes, errors)
    for function in scopes[0].functions:
        if function.dType in ['int', 'float']:
            if not function.hasReturn:
                errors.append(Error(function.headerLineNum, function.headerLine, 10))
    if errors:
        print 'REJECT'
        for error in errors:
            print error
    else:
        print 'ACCEPT'
#   printScopes(scopes)
#   printScopes(reversed(poppedScopes))

def printScopes(scopes):
    for scope in scopes:
        print scope.name, scope.level
        print '    variables:' if scope.variables else ''
        for key in scope.variables:
            variable = scope.variables[key]
            print '\t', variable.name, '-', variable.dType, 'arr, size=' + variable.arrSize if variable.isArr else ''
        print '    functions:' if scope.functions else ''
        for function in scope.functions:
            print '\t', function.dType, function.name, '(',
            for param in function.paramList:
                print param.dType, param.name, 
                if param.isArr:
                    print '[', param.arrSize, ']',
            print ')', 'has return' if function.hasReturn else 'no return'

def semanalyze(node, stack, scopes, errors, dType=None):
    global poppedScopes
    currentScope = scopes[-1]
    if stack:
        if node.children:
            for child in reversed(node.children):
                if child.name != '@':
                    stack.append(child)

#int, float, void
        if node.name in ['int', 'float', 'void']:
            return node.name

#params
        elif node.name == 'PARAMS':
            paramType = stack.pop()
            dType = paramType.name
            if dType == 'void':
                err = semanalyze(stack.pop(), stack, scopes, errors)
                if err:
                    errors.append(Error(paramType.token[2], paramType.token[3], 3))
                else:
                    stack.pop()
                    stack.pop()
                    scopes.append(Scope(currentScope.functions[-1].name, currentScope.level + 1))
                    semanalyze(stack.pop(), stack, scopes, errors)
            else: 
                if currentScope.functions[-1].name == 'main':
                    errors.append(Error(paramType.token[2], paramType.token[3], 9))
                semanalyze(stack.pop(), stack, scopes, errors, dType)

#statement list prime
        elif node.name == 'STMTLIST`':
            if stack[-1].name == '}':
                poppedScopes.append(scopes.pop())
                stack.pop()
                semanalyze(stack.pop(), stack, scopes, errors)
            else:
                semanalyze(stack.pop(), stack, scopes, errors)

#statement
        elif node.name == 'STMT':
            semanalyze(stack.pop(), stack, scopes, errors)

#return statement
        elif node.name == 'RETSTMT':
            stack.pop()
            getType = semanalyze(stack.pop(), stack, scopes, errors)
            stack.pop()
            for function in scopes[0].functions:
                if function.name == currentScope.name:
                    function.hasReturn = True
                    if getType[0] != function.dType:
                        errors.append(Error(0,'',19))
            semanalyze(stack.pop(), stack, scopes, errors)

#return statement prime
        elif node.name == 'RETSTMT`':
            if stack[-1].name == ';':
                return ('void',False)
            else:
                return semanalyze(stack.pop(), stack, scopes, errors) 

#compound statement
        elif node.name == 'COMPOUNDSTMT':
            stack.pop()
            scopes.append(Scope(currentScope.name, currentScope.level + 1))
            semanalyze(stack.pop(), stack, scopes, errors)

#expression statement
        elif node.name == 'EXPSTMT':
            if stack[-1].name == ';':
                stack.pop()
                semanalyze(stack.pop(), stack, scopes, errors)
            else:
                semanalyze(stack.pop(), stack, scopes, errors)
                stack.pop()

#term prime
        elif node.name == 'TERM`':
            if stack[-1].name == 'MULOP':
                semanalyze(stack.pop(), stack, scopes, errors)
                factorType = semanalyze(stack.pop(), stack, scopes, errors)
                typeCheck = semanalyze(stack.pop(), stack, scopes, errors)
                if typeCheck and typeCheck != factorType:
                    errors.append(Error(0,'',13)) #datatypes not matching in factor
                return factorType
            else:
                return semanalyze(stack.pop(), stack, scopes, errors)     

#additive expression prime
        elif node.name == 'ADDEXP`':
            if stack[-1].name == 'ADDOP':
                semanalyze(stack.pop(), stack, scopes, errors)
                factorType = semanalyze(stack.pop(), stack, scopes, errors)
                typeCheck = semanalyze(stack.pop(), stack, scopes, errors)
                if typeCheck and typeCheck != factorType:
                    errors.append(Error(0,'',13)) #datatypes not matching in factor
                typeCheck = semanalyze(stack.pop(), stack, scopes, errors)
                if typeCheck and typeCheck != factorType:
                    errors.append(Error(0,'',13)) #datatypes not matching in factor
                return factorType
            elif stack[-1].name == 'SIMPEXP`':
                return semanalyze(stack.pop(), stack, scopes, errors)     
            
#simple expression prime
        elif node.name == 'SIMPEXP`':
            if stack[-1].name == 'RELOP':
                semanalyze(stack.pop(), stack, scopes, errors)
                factorType = semanalyze(stack.pop(), stack, scopes, errors)
                typeCheck = semanalyze(stack.pop(), stack, scopes, errors)
                if typeCheck and typeCheck != factorType:
                    errors.append(Error(0,'',13)) #datatypes not matching in factor
                typeCheck = semanalyze(stack.pop(), stack, scopes, errors)
                if typeCheck and typeCheck != factorType:
                    errors.append(Error(0,'',13)) #datatypes not matching in factor
                return factorType

#relop
        elif node.name == 'RELOP':
            stack.pop()

#addop
        elif node.name == 'ADDOP':
            stack.pop()

#mulop
        elif node.name == 'MULOP':
            stack.pop() 

#factor
        elif node.name == 'FACTOR':
            print stack[-1].name
            if stack[-1].name == '(':
                stack.pop()
                return semanalyze(stack.pop(), stack, scopes, errors)
                stack.pop()
            elif stack[-1].name == 'num':
                return (stack.pop().token[2],False)
            elif stack[-1].name == 'id':
                nextNode = stack.pop()
                expType = semanalyze(stack.pop(), stack, scopes, errors)
                if expType == 'call':
                    if not any(nextNode.token[0] == function.name for function in scopes[0].functions):
                        errors.append(Error(nextNode.token[2], nextNode.token[3], 12, nextNode.token[0]))
                    for function in scopes[0].functions:
                        if function.name == nextNode.token[0]:
                            paramTypes = [(param.dType,param.isArr) for param in function.paramList]
                            stack.pop()
                            argTypes = semanalyze(stack.pop(), stack, scopes, errors)
                            print paramTypes, argTypes
                            if len(paramTypes) == len(argTypes):
                                if not all(paramTypes[i] == argTypes[i] for i in range(len(argTypes))):
                                    errors.append(Error(0,'',17))
                            else:
                                errors.append(Error(0,'',16))
                            functionType = (function.dType, False)
                            stack.pop()
                            typeCheck = semanalyze(stack.pop(), stack, scopes, errors)
                            if typeCheck and typeCheck != functionType:
                                errors.append(Error(0,'',13)) #kbakbvkbvk ERROR CHECK
                            return functionType
                else:
                    if all(nextNode.token[0] not in scope.variables for scope in scopes): 
                        errors.append(Error(nextNode.token[2], nextNode.token[3], 11, nextNode.token[0]))
                    for scope in reversed(scopes):
                        if nextNode.token[0] in scope.variables: 
                            idSymbol = scope.variables[nextNode.token[0]]
                            if expType:
                                if idSymbol.isArr:
                                    idType = (idSymbol.dType, False)
                                else:
                                    idType = (idSymbol.dType, False)
                                    errors.append(Error(0,'',18))
                            else:
                                if idSymbol.isArr:
                                    idType = (idSymbol.dType, True)
                                else:
                                    idType = (idSymbol.dType, False)
                            typeCheck = semanalyze(stack.pop(), stack, scopes, errors)
                            if typeCheck and typeCheck != idType:
                                errors.append(Error(0,'',13)) 
                            return idType

#factor prime

        elif node.name == 'FACTOR`':
            if stack[-1].name == '(':
                return 'call'
            elif stack[-1].name == 'VAR`':
                idType = semanalyze(stack.pop(), stack, scopes, errors)
                return idType

#expression
        elif node.name == 'EXP':
            nextNode = stack.pop()
            nextTok = nextNode.name
            if nextTok == '(':
                expType = semanalyze(stack.pop(), stack, scopes, errors)
                stack.pop()
                typeCheck = semanalyze(stack.pop(), stack, scopes, errors)
                if typeCheck and typeCheck != expType:
                    errors.append(Error(0,'',13))
                return expType
            elif nextTok == 'num':	
                typeCheck = semanalyze(stack.pop(), stack, scopes, errors)
                if typeCheck and typeCheck != (nextNode.token[2], False):
                    errors.append(Error(nextNode.token[3], nextNode.token[4], 13))
                return (nextNode.token[2], False) 
            elif nextTok == 'id':
                expType = semanalyze(stack.pop(), stack, scopes, errors)
                if expType == 'call':
                    if not any(nextNode.token[0] == function.name for function in scopes[0].functions):
                        errors.append(Error(nextNode.token[2], nextNode.token[3], 12, nextNode.token[0]))
                    for function in scopes[0].functions:
                        if function.name == nextNode.token[0]:
                            paramTypes = [(param.dType,param.isArr) for param in function.paramList]
                            stack.pop()
                            argTypes = semanalyze(stack.pop(), stack, scopes, errors)
                            print paramTypes, argTypes
                            if len(paramTypes) == len(argTypes):
                                if not all(paramTypes[i] == argTypes[i] for i in range(len(argTypes))):
                                    errors.append(Error(0,'',17))
                            else:
                                errors.append(Error(0,'',16))
                            functionType = (function.dType, False)
                            stack.pop()
                            typeCheck = semanalyze(stack.pop(), stack, scopes, errors)
                            if typeCheck and typeCheck != functionType:
                                errors.append(Error(0,'',13)) #kbakbvkbvk ERROR CHECK
                            return functionType
                else:
                    if all(nextNode.token[0] not in scope.variables for scope in scopes): 
                        errors.append(Error(nextNode.token[2], nextNode.token[3], 11, nextNode.token[0]))
                    for scope in reversed(scopes):
                        if nextNode.token[0] in scope.variables: 
                            idSymbol = scope.variables[nextNode.token[0]]
                            if expType:
                                if idSymbol.isArr:
                                    idType = (idSymbol.dType, False)
                                else:
                                    idType = (idSymbol.dType, False)
                                    errors.append(Error(0,'',18))
                            else:
                                if idSymbol.isArr:
                                    idType = (idSymbol.dType, True)
                                else:
                                    idType = (idSymbol.dType, False)
                            typeCheck = semanalyze(stack.pop(), stack, scopes, errors)
                            if typeCheck and typeCheck != idType:
                                errors.append(Error(0,'',13)) 
                            return idType

#expression double prime
        elif node.name =='EXP``':
            if stack[-1].name == '=':
                stack.pop()
                return semanalyze(stack.pop(), stack, scopes, errors)
            else:
                return semanalyze(stack.pop(), stack, scopes, errors)

#arglist
        elif node.name == 'ARGLIST`':
            return

#args
        elif node.name == 'ARGS':
            argTypes = []
            while stack[-1].name != ')':
                if stack[-1].name == ',':
                    stack.pop()
                argType = semanalyze(stack.pop(), stack, scopes, errors)
                argTypes.append(argType)
#               semanalyze(stack.pop(), stack, scopes, errors)
            return argTypes

#expression prime
        elif node.name == 'EXP`':
            if stack[-1].name == '(':
                return 'call'
            elif stack[-1].name == 'VAR`':
                idType = semanalyze(stack.pop(), stack, scopes, errors)
                return idType

#variable prime
        elif node.name == 'VAR`':
            if stack[-1].name == '[':
                stack.pop()
                expType = semanalyze(stack.pop(), stack, scopes, errors)
                if expType != ('int', False):
                    errors.append(Error(0,'',15))#ERROR FOR NONINT IN ARRAY
                stack.pop()
                return True
            else:
                if stack[-1].name == 'EXP``':
                    stack.pop()
                return False

#iteration statement
        elif node.name == 'ITERSTMT':
            print stack[-1].name
            stack.pop()
            print stack[-1].name
            stack.pop()
            print stack[-1].name
            semanalyze(stack.pop(), stack ,scopes, errors)
            semanalyze(stack.pop(), stack, scopes, errors)

#selection statement
        elif node.name == 'SELSTMT':
            stack.pop()
            stack.pop()
            semanalyze(stack.pop(), stack ,scopes, errors)
            stack.pop()
            semanalyze(stack.pop(), stack, scopes, errors)
            semanalyze(stack.pop(), stack, scopes, errors)

#selection statement prime
        elif node.name == 'SELSTMT`':
            if stack[-1].name == 'else':
                stack.pop()
                semanalyze(stack.pop(), stack, scopes, errors)

#locdec prime
        elif node.name == 'LOCDEC`':
            if stack[-1].name == 'STMTLIST`':
                semanalyze(stack.pop(), stack, scopes, errors)
            else:
                dType = semanalyze(stack.pop(), stack, scopes, errors)
                semanalyze(stack.pop(), stack, scopes, errors, dType)

#params prime
        elif node.name == 'PARAMS`':
            if stack[-1].name != ')':
                return True
            else:
                return False

#param prime
        elif node.name == 'PARAM`':
            nextNode = stack[-1]
            nextTok = nextNode.name
            if nextTok == '[':
                stack.pop()
                stack.pop()
                return 'paramarr'
            else:
                return 'param'

#paramlist prime
        elif node.name == 'PARAMLIST`':
            nextNode = stack.pop()
            nextTok = nextNode.name
            if nextTok == ')':
                stack.pop()
                scopes.append(Scope(currentScope.functions[-1].name, currentScope.level + 1))
                for param in currentScope.functions[-1].paramList:
                    scopes[-1].variables[param.name] = param
                semanalyze(stack.pop(), stack, scopes, errors)
            elif nextTok == ',':
                dType = semanalyze(stack.pop(), stack, scopes, errors)
                if dType == 'void':
                    errors.append(Error(nextNode.token[2], nextNode.token[3], 3))
                else:
                    semanalyze(stack.pop(), stack, scopes, errors, dType)

#id
        elif node.name == 'id':
            tok = node.token
            symType = semanalyze(stack.pop(), stack, scopes, errors)
            if symType == 'paramarr':
                params = currentScope.functions[-1].paramList
                for param in params:
                    if node.token[0] == param.name:
                        errors.append(Error(tok[2], tok[3], 4))
                        return
                params.append(Symbol(tok[0], dType, True))
                semanalyze(stack.pop(), stack, scopes, errors)
            elif symType == 'param':
                params = currentScope.functions[-1].paramList
                for param in params:
                    if tok[0] == param.name:
                        errors.append(Error(tok[2], tok[3], 4))
                        return
                params.append(Symbol(tok[0], dType))
                semanalyze(stack.pop(), stack, scopes, errors)
            elif symType == 'fun':
                if tok[0] == 'main':
                    currentScope.hasMain = True
                    if dType != 'void':
                        errors.append(Error(tok[2], tok[3], 8))
                functions = currentScope.functions
                for function in functions:
                    if function.name == tok[0]:
                        errors.append(Error(tok[2], tok[3], 5))
                        return
                functions.append(Function(tok[0], dType, tok[2], tok[3]))
                semanalyze(stack.pop(), stack, scopes, errors)
            elif symType == 'var':
                if dType == 'void':
                    errors.append(Error(tok[2], tok[3], 1))
                if tok[0] in currentScope.variables:
                    errors.append(Error(tok[2], tok[3], 4))
                    return
                currentScope.variables[tok[0]] = Symbol(tok[0], dType)
                semanalyze(stack.pop(), stack, scopes, errors)
            elif symType == 'arr':
                if dType == 'void':
                    errors.append(Error(tok[2], tok[3], 1))
                sizeNode = stack.pop()
                if sizeNode.token[2] == 'float':
                    errors.append(Error(tok[2], tok[3], 2))
                arrSize = sizeNode.token[0]
                if tok[0] in currentScope.variables:
                    errors.append(Error(tok[2], tok[3], 4))
                    return
                currentScope.variables[tok[0]] = Symbol(tok[0], dType, True, arrSize)
                stack.pop()
                stack.pop()
                semanalyze(stack.pop(), stack, scopes, errors)

#dec prime
        elif node.name == 'DEC`':
            nextNode = stack.pop()
            nextTok = nextNode.name
            if  nextTok == '(':
                return 'fun'
            elif nextTok == 'VARDEC`':
                return semanalyze(nextNode, stack, scopes, errors)

#vardec prime
        elif node.name == 'VARDEC`':
            nextTok = stack.pop().name
            if nextTok == ';':
                return 'var'
            elif nextTok == '[':
                return 'arr'

#declist prime
        elif node.name == 'DECLIST`':
            if stack[-1].name == 'PROGRAM':
                if not scopes[0].hasMain:
                    errors.append(Error(0, 'source code', 7))
                return
            elif currentScope.hasMain:
                tok = stack[-1].children[0].token
                errors.append(Error(tok[2], tok[3], 6))
            dType = semanalyze(stack.pop(), stack, scopes, errors)
            semanalyze(stack.pop(), stack, scopes, errors, dType)

#program
        elif node.name == 'PROGRAM':
            dType = semanalyze(stack.pop(), stack, scopes, errors)
            semanalyze(stack.pop(), stack, scopes, errors, dType)

#typespec
        elif node.name == 'TYPESPEC':
            return semanalyze(stack.pop(), stack, scopes, errors)
        
