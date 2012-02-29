#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

import codecs
import re
import os
from linecache import getline
from status import status
from common import (say,bsay,skrTimeStamp)
from globdata import (config,worldList)
import xmlout
# from configobj import ConfigObj

def storeWindowExit(caller,window):
  storeWindow(caller,window)
  window.destroy()

def storeWindow(caller,window):
  """Checks current window size against stored value in memory. If
  different, Checks for the existence of the config file, and if it
  exists, deletes old window definitions and writes a new set. Requires
  window argument specifying widget to read size/location info.
  """
  global config
  if config.get("nowindowstore"): return # Allow config option to disable this behavior
  (x, y) = window.get_position()
  (w, h) = window.get_size()
  if config['pos'] == (x,y) and config['size'] == (w,h):
    if config['debug'] > 0:
      print "Window not moved/resized. Keeping existing values."
    return
  lines = []
  found = []
  if os.path.exists(os.path.abspath(config['file'])): # Don't create a config file if it doesn't exist.
    try:
      with codecs.open(os.path.abspath(config['file']),'rU','utf-8') as conf:
        lines = conf.readlines()
        conf.close()
    except IOError as e:
      print " Could not read configuration file: %s" % e
      return
    if config['debug'] > 3: print str(lines) + "\n"
    i = 0
    for line in lines:
      line = line.strip()
      if line:
        values = [a.strip() for a in line.split('=')]
        if values[0] == "pos":
          found.append(i)
        if values[0] == "size":
          found.append(i)
      i += 1
    if len(found):
      found.sort()
      found.reverse()
      for i in found:
        del lines[i]
    lines.append("pos = (%s,%s)\n" % (x,y))
    lines.append("size = (%s,%s)\n" % (w,h))
    if config['debug'] > 3: print lines
    try:
      f = open(os.path.abspath(config['file']), 'w')
      f.writelines(lines)
      f.close()
    except IOError as e:
      print " Could not write configuration file: %s" % e
      return
    print "Saving window: %s,%s; %sx%s" % (x,y,w,h)
  else:
    print "No config file. Not saving window."

def writeListFile():
  global worldList
  global config
  persons = worldList['p']
  places = worldList['l']
  cities = worldList['c']
  states = worldList['s']
  orgs = worldList['o']
  fn = os.path.join(config['worlddir'],"myworld.cfg")
  try:
    with codecs.open(fn,'wU','utf-8') as conf:
      puts = []
      puts.append("persons = " + ','.join(persons))
      puts.append("\nplaces = " + ','.join(places))
      puts.append("\ncities = " + ','.join(cities))
      puts.append("\nstates = " + ','.join(states))
      puts.append("\norgs = " + ','.join(orgs))
      puts.append("\n")
      conf.writelines(puts)
      conf.close()
  except IOError as e:
    print " Could not write worldlist file: %s" % e
    exit(1)

def killListFile(caller = None):
  os.remove(os.path.join(os.path.abspath(config['worlddir']),"myworld.cfg"))
  say("WorldList destroyed!")
  global status
  status.push(0,"WorldList destroyed!")

def loadConfig(fn = None,recursion = 0):
  """Returns a dict containing the config options in the CCOW config file."""
  lines = []
  global config
  config['debug'] = 1
  if fn is None:
    fn = "default.cfg" # using 3-letter extension for MSWin compatibility, I hope.
  lines = readfile(fn)
  for line in lines:
    try:
      line = line.strip()
      if line:
        values = [x.strip() for x in line.split('=')]
        if values[0] != "loadworld":
          if not config.get(values[0]): config[values[0]] = values[1] # existing options will not be clobbered
        elif recursion < 2 and os.path.exists(values[1]): # loadworld must be first option, or its options may be ignored.
          recursion += 1
          loadConfig(values[1],recursion)
    except Exception as e:
      print "There was an error in the configuration file: %s" % e
  config['file'] = fn
  config = validateConfig(config)
  return config

def validateConfig(config):
  """Checks some config values for validity. Returns adjusted dictionary."""
  pos = config.get("pos","(0,0)") # default position
  siz = config.get("size","(620,440)") # default size
  pattern = re.compile(r'\(\s?(\d+)\s?,\s?(\d+)\s?\)')
  match = pattern.search(pos)
  if match:
    config['pos'] = (int(match.group(1)),int(match.group(2)))
  else:
    config['pos'] = (0,0)
  match = pattern.search(siz)
  if match:
    config['size'] = (int(match.group(1)),int(match.group(2)))
  else:
    config['size'] = (620,440)
  config['debug'] = config.get("debug","0")
  config['informat'] = config.get("informat","xml") # How are people stored initially?
  config['outformat'] = config.get("outformat","xml") # how will we save data?
  config['openduplicatetabs'] = config.get('openduplicatetabs',False) # Should we open duplicate tabs?
  config['worlddir'] = config.get("worlddir","worlds/example/") # Where should I look for XML files and configs?
# Person options
  config['familyfirst'] = config.get("familyfirst",False) # Does the family name come first?
  config['usemiddle'] = config.get("usemiddle",True) # Does the name include a middle or maiden name?
  config['startnew'] = config.get("startnew",False) # Start by opening a new person file?
  config['specialrelsonly'] = config.get("specialrelsonly",False) # use only world-defined relations?
  config['showstories'] = config.get("showstories","idlist") # Show titles, or just reference codes?
# XML file options
  config['uselistfile'] = config.get("uselistfile",True) # Whether to...
  """ save/load a list file instead of walking through each XML file
  to determine its class (saves load time/disk writes, but requires
  keeping the list file up to date).
  """
  config['printemptyXMLtags'] = config.get("printemptyXMLtags",False) # output includes <emptyelements />?
  config['dtddir'] = config.get("dtddir","dtd/") # Where are doctype defs kept?
  config['dtdurl'] = config.get("dtdurl",os.path.abspath(config['dtddir'])) # What reference goes in the XML files?
  config['xslurl'] = config.get("xslurl",os.path.abspath("xsl/")) # What reference goes in the XML files?
  return config

### Wrappers
def getCityList(order = 0):
  if config['informat'] == "sql":
    return backsql.getCityList(order)
  else:
    return backxml.getCityList(order)

def idExists(fileid,rectyp):
  global config
  if config['informat'] == "sql":
    backsql.idExists(fileid,rectyp)
  else:
    backxml.idExists(fileid)

def loadPerson(fileid):
  global config
  if config['informat'] == "sql":
    return backsql.loadPerson(fileid)
  else:
    return backxml.loadPerson(fileid)

def loadPlace(fileid):
  global config
  if config['informat'] == "sql":
    return backsql.loadPlace(fileid)
  else:
    return backxml.loadPlace(fileid)

def populateWorld():
  global config
  if config['informat'] == "sql":
    backsql.populateWorld()
  else:
    backxml.populateWorld()

def readfile(fn,verbose = True):
  lines = []
  if os.path.exists(os.path.abspath(fn)):
    try:
      with codecs.open(os.path.abspath(fn),'rU','utf-8') as f:
        lines = f.readlines()
        f.close()
    except IOError as e:
      if verbose: bsay(None, " Could not open file: %s" % e)
    status.push(0,"File read successfully: %s" % fn)
  else:
    if verbose: bsay(None,"File not found: %s" % fn)
  return lines

def savePerson(fileid,data):
  global config
  if config['outformat'] == "sql":
    return backsql.savePerson(fileid,data)
  else:
    return backxml.savePerson(fileid,data)

def savePlace(fileid,data):
  global config
  if config['outformat'] == "sql":
    return backsql.savePlace(fileid,data)
  else:
    return backxml.savePlace(fileid,data)

def writefile(fn,lines,create = False):
  if create or os.path.exists(os.path.abspath(fn)):
    try:
      f = codecs.open(os.path.abspath(fn),'wU',"UTF-8")
      f.writelines(lines)
      f.close()
    except IOError as e:
      bsay(None, " Could not write story file: %s" % e)
      return
    status.push(0,"%s written successfully." % fn)
  else:
    bsay("File not found and not created: %s" % fn)

### XML Backend
import backxml

### SQL Backend
# import backsql