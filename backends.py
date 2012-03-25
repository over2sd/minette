#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

import codecs
import re
import os
from status import status
from common import (say,bsay,skrTimeStamp)
from globdata import (config,worldList)
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

def saveConfig(fn):
  try:
    if not defaults.get("set",False):
      setDefaults()
  except NameError:
    setDefaults()
  lines = []
  for key in config.keys():
    if key is not "file" and key is not "set" and config[key] != defaults.get(key):
      lines.append("%s = %s\n" % (key,config[key]))
  if config['debug'] > 0: print lines
  try:
    f = open(os.path.abspath(fn), 'w')
    f.writelines(lines)
    f.close()
  except IOError as e:
    print " Could not write configuration file: %s" % e

def setDefaults():
  global defaults
  defaults = {}
  defaults['pos'] = "(20,40)" # Default window position and size, debug level
  defaults['size'] = "(620,440)"
  defaults['debug'] = "0"
  defaults['familyfirst'] = False # Does the family name come first?
  defaults['usemiddle'] = True # Does the name include a middle or maiden name?
  defaults['startnewperson'] = False # Start by opening a new person file?
  defaults['specialrelsonly'] = False # use only world-defined relations?
  defaults['showstories'] = "idlist" # Show titles, or just reference codes?
  defaults['informat'] = "xml" # input/output formats
  defaults['outformat'] = "xml"
  defaults['openduplicatetabs'] = False # Should we open duplicate tabs?
  defaults['worlddir'] = "worlds/example/" # Where should I look for XML files and configs?
  defaults['datestyle'] = "%y/%m/%db" # Style of date output, Assumed century for 2-digit years, earliest year of previous century
  defaults['century'] = 2000
  defaults['centbreak'] = 69
  defaults['uselistfile'] = True # Whether to...
  """ save/load a list file instead of walking through each XML file
  to determine its class (saves load time/disk writes, but requires
  keeping the list file up to date).
  """
  defaults['printemptyXMLtags'] = False # output includes <emptyelements />?
  defaults['dtddir'] = "dtd/" # Where are doctype defs kept?
  defaults['dtdurl'] = os.path.abspath(defaults['dtddir']) # What reference goes in the XML files?
  defaults['xslurl'] = os.path.abspath("xsl/") # What reference goes in the XML files?

  defaults['set'] = True

def validateConfig(config):
  """Checks some config values for validity. Returns adjusted dictionary."""
  try:
    if not defaults.get("set",False):
      setDefaults()
  except NameError:
    setDefaults()
  configs = ["pos","size","debug", "informat", "outformat", "openduplicatetabs", "worlddir", "datestyle", "century", "centbreak"]
  for key in configs:
    config[key] = config.get(key,defaults[key])
  if not os.path.exists(os.path.abspath(config['worlddir'])): # must be a valid directory
    bsay("?","Fatal error. World directory %s does not exist! Exiting." % config['worlddir'])
    exit(-1)
  pos = config.get("pos",defaults['pos']) # default position
  siz = config.get("size",defaults['size']) # default size
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
# Person options
  configs = ["familyfirst","usemiddle","specialrelsonly","showstories","startnewperson"]
  for key in configs:
    config[key] = config.get(key,defaults[key])
# XML file options
  configs = ["uselistfile","printemptyXMLtags","dtddir","dtdurl","xslurl"]
  for key in configs:
    if key == "dtdurl":
      config['dtdurl'] = config.get(key,os.path.abspath(config['dtddir'])) # What reference goes in the XML files?
    else:
      config[key] = config.get(key,defaults[key])
  return config

### Wrappers
def getCitiesIn(state):
  if config['informat'] == "sql":
    return backsql.getCitiesIn(state)
  else:
    return backxml.getCitiesIn(state)

def getCityList(order = 0):
  if config['informat'] == "sql":
    return backsql.getCityList(order)
  else:
    return backxml.getCityList(order)

def getPlacesIn(city):
  if config['informat'] == "sql":
    return backsql.getPlacesIn(city)
  else:
    return backxml.getPlacesIn(city)

def getPlaceList(pretty = 1):
  if config['informat'] == "sql":
    return backsql.getPlaceList(pretty)
  else:
    return backxml.getPlaceList(pretty)

def getPlaceListGTK(caller,pretty = 1):
  return getPlaceList(pretty)

def getStateList(order = 0):
  if config['informat'] == "sql":
    return backsql.getStateList(order)
  else:
    return backxml.getStateList(order)

def idExists(fileid,rectyp):
  global config
  if config['informat'] == "sql":
    backsql.idExists(fileid,rectyp)
  else:
    backxml.idExists(fileid)

def loadCity(fileid):
  global config
  if config['informat'] == "sql":
    return backsql.loadCity(fileid)
  else:
    return backxml.loadCity(fileid)

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

def loadState(fileid):
  global config
  if config['informat'] == "sql":
    return backsql.loadState(fileid)
  else:
    return backxml.loadState(fileid)

def populateWorld():
  if config['informat'] == "sql":
    backsql.populateWorld()
  else:
    backxml.populateWorld()

def pushLoc(statefile,statename = "",cityfile = "",cityname = "",placefile = "",placename = ""):
  if config['informat'] == "sql":
    backsql.pushLoc(statefile,statename,cityfile,cityname,placefile,placename)
  else:
    backxml.pushLoc(statefile,statename,cityfile,cityname,placefile,placename)

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

def saveCity(fileid,data):
  global config
  success = False
  if config['outformat'] == "sql":
    success = backsql.saveCity(fileid,data)
  else:
    success = backxml.saveCity(fileid,data)
  if success and fileid not in worldList['c']:
    worldList['c'].append(fileid)
    writeListFile()
  return success

def savePerson(fileid,data):
  global config
  success = False
  if config['outformat'] == "sql":
    success = backsql.savePerson(fileid,data)
  else:
    success = backxml.savePerson(fileid,data)
  if success and fileid not in worldList['p']:
    worldList['p'].append(fileid)
    writeListFile()
  return success

def savePlace(fileid,data):
  global config
  success = False
  if config['outformat'] == "sql":
    success = backsql.savePlace(fileid,data)
  else:
    success = backxml.savePlace(fileid,data)
  if success and fileid not in worldList['l']:
    worldList['l'].append(fileid)
    writeListFile()
  return success

def saveState(fileid,data):
  global config
  success = False
  if config['outformat'] == "sql":
    success = backsql.saveState(fileid,data)
  else:
    success = backxml.saveState(fileid,data)
  if success and fileid not in worldList['s']:
    worldList['s'].append(fileid)
    writeListFile()
  return success

def updateLocs(cityname,locfile,statefile):
  if config['informat'] == "sql":
    backsql.updateLocs(cityname,locfile,statefile)
  else:
    backxml.updateLocs(cityname,locfile,statefile)

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