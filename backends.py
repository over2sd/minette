#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

import codecs
import re
import os
from status import status
from common import (say,bsay,skrTimeStamp,findFile)
from debug import (printPretty,lineno)
from globdata import (config,worldList,cfgkeys,rlmkeys,defaults)
# from configobj import ConfigObj

def criticalDefaults():
  missing = {}
  try:
    if not defaults.get("set",False):
      setDefaults()
  except NameError:
    setDefaults()
  critical = []
  for key in cfgkeys:
    critical.append(key)
  for key in rlmkeys:
    critical.append(key)
  for key in critical:
    try:
      x = config[key]
    except KeyError:
      missing[key] = defaults[key]
  return missing

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
        if values[0] in ["pos","size"]:
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
  fn = os.path.join(config['realmdir'],"myrealm.cfg")
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
  os.remove(os.path.join(os.path.abspath(config['realmdir']),"myrealm.cfg"))
  say("WorldList destroyed!")
  global status
  status.push(0,"WorldList destroyed!")

def killRealmOpts():
  for k in rlmkeys:
    del config[k]
  loadConfig(config.get("file",None),9)

def loadConfig(fn = None,recursion = 0):
  """Returns a dict containing the config options in the Minette config file."""
  maxrecursion = 3
  lines = []
  global config
  global defaults
  if fn is None:
    fn = "default.cfg" # using 3-letter extension for MSWin compatibility, I hope.
  (found,fn) = findFile(lineno(),fn)
  if not found:
    print " [W] Config %s not loaded." % fn
    if not defaults.get("set",False):
      setDefaults()
    config.update(defaults)
    return config
  lines = readfile(fn)
  for line in lines:
    try:
      line = line.strip()
      if line:
        values = [x.strip() for x in line.split('=')]
        if values[0] != "loadconfig":
          if not config.get(values[0]): config[values[0]] = values[1] # existing options will not be clobbered
        elif recursion < maxrecursion and os.path.exists(values[1]): # loadconfig must be first option, or its options may be ignored.
          recursion += 1
          loadConfig(values[1],recursion)
    except Exception as e:
      print " [E] There was an error in the configuration file: %s" % e
  config['file'] = fn
  config = validateConfig(config)
  if len(config.get("realmfile","")) > 0 and recursion <= maxrecursion:
    rf = "realms/%s.rlm" % config['realmfile']
    realm = loadRealm(rf)
    config.update(realm)
  else:
    config['realmloaded'] = False
  config.update(criticalDefaults())
  return config

def loadRealm(fn = None,recursion = 0):
  """Returns a dict containing the config options in the Minette realm file."""
  maxrecursion = 3
  lines = []
  realm = {}
  realm['realmloaded'] = False
  if fn is None or fn == "":
    print "Could not load realm information. No filename provided!"
    exit(-1)
  (found,fn) = findFile(lineno(),fn)
  if not found:
    print " [W] Realm %s not loaded." % fn
    return realm
  lines = readfile(fn)
  for line in lines:
    try:
      line = line.strip()
      if line:
        values = [x.strip() for x in line.split('=')]
        if values[0] != "likerealm":
          realm[values[0]] = values[1] # unlike config, existing realm options WILL be clobbered
        elif recursion < maxrecursion: # likerealm must be first option, or it may clobber options for the parent realm.
          rf = "realms/%s.rlm" % values[1]
          recursion += 1
          realm.update(loadRealm(rf,recursion))
    except Exception as e:
      print "There was an error in the realm file: %s" % e
  fn = realm.get("realmdir","")
  (found,fn) = findFile(lineno(),fn)
  if not found:
    print " [E] Fatal error. Realm directory %s not found!" % fn
    exit(-1)
  realm = validateRealm(realm)
  realm['realmloaded'] = True
  return realm

def saveConfig(fn):
  if not defaults.get("set",False):
    setDefaults()
  lines = []
  for key in config.keys():
    if (key in cfgkeys or config['rlmincfg']) and config[key] != defaults.get(key):
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
  defaults['agedate'] = "06/08/10b" # Date for calculating ages
  defaults['centbreak'] = 69
  defaults['century'] = 2000
  defaults['datestyle'] = "%y/%m/%db" # Style of date output, Assumed century for 2-digit years, earliest year of previous century
  defaults['debug'] = 0
  defaults['dtddir'] = "dtd/" # Where are doctype defs kept?
  defaults['dtdurl'] = os.path.join("../../",defaults['dtddir']) # What reference goes in the XML files?
  defaults['duplicatetabs'] = False # Should we open duplicate tabs?
  defaults['familyfirst'] = False # Does the family name come first?
  defaults['hideage'] = False # Show only the calculated age, hiding freetext entry?
  defaults['informat'] = "xml" # input format
  defaults['matchlike'] = 2 # Write options from 'likerealm'? 2: write all options to realm; 1: write only options that differ from likerealm target; 0: Keep track of which options came from likerealm and don't write those
  defaults['outformat'] = "xml" # output format
  defaults['pos'] = (20,40) # Default window position and size, debug level
  defaults['printemptyXMLtags'] = False # output includes <emptyelements />?
  defaults['realmdir'] = "realms/default/" # Where should I look for XML files and configs?
  defaults['realmfile'] = "default" # Which realm file should I load by default?
  defaults['realmname'] = "Unnamed Setting" # What should I call the setting/world/realm?
  defaults['rlmincfg'] = False # Allow realm-specific items in config file? (will act as defaults)
  defaults['saverealm'] = False # Save realm on exit?
  defaults['seenfirstrun'] = False # Seen the first-run tutorial?
  defaults['showstories'] = "idlist" # Show titles, or just reference codes?
  defaults['size'] = (620,440)
  defaults['specialrelsonly'] = False # use only realm-defined relations?
  defaults['startnewperson'] = False # Start by opening a new person file?
  defaults['termcolors'] = False # Use ANSI codes in debug output?
  defaults['uselistfile'] = True # Whether to save/load a list file instead of walking through each XML file to determine its class (saves load time/disk writes, but requires keeping the list file up to date).
  defaults['usemiddle'] = True # Does the name include a middle or maiden name?
  defaults['xslurl'] = "xsl/" # What reference goes in the XML files?

  defaults['set'] = True

def validateConfig(config):
  """Checks some config values for validity. Returns adjusted dictionary."""
  try:
    if not defaults.get("set",False):
      setDefaults()
  except NameError:
    setDefaults()
  keylist = []
  keylist.extend(cfgkeys)
  if config.get("rlmincfg",False):
    keylist.extend(rlmkeys)
  for key in keylist:
    config[key] = config.get(key,defaults[key])
    if config[key] == "True": config[key] = True
    if config[key] == "False": config[key] = False
  pos = config.get("pos",defaults['pos']) # default position
  siz = config.get("size",defaults['size']) # default size
  pattern = re.compile(r'\(\s?(\d+)\s?,\s?(\d+)\s?\)')
  match = False
  if pos == str(pos): # otherwise, must be reloading config, no need to reprocess
    match = pattern.search(pos)
  if match:
    config['pos'] = (int(match.group(1)),int(match.group(2)))
  else:
    config['pos'] = (0,0)
  match = False
  if siz == str(siz): # otherwise, must be reloading config, no need to reprocess
    match = pattern.search(siz)
  if match:
    config['size'] = (int(match.group(1)),int(match.group(2)))
  else:
    config['size'] = (620,440)
  keys = ["debug","matchlike",]
  for k in keys:
    config[k] = int(config.get(k,0))
  return config

def validateRealm(realm):
  for key in realm.keys():
    if key not in rlmkeys: # Only allow keys in the realm-specific keys list
      del realm[key]
  for key in rlmkeys:
    # XML file options
    if key == "dtdurl":
      realm['dtdurl'] = realm.get(key,os.path.abspath(realm['dtddir']))
    # other options
    else:
      realm[key] = realm.get(key,defaults[key])
      if realm[key] == "True": realm[key] = True
      if realm[key] == "False": realm[key] = False
  if not os.path.exists(os.path.abspath(realm['realmdir'])): # must be a valid directory
    bsay("?","Fatal error. Realm directory %s does not exist! Exiting." % os.path.abspath(realm['realmdir']))
    exit(-1)
  return realm

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
  if config['informat'] == "sql":
    backsql.idExists(fileid,rectyp)
  else:
    backxml.idExists(fileid)

def listRealms():
  rlist = os.listdir("realms/")
  olist = []
  for r in rlist:
    if ".rlm" in r:
      olist.append(r[:-4])
  if config['debug'] > 0: printPretty(olist)
  return olist

def listThingsGTK(caller,pretty = 1):
  if config['informat'] == "sql":
    backsql.listThings(pretty)
  else:
    backxml.listThings(pretty)

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