#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

config = {}
worldList = {}

import codecs
import re
import os
from linecache import getline
from status import status
from common import say

def loadConfig(fn = None):
  """Returns a dict containing the config options in the CCOW config file."""
  lines = []
  global config
  config['debug'] = 1
  if fn is None:
    fn = "default.cfg" # using 3-letter extension for MSWin compatibility, I hope.
  if os.path.exists(os.path.abspath(fn)):
    try:
      with codecs.open(fn,'rU','utf-8') as conf:
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
  config = validateConfig(config)
  return config

def validateConfig(config):
  """Checks some config values for validity. Returns adjusted dictionary."""
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
  config['xmldir'] = config.get("xmldir","./") # Where should I look for XML files?
  return config

### Wrappers
def loadPerson(fileid):
  global config
  if config['informat'] == "sql":
    return loadPersonSQL(fileid)
  else:
    return loadPersonXML(fileid)

def savePerson(fileid,data,rels):
  global config
  if config['outformat'] == "sql":
    return savePersonSQL(fileid,data,rels)
  else:
    return savePersonXML(fileid,data,rels)

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
from xml.etree.ElementTree import (parse, Element)

def loadPersonXML(fileid):
  """Given an id (filename) matching an XML file in the appropriate
  directory, loads the tree from the file and pushes its data into
  two dictionaries, which it returns as a tuple.
  """
  dinf = {}
  drel = {}
  root = Element("person")
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
  
  if not idExistsXML(fileid):
    status.push(0,"new person created... '" + fileid + "'")
    return (dinf,drel)
  fileid = os.path.join(config['xmldir'],fileid + ".xml")
  status.push(0,"loading person from XML... '" + fileid + "'")
  try:
    with codecs.open(fileid,'rU','utf-8') as f:
      tree = parse(f)
      f.close()
      root = tree.getroot()
  except IOError as e:
    print " Could not open configuration file: %s" % e

  ir = 0
  for i in range(len(root)):
    if root[i].tag is not None:
      if root[i].tag == "relat":
#        print "r",
        key = None
        values = {}
        if len(root[i]):
          key = root[i].find("related").text
          for j in root[i]:
            if j.text is not None:
              values[j.tag] = [j.text,False]
        if key is not None:
          drel[key] = values
#        print drel[key]
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
          if values[0] == "person":
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
      if re.search(r'.[Xx][Mm][Ll]',olist[i]):
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
      for i in persons:
        puts.append("person = " + i + "\n")
      for i in places:
        puts.append("place = " + i + "\n")
      for i in cities:
        puts.append("city = " + i + "\n")
      for i in states:
        puts.append("state = " + i + "\n")
      for i in orgs:
        puts.append("org = " + i + "\n")
      conf.writelines(puts)
      conf.close()
  except IOError as e:
    print " Could not write worldlist file: %s" % e
    exit(1)

def killListFile(caller = None):
  os.remove(os.path.join(os.path.abspath(config['xmldir']),"myworld.cfg"))
  say("WorldList destroyed!")

def savePersonXML(fileid,data,rels):
  """Given a filename and two dictionaries, saves a person's values to an "id" XML file.
  """

def idExistsXML(fileid):
  global config
  if config['debug'] > 3: print "seeking " + os.path.join(os.path.abspath(config['xmldir']),fileid + ".xml") + "...",
  return os.path.exists(os.path.join(os.path.abspath(config['xmldir']),fileid + ".xml"))

### SQL Backend