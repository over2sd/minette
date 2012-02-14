#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

config = {}

import codecs
from os import path
from status import status

def loadConfig(fn = None):
  """Returns a dict containing the config options in the CCOW config file."""
  lines = []
  global config
  config['debug'] = 1
  if fn is None:
    fn = "chardb.conf"
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
  config['familyfirst'] = config.get("familyfirst",False) # Does the family name come first?
  return config

### Wrappers
def loadPerson(fileid):
  if True:
    fileid = config['xmldir'] + "/" + fileid + ".xml"
    return loadPersonXML(fileid)
  else:
    return loadPersonSQL(fileid)

def savePerson(fileid,data,rels):
  if True:
    return savePersonWML()
  else:
    return savePersonSQL()

### XML Backend
from xml.etree.ElementTree import (parse, Element)

def loadPersonXML(fileid):
  """Given an id (filename) matching an XML file in the appropriate
  directory, loads the tree from the file and pushes its data into
  two dictionaries, which it returns as a tuple.
  """
  status.push(0,"loading person from XML... '" + fileid + "'")
  dinf = {}
  drel = {}
  root = Element("person")
  text = None
  try:
    with codecs.open(fileid,'rU','utf-8') as f:
      tree = parse(f)
      f.close()
      root = tree.getroot()
  except IOError as e:
    print " Could not open configuration file: %s" % e

  ir = 0
  for i in range(len(root)):
    if root[i].text is not None:
      if root[i].tag != "relat":
        dinf[root[i].tag] = (root[i].text.strip(), False)
      else:
        key = root[i].find("related").text
        values = {}
        for j in root[i]:
          if j.text is not None:
            values[j.tag] = (j.text,False)
        drel[key] = values
#        print drel[key]
      if config['debug'] > 2: print str(i) + " ",
  return (dinf,drel)

def savePersonXML(id,data,rels):
  """Given a filename and two dictionaries, saves a person's values to an "id" XML file.
  """

### SQL Backend