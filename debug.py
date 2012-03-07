import traceback
import os

def printStack(length = 3):
  stack = traceback.extract_stack()
  start = -2 - length
  for item in stack[start:-2]: # give three lines, trimming call to this function and stack = extract_stack
    p,f = os.path.split(item[0])
    ln = item[1]
    func = item[2]
    cmd = item[3]
    print "* At line %d in %s:%s():\n\t%s" % (ln,f,func,cmd)
