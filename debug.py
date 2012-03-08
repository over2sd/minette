#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

import traceback
import os

def printStack(length = 3,callonly = False):
  stack = traceback.extract_stack()
  start = -2 - length
  for item in stack[start:-2]: # give three lines, trimming call to this function and stack = extract_stack
    p,f = os.path.split(item[0])
    ln = item[1]
    func = item[2]
    cmd = item[3]
    if callonly:
      print "* %s:" % cmd
    else:
      print "* At line %d in %s:%s():\n\t%s" % (ln,f,func,cmd)

def printPretty(string,quiet = True):
  """This function prints Python variable/string in colored format in bash/ANSI
  terminal. It makes some broad assumptions that won't always work, particularly,
  that you won't pass it a string containing special Python characters. If you do,
  it will simply put that character in its special color, and you may become confused.
  """
  printStack(1,quiet) # Say what we're printing
  string = str(string) # Treat this as a string, even if it's not, which it usually won't be
  NORM = '\033[0;37;40m' # normal gray
  BRACE = '\033[32;40m' # green
  LIST = '\033[35;40m' # purple
  ANGLES = '\033[31;40m' # red
  COLON = '\033[36;40m' # cyan
  EQ = '\033[1;34;40m' # bold blue
  COMMA = '\033[1;33;40m' # bold yellow
  print NORM,
  output = ""
  depth = 0
  un = 2
  b = ""
  for c in string:
    if c == '{':
      depth += un
      output += "%s\n%s " % (BRACE + c + NORM,pad(depth))
    elif c == '}':
      output += "\n%s%s" % (pad(depth),BRACE + c + NORM)
      depth -= un
    elif c == '[':
      depth += un
      output += "%s" % (LIST + c + NORM)
    elif c == ']':
      depth -= un
      output += "%s" % (LIST + c + NORM)
    elif c == ',' and b in ['}',']']:
      output += "%s\n%s" % (c,pad(depth))
    elif c == ',':
      output += "%s" % (COMMA + c + NORM)
    elif c in ['<','>']:
      output += "%s" % ANGLES + c + NORM
    elif c == ':':
      output += "%s" % COLON + c + NORM
    elif c == '=':
      output += "%s" % EQ + c + NORM
    else:
      output += c
    b = str(c)
  print output

def pad(depth):
  sp = ""
  for i in range(depth):
    sp += ' '
  return sp