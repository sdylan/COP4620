instructions = []
tempnum = 0
relopsymbol = ''

class Instruction:
    def __init__(self, op, arg1, arg2, result):
        self.op = op
        self.arg1 = arg1
        self.arg2 = arg2
        self. result = result

    def __str__(self):
        return "{:8}{:8}{:8}{:8}".format(self.op, self.arg1, self.arg2, self.result)

def genTemp():
    global tempnum
    tempname = 't'+str(tempnum)
    tempnum += 1
    return tempname

def getBranchType():
    if relopsymbol == '>':
        return 'brle'
    if relopsymbol == '>=':
        return 'brlt'
    if relopsymbol == '<':
        return 'brge'
    if relopsymbol == '<=':
        return 'brgt'
    if relopsymbol == '==':
        return 'brne'
    if relopsymbol == '!=':
        return 'bre'

def driver(tokens):
    tokens.append(['$','$'])
    program(tokens)
    for inst, num in zip(instructions, range(1,len(instructions)+1)):
        print '{:3} {}'.format(str(num), inst)

def program (tokens):
    dtype = typespec(tokens)
    id = tokens.pop(0)[0]
    if tokens[0][0] == '(':
        instructions.append(Instruction('func', id, dtype, '0')) #fix the numbers later
    space = decprime(tokens)
    if space == 0:
        instructions.append(Instruction('end','func', id, ''))
    if space > 0:
        instructions.append(Instruction('alloc', str(space * 4), '', id))
    declistprime(tokens)

def declistprime(tokens):
    if tokens[0][0] != '$':
        dtype = typespec(tokens)
        id = tokens.pop(0)[0]
        if tokens[0][0] == '(':
            instructions.append(Instruction('func', id, dtype, '0')) #fix the numbers later
        space = decprime(tokens)
        if space == 0:
            instructions.append(Instruction('end','func', id, ''))
        if space > 0:
            instructions.append(Instruction('alloc', str(space * 4), '', id))
        declistprime(tokens)

def decprime(tokens):
    if tokens[0][0] == '(':
        tokens.pop(0)
        params(tokens)
        tokens.pop(0)
        tokens.pop(0)
        locdecprime(tokens)
        stmtlistprime(tokens)
        tokens.pop(0)
        return 0
    else:
        return vardecprime(tokens)
       
def vardecprime(tokens):
    if tokens[0][0] == ';':
        tokens.pop(0)
        return 1
    else:
        tokens.pop(0)
        space = int(tokens.pop(0)[0])
        tokens.pop(0)
        tokens.pop(0)
        return space
        
def typespec(tokens):
    return tokens.pop(0)[0]

def params(tokens):
    if tokens[0][0] == 'void':
        tokens.pop(0)
        return
    else:
        dtype = tokens.pop(0)[0]
        id = tokens.pop(0)[0]
        instructions.append(Instruction('param', '', '', id))
        instructions.append(Instruction('alloc', '4', '', id))
        paramprime(tokens)
        paramlistprime(tokens)

def paramlistprime(tokens):
    if tokens[0][0] != ')':
        tokens.pop(0)
        dtype = tokens.pop(0)[0]
        id = tokens.pop(0)[0]
        instructions.append(Instruction('param', '', '', id))
        instructions.append(Instruction('alloc', '4', '', id))
        paramprime(tokens)
        paramlistprime(tokens)
    
def paramprime(tokens):
    if tokens[0][0] == '[':
        tokens.pop(0)
        tokens.pop(0) 

def locdecprime(tokens):
    if tokens[0][0] in ['int', 'float', 'void']:
        dtype = tokens.pop(0)[0]
        id = tokens.pop(0)[0]
        space = vardecprime(tokens)
        instructions.append(Instruction('alloc', str(space * 4), '', id))
        locdecprime(tokens)

def stmtlistprime(tokens):
    if tokens[0][0] != '}':
        stmt(tokens)
        stmtlistprime(tokens)

def stmt(tokens):
    if tokens[0][0] == '{':
        compoundstmt(tokens)
    elif tokens[0][0] == 'if':
        selstmt(tokens)
    elif tokens[0][0] == 'while':
        iterstmt(tokens)
    elif tokens[0][0] == 'return':
        retstmt(tokens)
    else:
        expstmt(tokens)

def compoundstmt(tokens):
    instructions.append(Instruction('block','','',''))
    tokens.pop(0)
    locdecprime(tokens)
    stmtlistprime(tokens)
    tokens.pop(0)
    instructions.append(Instruction('end','block','',''))

def backpatchOut(bpo):
    instructions[bpo].result = str(len(instructions) + 1)

def selstmt(tokens):
    tokens.pop(0)
    tokens.pop(0)
    res = exp(tokens)
    bpe = len(instructions)
    instructions.append(Instruction(getBranchType(), res, '','')) 
    tokens.pop(0)
    stmt(tokens)
    bpo = len(instructions)
    instructions.append(Instruction('br', '','',''))
    backpatchOut(bpe)
    res = selstmtprime(tokens)
    if res:
        backpatchOut(bpo)
    else:
        instructions.pop()
        backpatchOut(bpe)

def selstmtprime(tokens):
    if tokens[0][0] == 'else':
        tokens.pop(0)
        stmt(tokens)
        return 1
    else:
        return 0

def iterstmt(tokens):
    tokens.pop(0)
    tokens.pop(0)
    bpw = len(instructions) + 1
    res = exp(tokens)
    bpo = len(instructions)
    instructions.append(Instruction(getBranchType(), res, '', '')) 
    tokens.pop(0)
    stmt(tokens)
    instructions.append(Instruction('br', '', '', str(bpw)))
    backpatchOut(bpo)

def retstmt(tokens):
    tokens.pop(0)
    retstmtprime(tokens)

def expstmt(tokens):
    if tokens[0][0] == ';':
        tokens.pop(0)
        return
    else:
        exp(tokens)
        tokens.pop(0)

def retstmtprime(tokens):
    if tokens[0][0] == ';':
        tokens.pop(0)
        instructions.append(Instruction('return','','', '')) 
        return
    else:
        res = exp(tokens)
        tokens.pop(0)
        instructions.append(Instruction('return','','', res))
   
def exp(tokens):
    if tokens[0][0] == '(':
        tokens.pop(0)
        res = exp(tokens)
        tokens.pop(0)
        termleft = termprime(tokens, res)
        sum = addexpprime(tokens, termleft if termleft else res)
        simpcomp = simpexpprime(tokens, sum if sum else termleft if termleft else res)
        return simpcomp if simpcomp else sum if sum else termleft if termleft else res
    if tokens[0][1] == 'num':
        arg1 = tokens.pop(0)[0]
        termleft = termprime(tokens, arg1)
        sum = addexpprime(tokens, termleft if termleft else arg1)
        simpcomp = simpexpprime(tokens, sum if sum else termleft if termleft else arg1)
        return simpcomp if simpcomp else sum if sum else termleft if termleft else arg1
    if tokens[0][1] == 'id':
        arg1 = tokens.pop(0)[0]
        return expprime(tokens, arg1)

def expprime(tokens, id):
    if tokens[0][0] == '(':
        tokens.pop(0)
        args(tokens)
        tokens.pop(0)
        instructions.append(Instruction('call', id,'0',genTemp()))
        left = instructions[-1].result
        termleft = termprime(tokens, left)
        sum = addexpprime(tokens, termleft if termleft else left)
        simpcomp = simpexpprime(tokens, sum if sum else termleft if termleft else left)
        return simpcomp if simpcomp else sum if sum else termleft if termleft else left
    else:
        res = varprime(tokens)
        disp = 0
        if res:
            instructions.append(Instruction('disp', id, res, genTemp()))
            disp = instructions[-1].result
        return expdoubleprime(tokens, disp if disp else id)

def expdoubleprime(tokens, left):
    if tokens[0][0] == '=':
        tokens.pop(0)
        res = exp(tokens)
        instructions.append(Instruction('asgn', res, '', left))
        return res
    else:
        termleft = termprime(tokens, left)
        sum = addexpprime(tokens, termleft if termleft else left)
        simpcomp = simpexpprime(tokens, sum if sum else termleft if termleft else left)
        return simpcomp if simpcomp else sum if sum else termleft if termleft else left

def varprime(tokens): 
    if tokens[0][0] == '[':
        tokens.pop(0)
        res = exp(tokens)
        tokens.pop(0)
        instructions.append(Instruction('mult', res, '4', genTemp() ))
        return instructions[-1].result
    
def simpexpprime(tokens, left):
    global relopsymbol
    if tokens[0][0] in ['>','<','>=','<=','!=','==']:
        relopsymbol = relop(tokens)
        leftfactor = factor(tokens)
        termleft = termprime(tokens, leftfactor)
        sum = addexpprime(tokens, termleft if termleft else leftfactor)        
        instructions.append(Instruction('comp', left, sum if sum else termleft if termleft else leftfactor, genTemp()))
        return instructions[-1].result

def relop(tokens):
    return tokens.pop(0)[0]

def addexpprime(tokens, left):
    if tokens[0][0] in ['+','-']:
        addsymbol = addop(tokens)
        leftfactor = factor(tokens)
        right = termprime(tokens, leftfactor)
        instructions.append(Instruction('add' if addsymbol == '+' else 'sub', left, right if right else leftfactor, genTemp()))
        addexpprime(tokens, instructions[-1].result)
        return instructions[-1].result

def addop(tokens):
    return tokens.pop(0)[0]

def termprime(tokens, left):
    if tokens[0][0] in ['*','/']:
        multsymbol = mulop(tokens)
        right = factor(tokens)
        instructions.append(Instruction('mult' if multsymbol == '*' else 'div', left, right, genTemp()))
        termprime(tokens, instructions[-1].result)
        return instructions[-1].result

def mulop(tokens):
    return tokens.pop(0)[0]

def factor(tokens):
    if tokens[0][0] == '(':
        tokens.pop(0)
        res = exp(tokens)
        tokens.pop(0)
        return res
    if tokens[0][1] == 'num':
        return tokens.pop(0)[0]
    else:
        id = tokens.pop(0)[0]
        res = factorprime(tokens, id)
        return res if res else id

def factorprime(tokens, id):
    if tokens[0][0] == '(':
        tokens.pop(0)
        args(tokens)
        tokens.pop(0)
        instructions.append(Instruction('call', id,'0',genTemp()))
        return instructions[-1].result
    else:
        res = varprime(tokens)
        disp = 0
        if res:
            instructions.append(Instruction('disp', id, res, genTemp()))
            disp = instructions[-1].result
        return disp
 
def args(tokens):
    if tokens[0][0] != ')':
        res = exp(tokens)
        instructions.append(Instruction('arg','','',res))
        arglistprime(tokens)

def arglistprime(tokens):
    if tokens[0][0] == ',':
        tokens.pop(0)
        res = exp(tokens)
        instructions.append(Instruction('arg','','',res))
        arglistprime(tokens)        
