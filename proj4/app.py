from reglex import *
from rdparser import *
from sys import argv

tokens = getTokens(argv[1])
driver(tokens)
