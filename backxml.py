#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

import codecs
from linecache import getline
import os
import re
import xml.etree.ElementTree as etree

import common
from debug import (printPretty,lineno,showConfig)
from globdata import (config,worldList,cities,people,places,states,placeList)
from status import status
import xmlout

locs = {}
lockeys = {}
statekeys = [{},{}]

def getCitiesIn(state):
  if state.find(".xml") > -1: state = state.split('.')[0]
  if state:
    data = placeList.get(state)
    if data is not None:
      keys = data.keys()
      if keys is not None:
        return data
      else:
        common.bsay("?","State %s is empty in placeList" % state)
    else:
      common.bsay("?","State %s not found in placeList" % state)
  return {}

def getCityList(order):
  global locs
  global lockeys
  if not len(worldList): populateWorld()
#  else:
#    print len(worldList['c'])
  if order == 0:
    if not len(locs):
      for city in worldList['c']:
        cityloc = [None,None,None]
        if len(city) > 0: cityloc = getCityLoc(city)
        if cityloc:
          locs[city] = cityloc
          if cityloc[0] is not None and cityloc[1] is not None and cityloc[2] is not None:
            (cityname,state,statename) = cityloc
            if state is not None and city is not None: pushLoc(state,statename,city,cityname)
#    printPretty([lineno(),locs],length=3,quiet=False)
    return locs
  elif order == 1:
    if not len(locs): getCityList(0)
    if not len(lockeys):
      for loc in locs:
        cityloc = [None,None,None]
        if len(loc) > 0: cityloc = getCityLoc(loc)
        if cityloc[0] is not None and cityloc[2] is not None:
          lockeys["%s, %s" % (cityloc[0],cityloc[2])] = loc
#    printPretty([lineno(),locs],length=3,quiet=False)
    return lockeys

def getCityLoc(fileid):
  root = etree.Element("place")
  fn = os.path.join(config['realmdir'],"%s.xml" % fileid)
  status.push(0,"reading city location from XML... '%s'" % fn)
  try:
    with codecs.open(fn,'rU','utf-8') as f:
      tree = etree.parse(f)
      f.close()
      root = tree.getroot()
  except IOError as e:
    print " Could not open configuration file: %s" % e
  cityname = None
  statename = None
  statefile = None
  if root.find("name") is not None: cityname = root.find("name").text.strip()
  if root.find("state") is not None: statename = root.find("state").text.strip()
  if root.find("statefile") is not None: statefile = root.find("statefile").text.strip()
  return [cityname,statefile,statename]

def getPlaceList(pretty):
  if pretty:
    printPretty(placeList)
  else:
    print placeList
  return True

def getPlacesIn(city):
  state = common.getInf(cities.get(city),["info","statefile"],None)
  if state.find(".xml") > -1: state = state.split('.')[0]
  if city.find(".xml") > -1: city = city.split('.')[0]
  if state:
    data = placeList.get(state)
    if data is not None:
      data = placeList[state].get(city)
      if data is not None:
        return data
      else:
        common.say("City %s not found in placeList" %city)
    else:
      common.say("State %s not found in placeList" % state)
  return {}

def getStateList(order):
  global states
  global statekeys
  if not len(worldList): populateWorld()
#  else:
#    print len(worldList['c'])
  if order == 0:
    if not len(statekeys[0]):
      if config['debug'] > 3: printPretty([__name__,lineno(),worldList])
      for state in worldList['s']:
        statename = None
        if len(state) > 0: statename = getStateName(state)
        if statename:
          if config['debug'] > 3: print "%s %s" % (lineno(),statename)
          statekeys[0][state] = statename
          pushLoc(state,statename)
    return statekeys[0]
  elif order == 1:
    if not len(statekeys[0]): getStateList(0)
    if not len(statekeys[1]):
      for state in statekeys[0]:
        statename = None
        if len(state) > 0: statename = getStateName(state)
        if statename:
          statekeys[1]["%s" % statename] = state
    return statekeys[1]

def getStateName(fileid):
  root = etree.Element("state")
  fn = os.path.join(config['realmdir'],fileid + ".xml")
  status.push(0,"reading city location from XML... '%s'" % fn)
  try:
    with codecs.open(fn,'rU','utf-8') as f:
      tree = etree.parse(f)
      f.close()
      root = tree.getroot()
  except IOError as e:
    print " Could not open configuration file: %s" % e
  if root.find("name") is None: return ""
  statename = root.find("name").text.strip()
  return statename

def idExists(fileid):
  global config
  if config['debug'] > 3: print "seeking %s..." % os.path.join(os.path.abspath(config['realmdir']),"%s.xml" % fileid),
  return os.path.exists(os.path.join(os.path.abspath(config['realmdir']),fileid + ".xml"))

def listThings(pretty):
  if pretty:
    printPretty(people)
    printPretty(places)
    printPretty(cities)
    printPretty(states)
    showConfig()
  else:
    print people
    print places
    print cities
    print states
    print config
  getPlaceList(pretty)
  return True

def loadCity(fileid):
  """Given an id (filename) matching an XML file in the appropriate
  directory, loads the tree from the file and pushes its data into
  two dictionaries, which it returns as a tuple.
  """
  dinf = {}
  root = etree.Element("city")
  text = None
  statename = ""
  statefile = ""
  cityname = ""
  # TODO: put this in a global variable, and make a function to populate it from the DTD.
  tags = ["name","state","statefile","start","scue","end","ecue","place"]
  for tag in tags:
    dinf[tag] = ["",False]
  if not dinf.get("places"): dinf['places'] = {}
  if not idExists(fileid):
    status.push(0,"new city created... '%s'" % fileid)
    return dinf
  fn = os.path.join(config['realmdir'],"%s.xml" % fileid)
  status.push(0,"loading city from XML... '%s'" % fn)
  try:
    with codecs.open(fn,'rU','utf-8') as f:
      tree = etree.parse(f)
      f.close()
      root = tree.getroot()
  except IOError as e:
    print "c: Could not open configuration file: %s" % e

  ir = 0
  for i in range(len(root)):
    if root[i].tag is not None:
      if root[i].tag == "place":
        if len(root[i]) > 0:
          node = ""
          node = root[i].find("file")
          if node.text:
            node = node.text.strip()
            node = common.validateFileid(node)
            dinf['places'][node] = {}
            for j in root[i]:
              if j.tag and j.text and j.tag != "file":
                dinf['places'][node][j.tag] = [j.text.strip(),False]
            if config['debug'] > 3: print dinf['places'][node]
          else:
            if config['debug'] > 0:
              print "Invalid place tag:"
              for c in root[i]:
                print c.tag + ': ' + c.text,
        else: # no relat length
          if config['debug'] > 0: print "Empty place tag."
      elif root[i].text is not None:
        if root[i].tag == "statefile":
          statefile = root[i].text.strip()
          statefile = common.validateFileid(statefile)
          if statefile is None: statefile = ""
        elif root[i].tag == "state":
          statename = root[i].text.strip()
        elif root[i].tag == "name":
          cityname = root[i].text.strip()
        dinf[root[i].tag] = [root[i].text.strip(), False]
        if config['debug'] > 2: print str(i) + " ",
  if len(statefile) > 0: pushLoc(statefile,statename,fileid,cityname)
  return dinf

def loadPerson(fileid):
  """Given an id (filename) matching an XML file in the appropriate
  directory, loads the tree from the file and pushes its data into
  two dictionaries, which it returns as a tuple.
  """
  dinf = {}
  drel = {}
  root = etree.Element("person")
  text = None
  # TODO: put this in a global variable, and make a function to populate it from the DTD.
  tags = ["commonname", "ctitle", "gname", "mname", "fname", "nname", "nameorder", "gender", "bday", "dday", "stories", "mention", "appear1ch", "appear1wr", "conflict", "leadrel", "bodytyp", "age", "skin", "eyes", "hair", "dmarks", "dress", "attposs", "asmell", "personality", "speech", "formocc", "currocc", "strength", "weak", "mole", "hobby", "misc", "ethnic", "origin", "backstory", "residence", "minchar", "talent", "abil", "sgoal", "other", "relat", "update"]
  tags.remove("currocc")
  tags.remove("formocc")
  tags.remove("relat")
  tags.append("file")
  for tag in tags:
    dinf[tag] = ["",False]
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
  if not idExists(fileid):
    status.push(0,"new person created... '%s'" % fileid)
    return (dinf,drel)
  fn = os.path.join(config['realmdir'],fileid + ".xml")
  status.push(0,"loading person from XML... '%s'" % fn)
  try:
    with codecs.open(fn,'rU','utf-8') as f:
      tree = etree.parse(f)
      f.close()
      root = tree.getroot()
  except IOError as e:
    print " Could not open configuration file: %s" % e

  ir = 0
  for i in range(len(root)):
    if root[i].tag is not None:
      if root[i].tag == "relat":
        if len(root[i]) > 0:
          node = ""
          node = root[i].find("file")
          if node is not None and node.text:
            node = node.text.strip()
            node = common.validateFileid(node)
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
          else:
            if config['debug'] > 0:
              print "Invalid relat tag:"
              for c in root[i]:
                print c.tag
        else: # no relat length
          if config['debug'] > 0: print "Empty relat tag."
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

def loadPlace(fileid):
  """Given an id (filename) matching an XML file in the appropriate
  directory, loads the tree from the file and pushes its data into
  two dictionaries, which it returns as a tuple.
  """
  dinf = {}
  drel = {}
  root = etree.Element("place")
  text = None
  city = ""
  cityf = ""
  state = ""
  statef = ""
  placename = ""
  # TODO: put this in a global variable, and make a function to populate it from the DTD.
  tags = ["commonname","name","start","scue","end","ecue","stories","mention","desc","address","loc","locfile","state","statefile","note", "relat","update"]
  tags.remove("note")
  tags.remove("relat")
  tags.append("file")
  for tag in tags:
    dinf[tag] = ["",False]
  # if no relations or notes, leave blank
  if not idExists(fileid):
    status.push(0,"new place created... '%s'" % fileid)
    return (dinf,drel)
  fn = os.path.join(config['realmdir'],"%s.xml" % fileid)
  status.push(0,"loading place from XML... '%s'" % fn)
  try:
    with codecs.open(fn,'rU','utf-8') as f:
      tree = etree.parse(f)
      f.close()
      root = tree.getroot()
  except IOError as e:
    print " Could not open place file: %s" % e

  ir = 0
  for i in range(len(root)):
    if root[i].tag is not None:
      if root[i].tag == "relat":
        node = ""
        try:
          node = root[i].find("file").text.strip()
        except AttributeError:
          common.bsay("?","XML formatting error in %s! Probably an empty relat tag." % fileid)
        node = common.validateFileid(node)
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
      elif root[i].tag == "note":
#        print ",",
        if not dinf.get("notes"):
          dinf['notes'] = {}
        x = str(len(dinf['notes']))
        dinf['notes'][x] = {}
        try:
          dinf['notes'][x]['content'] = [root[i].find("content").text.strip(),False]
        except AttributeError:
          del dinf['notes'][x]
        if dinf['notes'].get(x):
          dinf['notes'][x]['date'] = [root[i].find("date").text.strip(),False]
#      elif root[i].tag == "formocc":
#        print ",",
      elif root[i].text is not None:
        if root[i].tag == "statefile":
          statef = root[i].text.strip()
          statef = common.validateFileid(statef)
          if statef is None: statef = ""
        elif root[i].tag == "state":
          state = root[i].text.strip()
        elif root[i].tag == "locfile":
          cityf = root[i].text.strip()
          cityf = common.validateFileid(cityf)
          if cityf is None: cityf = ""
        elif root[i].tag == "loc":
          city = root[i].text.strip()
        elif root[i].tag == "name":
          placename = root[i].text.strip()
        dinf[root[i].tag] = [root[i].text.strip(), False]
        if config['debug'] > 2: print str(i) + " ",
  if len(statef) > 0 and len(cityf) > 0: pushLoc(statef,state,cityf,city,fileid,placename)
  return (dinf,drel)

def loadState(fileid):
  """Given an id (filename) matching an XML file in the appropriate
  directory, loads the tree from the file and pushes its data into
  a dictionary.
  """
  dinf = {}
  root = etree.Element("state")
  text = None
  statename = ""
  statefile = ""
  # TODO: put this in a global variable, and make a function to populate it from the DTD.
  tags = ["name","start","scue","end","ecue"]
  for tag in tags:
    dinf[tag] = ["",False]
  dinf['cities'] = {}
  dinf['m'] = {}
  dinf['m']['events'] = {}
  if not idExists(fileid):
    status.push(0,"new state created... '%s'" % fileid)
    return dinf
  statefile = fileid
  fn = os.path.join(config['realmdir'],"%s.xml" % fileid)
  status.push(0,"loading state from XML... '%s'" % fn)
  try:
    with codecs.open(fn,'rU','utf-8') as f:
      tree = etree.parse(f)
      f.close()
      root = tree.getroot()
  except IOError as e:
    print "c: Could not open configuration file: %s" % e

  ir = 0
  for i in range(len(root)):
    if root[i].tag is not None:
      if root[i].tag == "city":
        if len(root[i]) > 0:
          node = ""
          node = root[i].find("file")
          if node.text:
            node = node.text.strip()
            node = common.validateFileid(node)
            dinf['cities'][node] = {}
            for j in root[i]:
              if j.tag and j.text and j.tag != "file":
                dinf['cities'][node][j.tag] = [j.text.strip(),False]
            if config['debug'] > 3: printPretty(dinf['cities'][node])
          else:
            if config['debug'] > 0:
              print "Invalid city tag:"
              for c in root[i]:
                print c.tag + ': ' + c.text,
        else: # no relat length
          if config['debug'] > 0: print "Empty city tag."
      elif root[i].tag == "events":
        if len(root[i]) > 0:
          nodes = root[i]
          for node in nodes:
            k = str(len(dinf['m']['events']))
            dinf['m']['events'][k] = {}
            for j in node:
              print "%s: %s" % (j.tag,j.text)
              if j.tag and j.text:
                dinf['m']['events'][k][j.tag] = [j.text.strip(),False]
              else:
                if config['debug'] > 0:
                  print "Invalid milestone tag:"
                  for c in node:
                    print c.tag + ': ' + c.text,
          if config['debug'] > 0: printPretty(dinf['m']['events'])
        else: # no relat length
          if config['debug'] > 0: print "Empty milestone tag."

      elif root[i].text is not None:
        dinf[root[i].tag] = [root[i].text.strip(), False]
        if config['debug'] > 2: print str(i) + " ",
  statename = dinf.get("name","")
  if len(statename) > 1: pushLoc(statefile,statename)
  return dinf

def populateWorld():
  """Looks in the realmdir and makes a list of fileids the program can
  load. Makes worldList a tuple of lists.
  """
  global config
  global worldList
  fn = os.path.join(config['realmdir'],"myrealm.cfg")
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
            print "Unknown type %s found" % values[0]
      except Exception as e:
        print "There was an error in the configuration file: %s" % e
  elif not os.path.exists(config['realmdir']):
    print "Fatal error. World directory %s does not exist! Exiting." % config['realmdir']
    exit(-1)
  else:
    print "Generating worldList from directory..."
    olist = os.listdir(config['realmdir'])
    nlist = []
    ilist = []
    for i in range(len(olist)):
      if re.search(r'.[Xx][Mm][Ll]$',olist[i]):
        ilist.append(os.path.splitext(olist[i])[0])
        nlist.append(olist[i])
    for i in range(len(nlist)):
      fn = os.path.join(config['realmdir'],nlist[i])
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
          print "Unknown type %s found" % line
  if config['debug'] > 2: print "\nPersons: %s\nPlaces: %s\nCities: %s\nStates: %s\nOrgs: %s\n" % (persons,places,cities,states,orgs)
  worldList['p'] = persons
  worldList['l'] = places
  worldList['c'] = cities
  worldList['s'] = states
  worldList['o'] = orgs
  for key in worldList.keys():
    if len(worldList[key]):
      if not len(worldList[key][0]):
        worldList[key] = []
  for s in worldList['s']:
    pushLoc(s)
  getStateList(0)
  getCityList(0)
  if config['debug'] > 3:
    printPretty(worldList)
    printPretty(placeList)

def pushLoc(statefile,statename = "",cityfile = "",cityname = "",placefile = "",placename = ""):
  for f in [statefile,cityfile,placefile]:
    if f is None:
      f = ""
  if config['debug'] > 3:
    printPretty([statefile,cityfile,placefile])
  if len(statefile) > 0:
    if statefile.find(".xml") > -1: statefile = statefile.split('.')[0]
    if not placeList.get(statefile): placeList[statefile] = {}
    if statename is not None and len(statename) > 0:
      placeList[statefile]['_name'] = statename
    if len(cityfile) > 0:
      if cityfile.find(".xml") > -1: cityfile = cityfile.split('.')[0]
      if not placeList[statefile].get(cityfile): placeList[statefile][cityfile] = {}
      if cityname is not None and len(cityname) > 0:
        placeList[statefile][cityfile]['_name'] = cityname
      if len(placefile) > 0:
        if placefile.find(".xml") > -1: placefile = placefile.split('.')[0]
        if len(placename) > 0 and len(placefile) > 0: placeList[statefile][cityfile][placefile] = placename
    elif len(placefile) > 0:
      print "Could not place ",
      printPretty([statefile,cityfile,placefile])
  elif len(placefile) > 0:
    print "Could not place ",
    printPretty([statefile,cityfile,placefile])

def saveCity(fileid,data):
  """Given a filename, saves a city's values to an "id" XML file.
  """
  global cities
  info = data.get('info')
  fn = fileid + ".xml"
  city = etree.Element("city")
  # TODO: put this in a global variable, and make a function to populate it from the DTD.
  tags = ["name","state","statefile","start","scue","end","ecue","places","update"]
  for tag in tags:
    if tag == "places":
      nodes = info.get("places")
      if nodes is not None:
        for node in nodes.keys():
          if nodes[node].get("name"):
            connected = etree.Element("place")
            value = info['places'][node].get("name")
            if value is None: value = ['',False]
            etree.SubElement(connected,"name").text = value[0]
            value = node
            if value is None: value = ''
            etree.SubElement(connected,"file").text = value
            value = info['places'][node].get("note")
            if value is not None and len(value[0]) > 0: etree.SubElement(connected,"note").text = value[0]
            city.append(connected)
#            for t in range(len(connected)):
#              print "%s: %s" % (connected[t].tag,connected[t].text)
          else:
            print "A required tag is missing from place %s." % node
      else:
        print "no places found"
    elif tag == "update":
      etree.SubElement(city,tag).text = common.skrTimeStamp(config['datestyle'])
    else:
      value = info.get(tag)
      if value is None: value = ['',False]
      etree.SubElement(city,tag).text = value[0]
  saveXMLtree(city,"city",fileid)
  cities[fileid]['changed'] = False
  return True

def savePerson(fileid,data):
  """Given a filename, saves a person's values to an "id" XML file.
  """
  global people
  info = data.get('info')
  rels = data.get('relat')
  fn = fileid + ".xml"
  person = etree.Element("person")
  # TODO: put this in a global variable, and make a function to populate it from the DTD.
  tags = ["commonname", "ctitle", "gname", "mname", "fname", "nname", "nameorder", "gender", "bday", "dday", "stories", "mention", "appear1ch", "appear1wr", "conflict", "leadrel", "bodytyp", "age", "skin", "eyes", "hair", "dmarks", "dress", "attposs", "asmell", "personality", "speech", "formocc", "currocc", "strength", "weak", "mole", "hobby", "misc", "ethnic", "origin", "backstory", "residence", "minchar", "talent", "abil", "sgoal", "other", "relat", "update"]
  reltags = ["related", "relation", "file", "rtype", "events", "cat", "realm"]
  for tag in tags:
    if tag == "relat":
      if len(rels):
        for r in rels:
          if rels[r].get("cat") is None:
            rels[r]['cat'] = common.getCat(r) # Try to figure it out
          if rels[r].get("related") is not None and rels[r].get("relation") is not None and rels[r].get("rtype") is not None and rels[r].get("cat") is not None:
            connected = etree.Element("relat")
            for t in reltags:
              if rels[r].get(t):
                if t == "events":
                  if len(rels[r]['events']):
                    events = etree.Element("events")
                    elist = rels[r]['events'].keys()
                    chron = sorted(elist, key = lambda x: rels[r]['events'][x].get("date"))
                    for e in chron:
                      mstone = etree.Element("mstone")
                      etree.SubElement(mstone,"date").text = rels[r]['events'][e].get("date",("",False))[0]
                      etree.SubElement(mstone,"event").text = rels[r]['events'][e].get("event",("",False))[0]
                      if rels[r]['events'][e].get("Type"):
                        etree.SubElement(mstone,"type").text = rels[r]['events'][e].get("type")[0]
                      events.append(mstone)
                    connected.append(events)
                else:
                  value = rels[r].get(t)
                  if value is None: value = ['',False]
                  etree.SubElement(connected,t).text = value[0]
              elif t == "file":
                value = [r,False]
                etree.SubElement(connected,t).text = value[0]
            person.append(connected)
          else:
            print "A required tag is missing from relation %s." % r,
            printPretty(rels[r])
      else:
        print "no relations found"
    elif tag == "currocc" or tag == "formocc":
      if info[tag].get("pos"):
        occ = etree.Element(tag)
        value = info[tag].get("pos")
        if value is None: value = ['',False]
        etree.SubElement(occ,"pos").text = value[0]
        if info[tag].get("events"):
          if len(info[tag]['events']):
            events = etree.Element("events")
            elist = info[tag]['events'].keys()
            chron = sorted(elist, key = lambda x: info[tag]['events'][x].get("date"))
            for e in chron:
              mstone = etree.Element("mstone")
              etree.SubElement(mstone,"date").text = info[tag]['events'][e].get("date",("",False))[0]
              etree.SubElement(mstone,"event").text = info[tag]['events'][e].get("event",("",False))[0]
              if info[tag]['events'][e].get("Type"):
                etree.SubElement(mstone,"type").text = info[tag]['events'][e].get("type")[0]
              events.append(mstone)
          occ.append(events)
        person.append( occ )
    elif tag == "update":
      etree.SubElement(person,tag).text = common.skrTimeStamp(config['datestyle'])
    else:
      value = info.get(tag)
      if value is None: value = ['',False]
      etree.SubElement(person,tag).text = value[0]
  saveXMLtree(person,"person",fileid)
  people[fileid]['changed'] = False
  return True

def savePlace(fileid,data):
  """Given a filename, saves a place's values to an "id" XML file.
  """
  global places
  info = data.get('info')
  rels = data.get('relat')
  fn = fileid + ".xml"
  place = etree.Element("place")
  # TODO: put this in a global variable, and make a function to populate it from the DTD.
  tags = ["commonname","name","start","scue","end","ecue","stories","mention","desc","address","loc","locfile","state",\
"statefile","note", "relat","update"]
  reltags = ["related", "relation", "file", "rtype", "events", "cat", "realm"]
  for tag in tags:
    if tag == "relat":
      if len(rels):
        for r in rels:
          if rels[r].get("related") and rels[r].get("relation") and rels[r].get("rtype") and rels[r].get("cat"):
            connected = etree.Element("relat")
            for t in reltags:
              if rels[r].get(t):
                if t == "events":
                  if len(rels[r]['events']):
                    events = etree.Element("events")
                    elist = rels[r]['events'].keys()
                    chron = sorted(elist, key = lambda x: rels[r]['events'][x].get("date"))
                    for e in chron:
                      mstone = etree.Element("mstone")
                      etree.SubElement(mstone,"date").text = rels[r]['events'][e].get("date",("",False))[0]
                      etree.SubElement(mstone,"event").text = rels[r]['events'][e].get("event",("",False))[0]
                      if rels[r]['events'][e].get("Type"):
                        etree.SubElement(mstone,"type").text = rels[r]['events'][e].get("type")[0]
                      events.append(mstone)
                    connected.append(events)
                else:
                  value = rels[r].get(t)
                  if value is None: value = ['',False]
                  etree.SubElement(connected,t).text = value[0]
            place.append(connected)
          else:
            print "A required tag is missing from relation %s." % r
      else:
        print "no relations found"
    elif tag == "note":
      if info.get(tag):
        for i in range(len(info[tag])):
          note = etree.Element(tag)
          di = info[tag].get(str(i))
          if di:
            value = di.get("content")
            if value is not None:
              etree.SubElement(note,"content").text = value[0]
              value = di.get("date")
              if value is not None:
                etree.SubElement(note,"date").text = value[0]
                place.append(note)
      else:
        print "no notes"
    elif tag == "update":
      etree.SubElement(place,tag).text = common.skrTimeStamp(config['datestyle'])
    else:
      value = info.get(tag)
      if value is None: value = ['',False]
      etree.SubElement(place,tag).text = value[0]
  saveXMLtree(place,"place",fileid)
  places[fileid]['changed'] = False
  return True

def saveState(fileid,data):
  """Given a filename, saves a state's values to an "id" XML file.
  """
  global states
  info = data.get('info')
  fn = fileid + ".xml"
  state = etree.Element("state")
  # TODO: put this in a global variable, and make a function to populate it from the DTD.
  tags = ["name","start","scue","end","ecue","cities","events","update"]
  for tag in tags:
    if tag == "cities":
      nodes = info.get("cities")
      if nodes is not None:
        for node in nodes.keys():
          if nodes[node].get("name"):
            connected = etree.Element("city")
            value = info['cities'][node].get("name")
            if value is None: value = ['',False]
            etree.SubElement(connected,"name").text = value[0]
            value = node
            if value is None: value = ''
            etree.SubElement(connected,"file").text = value
            value = info['cities'][node].get("note")
            if value is not None and len(value[0]) > 0: etree.SubElement(connected,"note").text = value[0]
            state.append(connected)
          else:
            print "A required tag is missing from city %s." % node
      else:
        print "no cities found"
    elif tag == "events":
      nodes = info.get("m")
      nodes = nodes.get("events")
      if nodes is not None:
        events = etree.Element("events")
        for node in nodes.keys():
          if nodes[node].get("event"):
            connected = etree.Element("mstone")
            value = info['m']['events'][node].get("event")
            if value is None: value = ['',False]
            etree.SubElement(connected,"event").text = value[0]
            value = info['m']['events'][node].get("date")
            if value is None: value = ['',False]
            etree.SubElement(connected,"date").text = value[0]
            events.append(connected)
          else:
            print "A required tag is missing from event %s." % node
        state.append(events)
      else:
        print "no events found"
    elif tag == "update":
      etree.SubElement(state,tag).text = common.skrTimeStamp(config['datestyle'])
    else:
      value = info.get(tag)
      if value is None: value = ['',False]
      etree.SubElement(state,tag).text = value[0]
  r = saveXMLtree(state,"state",fileid)
  if r:
    try:
      states[fileid]['changed'] = False
    except KeyError:
      printPretty(states)
  return r

def saveXMLtree(tree,category,fileid):
  out = ""
  if config['debug'] > 6: printPretty(etree.tostring(tree),True,True)
  try:
    out = etree.tostring(tree,pretty_print=True)
  except TypeError: # for me, previous line results in "unexpected keyword argument 'pretty_print'"
    out = xmlout.prettyXML(tree)
  start = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<?xml-stylesheet type=\"text/xsl\" href=\""
  start += os.path.join(config['xslurl'],"%s.xsl" % category)
  start += "\"?>\n<!DOCTYPE person SYSTEM \"%s.dtd\">\n" % category
  finaloutput = start + out
  if config['debug'] > 0: print finaloutput
  fn = os.path.join(os.path.abspath(config['realmdir']),fileid + ".xml")
  try:
    with codecs.open(fn,'wU','UTF-8') as f:
      f.write(finaloutput)
      f.close()
  except IOError as e:
    message = "The file %s could not be saved: %s" % (fn,e)
    common.bsay("?",message)
    status.push(0,message)
    return False
  return True

def updateLocs(cityname,locfile,statefile):
  global locs
  global lockeys
  statename = getStateName(statefile)
  if statename:
    cityloc = [None,None,None]
    if len(cityname) > 0: cityloc = getCityLoc(cityname)
    if cityloc[0] and cityloc[2]:
      del lockeys["%s, %s" % (cityloc[0],cityloc[2])]
    lockeys["%s, %s" % (cityname,statename)] = locfile
    cityloc = [cityname,statefile,statename]
    locs[locfile] = cityloc
