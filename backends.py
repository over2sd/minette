#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

config = {}
worldList = {}
relsP = {}

import codecs
import re
import os
from linecache import getline
from status import status
from common import say
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

def getRelsP(pgender,rgender):
  global relsP
  if not len(relsP):
    print "Loading people relations for the first time."
#    r = ConfigOb(os.path.abspath("peopleconnections.ini"))
# TODO: INI file import
    # Some day, pull these values from a backend
    relsP['relsnn'] = { # [autoreverse,rtype]
      '101':['Friend','Friend','friend',"nn"],
      '102':['Boss',"Subordinate",'work',"nn"],
      '103':['Subordinate','Boss','work',"nn"],
      '104':['Running Partner','Running Partner','casual',"nn"],
      '105':['Sibling','Sibling','fam',"nn"],
      '106':['Cousin','Cousin','fam',"nn"],
    }
    relsP['relsnf'] = {
'107':['Sister','Sibling','fam',"nf"],
'108':['Mother','Child','fam',"nf"],
'109':['Sister-in-law','Sibling-in-law','fam',"nf"],
'110':['Mother-in-law','Child-in-law','fam',"nf"],
'111':['Stepsister','Stepsibling','fam',"nf"],
'112':['Stepmother','Stepchild','fam',"nf"],
    }
    relsP['relsnm'] = {
'113':['Brother','Sibling','fam',"nm"],
'114':['Father','Child','fam',"nm"],
'115':['Brother-in-law','Sibling-in-law','fam',"nm"],
'116':['Father-in-law','Child-in-law','fam',"nm"],
'117':['Stepbrother','Stepsibling','fam',"nm"],
'118':['Stepfather','Stepchild','fam',"nm"],
    }
    relsP['relsmf'] = {
'119':['Lover','Lover','other',"mf"],
'120':['Wife','Husband','fam',"mf"],
'121':['Sister','Brother','fam',"mf"],
'122':['Mother','Son','fam',"mf"],
'123':['Sister-in-law','Brother-in-law','fam',"mf"],
'124':['Mother-in-law','Son-in-law','fam',"mf"],
'125':['Stepsister','Stepbrother','fam',"mf"],
'126':['Stepmother','Stepson','fam',"mf"],
    }
    relsP['relsfm'] = {
'127':['Lover','Lover','other',"fm"],
'128':['Husband','Wife','fam',"fm"],
'129':['Brother','Sister','fam',"fm"],
'130':['Father','Daughter','fam',"fm"],
'131':['Brother-in-law','Sister-in-law','fam',"fm"],
'132':['Father-in-law','Daughter-in-law','fam',"fm"],
'133':['Stepbrother','Stepsister','fam',"fm"],
'134':['Stepfather','Stepdaughter','fam',"fm"],
    }
    relsP['relsff'] = {
'135':['Sister','Sister','fam',"fm"],
'136':['Mother','Daughter','fam',"fm"],
'137':['Sister-in-law','Sister-in-law','fam',"fm"],
'138':['Mother-in-law','Daughter-in-law','fam',"fm"],
'139':['Stepsister','Stepsister','fam',"fm"],
'140':['Stepmother','Stepdaughter','fam',"fm"],
    }
    relsP['relsmm'] = {
'141':['Brother','Brother','fam',"mm"],
'142':['Father','Son','fam',"mm"],
'143':['Brother-in-law','Brother-in-law','fam',"mm"],
'144':['Father-in-law','Son-in-law','fam',"mm"],
'145':['Stepbrother','Stepbrother','fam',"mm"],
'146':['Stepfather','Stepson','fam',"mm"],
    }

  if pgender == 'n' and rgender == 'f':
    return relsP['relsnf']
  elif pgender == 'f' and rgender == 'f':
    return relsP['relsff']
  elif pgender == 'm' and rgender == 'f':
    return relsP['relsmf']
  elif pgender == 'n' and rgender == 'm':
    return relsP['relsnm']
  elif pgender == 'f' and rgender == 'm':
    return relsP['relsfm']
  elif pgender == 'm' and rgender == 'm':
    return relsP['relsmm']
  else:
    return relsP['relsnn']


def loadConfig(fn = None):
  """Returns a dict containing the config options in the CCOW config file."""
  lines = []
  global config
  config['debug'] = 1
  if fn is None:
    fn = "default.cfg" # using 3-letter extension for MSWin compatibility, I hope.
  if os.path.exists(os.path.abspath(fn)):
    try:
      with codecs.open(os.path.abspath(fn),'rU','utf-8') as conf:
        lines = conf.readlines()
        conf.close()
    except IOError as e:
      print " Could not open configuration file: %s" % e
  for line in lines:
    try:
      line = line.strip()
      if line:
        values = [x.strip() for x in line.split('=')]
        config[values[0]] = values[1]
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
# Person options
  config['familyfirst'] = config.get("familyfirst",False) # Does the family name come first?
  config['usemiddle'] = config.get("usemiddle",True) # Does the name include a middle or maiden name?
  config['startnew'] = config.get("startnew",False) # Start by opening a new person file?
# XML file options
  config['uselistfile'] = config.get("uselistfile",True) # Whether to...
  """ save/load a list file instead of walking through each XML file
  to determine its class (saves load time/disk writes, but requires
  keeping the list file up to date).
  """
  config['xmldir'] = config.get("xmldir","worlds/default/") # Where should I look for XML files?
  config['dtddir'] = config.get("dtddir","dtd/") # Where are doctype defs kept?
  config['dtdurl'] = config.get("dtdurl",os.path.abspath(config['dtddir'])) # What reference goes in the XML files?
  config['xslurl'] = config.get("xslurl",os.path.abspath("xsl/")) # What reference goes in the XML files?
  return config

### Wrappers
def loadPerson(fileid):
  global config
  if config['informat'] == "sql":
    return loadPersonSQL(fileid)
  else:
    return loadPersonXML(fileid)

def savePerson(fileid,data):
  global config
  if config['outformat'] == "sql":
    return savePersonSQL(fileid,data)
  else:
    return savePersonXML(fileid,data)

def populateWorld():
  global config
  if config['informat'] == "sql":
    populateWorldSQL()
  else:
    populateWorldXML()

def idExists(fileid,rectyp):
  global config
  if config['informat'] == "sql":
    idExistsSQL(fileid,rectyp)
  else:
    idExistsXML(fileid)

### XML Backend
import xml.etree.ElementTree as etree
#from xml.etree.ElementTree import (parse, Element)

def loadPersonXML(fileid):
  """Given an id (filename) matching an XML file in the appropriate
  directory, loads the tree from the file and pushes its data into
  two dictionaries, which it returns as a tuple.
  """
  dinf = {}
  drel = {}
  root = etree.Element("person")
  text = None
  dinf['abil'] = ["",False]
  dinf['age'] = ["",False]
  dinf['appear1ch'] = ["",False]
  dinf['appear1wr'] = ["",False]
  dinf['asmell'] = ["",False]
  dinf['attposs'] = ["",False]
  dinf['backstory'] = ["",False]
  dinf['bday'] = ["",False]
  dinf['bodytyp'] = ["",False]
  dinf['commonname'] = ["",False]
  dinf['conflict'] = ["",False]
  dinf['ctitle'] = ["",False]
  dinf['dday'] = ["",False]
  dinf['dress'] = ["",False]
  dinf['ethnic'] = ["",False]
  dinf['eyes'] = ["",False]
  dinf['gname'] = ["",False]
  dinf['gender'] = ["",False]
  dinf['hair'] = ["",False]
  dinf['hobby'] = ["",False]
  dinf['leadrel'] = ["",False]
  dinf['fname'] = ["",False]
  dinf['dmarks'] = ["",False]
  dinf['file'] = ["",False]
  dinf['mention'] = ["",False]
  dinf['minchar'] = ["",False]
  dinf['misc'] = ["",False]
  dinf['mname'] = ["",False]
  dinf['mole'] = ["",False]
  dinf['nname'] = ["",False]
  dinf['origin'] = ["",False]
  dinf['other'] = ["",False]
  dinf['personality'] = ["",False]
  dinf['residence'] = ["",False]
  dinf['sgoal'] = ["",False]
  dinf['skin'] = ["",False]
  dinf['speech'] = ["",False]
  dinf['stories'] = ["",False]
  dinf['strength'] = ["",False]
  dinf['talent'] = ["",False]
  dinf['weak'] = ["",False]
  dinf['update'] = ["",False]
  dinf['currocc'] = {}
  dinf['currocc']['pos'] = ["",False]
  dinf['formocc'] = {}
  dinf['formocc']['pos'] = ["",False]
  events = {}
  events['0'] = {}
  events['0']['date'] = ["",False]
  events['0']['event'] = ["",False]
  dinf['currocc']['events'] = events
  dinf['formocc']['events'] = events
  # if no relations, leave blank
  if not idExistsXML(fileid):
    status.push(0,"new person created... '" + fileid + "'")
    return (dinf,drel)
  fileid = os.path.join(config['xmldir'],fileid + ".xml")
  status.push(0,"loading person from XML... '" + fileid + "'")
  try:
    with codecs.open(fileid,'rU','utf-8') as f:
      tree = etree.parse(f)
      f.close()
      root = tree.getroot()
  except IOError as e:
    print " Could not open configuration file: %s" % e

  ir = 0
  for i in range(len(root)):
    if root[i].tag is not None:
      if root[i].tag == "relat":
        node = ""
        try:
          node = root[i].find("file").text.strip()
        except AttributeError:
          bsay("?","XML formatting error in %s! Probably an empty relat tag." % fileid)
        drel[node] = {}
        for j in root[i]:
          if j.tag == "events":
            if not drel[node].get('events'): drel[node]['events'] = {}
            for k in j:
              stone = str(len(drel[node]['events']))
              drel[node]['events'][stone] = {}
              for m in k:
                if m.tag and m.text:
                  drel[node]['events'][stone][m.tag] = [m.text.strip(),False]
          else: # elif j.tag != "file":
            if j.tag and j.text:
              drel[node][j.tag] = [j.text.strip(),False]
        if config['debug'] > 3: print drel[node]
      elif root[i].tag == "currocc":
#        print ",",
        dinf['currocc'] = {}
        try:
          dinf['currocc']['pos'] = [root[i].find("pos").text.strip(),False]
        except AttributeError:
          del dinf['currocc']
        if dinf.get('currocc'):
          events = {}
          if len(root[i]) > 1:
            for j in root[i]:
              if j.tag is not None:
                if j.tag == "events":
                  for k in j:
                    if k.tag == "mstone":
                      le = str(len(events))
                      events[le] = {}
                      events[le]['date'] = ["",False]
                      events[le]['event'] = ["",False]
                      for m in k:
                        if m.tag and m.text:
                          events[le][m.tag] = [m.text.strip(),False]
          else:
            events['0'] = {}
            events['0']['date'] = ["",False]
            events['0']['event'] = ["",False]
          dinf['currocc']['events'] = events
        else:
          dinf['currocc'] = {}
          dinf['currocc']['pos'] = ["",False]
          events = {}
          events['0'] = {}
          events['0']['date'] = ["",False]
          events['0']['event'] = ["",False]
          dinf['currocc']['events'] = events
      elif root[i].tag == "formocc":
#        print ",",
        dinf['formocc'] = {}
        try:
          dinf['formocc']['pos'] = [root[i].find("pos").text.strip(),False]
        except AttributeError:
          del dinf['formocc']
        if dinf.get('formocc'):
          events = {}
          if len(root[i]) > 1:
            for j in root[i]:
              if j.tag is not None:
                if j.tag == "events":
                  for k in j:
                    if k.tag == "mstone":
                      le = str(len(events))
                      events[le] = {}
                      events[le]['date'] = ["",False]
                      events[le]['event'] = ["",False]
                      for m in k:
                        if m.tag and m.text:
                          events[le][m.tag] = [m.text.strip(),False]
          else:
            events['0'] = {}
            events['0']['date'] = ["",False]
            events['0']['event'] = ["",False]
          dinf['formocc']['events'] = events
        else:
          dinf['formocc'] = {}
          dinf['formocc']['pos'] = ["",False]
          events = {}
          events['0'] = {}
          events['0']['date'] = ["",False]
          events['0']['event'] = ["",False]
          dinf['formocc']['events'] = events
      elif root[i].text is not None:
#        print ".",
        dinf[root[i].tag] = [root[i].text.strip(), False]
        if config['debug'] > 2: print str(i) + " ",
#  print str(dinf)
  return (dinf,drel)

def populateWorldXML():
  """Looks in the xmldir and makes a list of fileids the program can
  load. Makes worldList a tuple of lists.
  """
  global config
  global worldList
  fn = os.path.join(config['xmldir'],"myworld.cfg")
  persons = []
  places = []
  cities = []
  states = []
  orgs = []
  # other data types.
  if config['uselistfile'] and os.path.exists(fn):
    print "Loading worldList from file..."
    lines = []
    try:
      with codecs.open(fn,'rU','utf-8') as conf:
        lines = conf.readlines()
        conf.close()
    except IOError as e:
      print " Could not open worldlist file: %s" % e
      exit(1)
    for line in lines:
      try:
        line = line.strip()
        if line:
          values = [x.strip() for x in line.split('=')]
          if values[0] == "persons":
            y = values[1]
            persons.extend(y.split(','))
          elif values[0] == "places":
            y = values[1]
            places.extend(y.split(','))
          elif values[0] == "cities":
            y = values[1]
            cities.extend(y.split(','))
          elif values[0] == "states":
            y = values[1]
            states.extend(y.split(','))
          elif values[0] == "orgs":
            y = values[1]
            orgs.extend(y.split(','))
          elif values[0] == "person":
            persons.append(values[1])
          elif values[0] == "place":
            places.append(values[1])
          elif values[0] == "city":
            cities.append(values[1])
          elif values[0] == "state":
            states.append(values[1])
          elif values[0] == "org":
            orgs.append(values[1])
          else:
            print "Unknown type " + values[0] + " found"
      except Exception as e:
        print "There was an error in the configuration file: %s" % e
  else:
    print "Generating worldList from directory..."
    olist = os.listdir(config['xmldir'])
    nlist = []
    ilist = []
    for i in range(len(olist)):
      if re.search(r'.[Xx][Mm][Ll]$',olist[i]):
        ilist.append(os.path.splitext(olist[i])[0])
        nlist.append(olist[i])
    for i in range(len(nlist)):
      fn = os.path.join(config['xmldir'],nlist[i])
      line = getline(fn,2)
      match = line.find("SYSTEM")
      if match == -1:
        line = getline(fn,3)
        match = line.find("SYSTEM")
      if match != -1:
        match += 8 # trims 'SYSTEM "'
        line = line[match:-7] # trims '.dtd">\n'
        if line == "person":
          persons.append(ilist[i])
        elif line == "place":
          places.append(ilist[i])
        elif line == "city":
          cities.append(ilist[i])
        elif line == "state":
          states.append(ilist[i])
        elif line == "org":
          orgs.append(ilist[i])
        else:
          print "Unknown type " + line + " found"
  if config['debug'] > 2: print "\nPersons: %s\nPlaces: %s\nCities: %s\nStates: %s\nOrgs: %s\n" % (persons,places,cities,states,orgs)
  worldList['p'] = persons
  worldList['l'] = places
  worldList['c'] = cities
  worldList['s'] = states
  worldList['o'] = orgs
  fn = os.path.join(config['xmldir'],"myworld.cfg")
  if config['uselistfile'] and not os.path.exists(fn):
    print " writing list file so you won't have to walk the directory again..."
    writeListFile()
  if config['debug'] > 3: print worldList

def writeListFile():
  global worldList
  global config
  persons = worldList['p']
  places = worldList['l']
  cities = worldList['c']
  states = worldList['s']
  orgs = worldList['o']
  fn = os.path.join(config['xmldir'],"myworld.cfg")
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
  os.remove(os.path.join(os.path.abspath(config['xmldir']),"myworld.cfg"))
  say("WorldList destroyed!")
  global status
  status.push(0,"WorldList destroyed!")

def savePersonXML(fileid,data):
  """Given a filename, saves a person's values to an "id" XML file.
  """
  info = data.get('info')
  rels = data.get('relat')
  fn = fileid + ".xml"
  person = etree.Element("person")
  etree.SubElement(person,"commonname").text = info['commonname'][0]
  etree.SubElement(person,"ctitle").text = info['ctitle'][0]
  print etree.tostring(person)


def idExistsXML(fileid):
  global config
  if config['debug'] > 3: print "seeking " + os.path.join(os.path.abspath(config['xmldir']),fileid + ".xml") + "...",
  return os.path.exists(os.path.join(os.path.abspath(config['xmldir']),fileid + ".xml"))

### SQL Backend