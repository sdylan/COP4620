from display import printRules, printTokens

def getRules(file, adict, orderlist):
    
    lines = open(file)
    
    for line in lines:
        parts = line.split('?')
    
        producer = parts[0].strip()
        if producer not in orderlist:
            orderlist.append(producer)
        if producer not in adict:
            a = [parts[1].strip()]
            adict[producer] = a
        else:
            adict[producer].append(parts[1].strip())

def menu(rulesFirst, rulesFollow, order, parseTree, parse, parsingTable, displist):
    print
    print
    print '1. Print grammar, firsts and follows.'
    print '2. Print parse tree.'
    print '3. Print parse.'
    print '4. Print tokens.'
    print '5. Quit.'
    input = raw_input('\n\t\tChoose Selection: ')
    
    while input is not '5':
        if input is '1':
            printRules(rulesFirst, rulesFollow, order)
        elif input is '2':
            parseTree.printTree()
        elif input is '3':
            print
            print
            for i in parse:
                print '{:25} {}'.format(i, (parsingTable[i] if isinstance(i, tuple) else ''))
        elif input is '4':
            printTokens(displist) 
        else:
            input = raw_input('\t\t A number [1-5]: ')
            continue
        print
        print
        print '1. Print grammar, firsts and follows.'
        print '2. Print parse tree.'
        print '3. Print parse.'
        print '4. Print tokens.'
        print '5. Quit.'
        input = raw_input('\n\t\tChoose Selection: ')

def exportTable(parsingTable):
    file = open('parsingTable.csv', 'w')
    for k, v in parsingTable.items():
        line = '{}?{}?{}\n'.format(k[0], k[1], v)
        file.write(line)
    file.close()    
