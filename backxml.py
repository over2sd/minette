import xml.etree.ElementTree as etree
from globdata import (config,worldList)
from status import status
import codecs
import os

def idExists(fileid):
  global config
  if config['debug'] > 3: print "seeking " + os.path.join(os.path.abspath(config['worlddir']),fileid + ".xml") + "...",
  return os.path.exists(os.path.join(os.path.abspath(config['worlddir']),fileid + ".xml"))

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
  # if no relations, leave blank
  if not idExists(fileid):
    status.push(0,"new person created... '" + fileid + "'")
    return (dinf,drel)
  fileid = os.path.join(config['worlddir'],fileid + ".xml")
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

def loadPlace(fileid):
  """Given an id (filename) matching an XML file in the appropriate
  directory, loads the tree from the file and pushes its data into
  two dictionaries, which it returns as a tuple.
  """
  dinf = {}
  drel = {}
  root = etree.Element("place")
  text = None
  # TODO: put this in a global variable, and make a function to populate it from the DTD.
  tags = ["commonname","name","start","scue","end","ecue","stories","mention","desc","address","loc","locfile","state","statefile","note", "relat","update"]
  tags.remove("note")
  tags.remove("relat")
  tags.append("file")
  for tag in tags:
    dinf[tag] = ["",False]
  # if no relations or notes, leave blank
  if not idExists(fileid):
    status.push(0,"new place created... '" + fileid + "'")
    return (dinf,drel)
  fileid = os.path.join(config['worlddir'],fileid + ".xml")
  status.push(0,"loading place from XML... '" + fileid + "'")
  try:
    with codecs.open(fileid,'rU','utf-8') as f:
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
        dinf[root[i].tag] = [root[i].text.strip(), False]
        if config['debug'] > 2: print str(i) + " ",
#  print str(dinf)
  return (dinf,drel)

def populateWorld():
  """Looks in the worlddir and makes a list of fileids the program can
  load. Makes worldList a tuple of lists.
  """
  global config
  global worldList
  fn = os.path.join(config['worlddir'],"myworld.cfg")
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
    olist = os.listdir(config['worlddir'])
    nlist = []
    ilist = []
    for i in range(len(olist)):
      if re.search(r'.[Xx][Mm][Ll]$',olist[i]):
        ilist.append(os.path.splitext(olist[i])[0])
        nlist.append(olist[i])
    for i in range(len(nlist)):
      fn = os.path.join(config['worlddir'],nlist[i])
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
  fn = os.path.join(config['worlddir'],"myworld.cfg")
  if config['uselistfile'] and not os.path.exists(fn):
    print " writing list file so you won't have to walk the directory again..."
    writeListFile()
  if config['debug'] > 3: print worldList

def savePerson(fileid,data):
  """Given a filename, saves a person's values to an "id" XML file.
  """
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
            person.append(connected)
          else:
            print "A required tag is missing from relation %s." % r
      else:
        print "no relations found"
    elif tag == "currocc":
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
    elif tag == "formocc":
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
      etree.SubElement(person,tag).text = skrTimeStamp(1)
    else:
      value = info.get(tag)
      if value is None: value = ['',False]
      etree.SubElement(person,tag).text = value[0]
  out = ""
  try:
    out = etree.tostring(person,pretty_print = True)
  except TypeError: # for me, previous line results in "unexpected keyword argument 'pretty_print'"
    out = xmlout.prettyXML(person)
  start = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<?xml-stylesheet type=\"text/xsl\" href=\""
  start += os.path.join(config['xslurl'],"person.xsl")
  start += "\"?>\n<!DOCTYPE person SYSTEM \"person.dtd\">\n"
  finaloutput = start + out
  if config['debug'] > 0: print finaloutput
  fn = os.path.join(os.path.abspath(config['worlddir']),fileid + ".xml")
  try:
    with codecs.open(fn,'wU','UTF-8') as f:
      f.write(finaloutput)
      f.close()
  except IOError as e:
    message = "The file %s could not be saved: %s" % (fn,e)
    bsay("?",message)
    status.push(0,message)
    return False
  people[fileid]['changed'] = False
  return True

def savePlace(fileid,data):
  """Given a filename, saves a place's values to an "id" XML file.
  """
  info = data.get('info')
  rels = data.get('relat')
  fn = fileid + ".xml"
  place = etree.Element("place")
  # TODO: put this in a global variable, and make a function to populate it from the DTD.
  tags = ["commonname","name","start","scue","end","ecue","stories","mention","desc","address","loc","locfile","state","statefile","note", "relat","update"]
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
    elif tag == "update":
      etree.SubElement(place,tag).text = skrTimeStamp(1)
    else:
      value = info.get(tag)
      if value is None: value = ['',False]
      etree.SubElement(place,tag).text = value[0]
  out = ""
  try:
    out = etree.tostring(place,pretty_print = True)
  except TypeError: # for me, previous line results in "unexpected keyword argument 'pretty_print'"
    out = xmlout.prettyXML(place)
  start = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<?xml-stylesheet type=\"text/xsl\" href=\""
  start += os.path.join(config['xslurl'],"place.xsl")
  start += "\"?>\n<!DOCTYPE place SYSTEM \"place.dtd\">\n"
  finaloutput = start + out
  if config['debug'] > 0: print finaloutput
  fn = os.path.join(os.path.abspath(config['worlddir']),fileid + ".xml~")
  try:
    with codecs.open(fn,'wU','UTF-8') as f:
      f.write(finaloutput)
      f.close()
  except IOError as e:
    message = "The file %s could not be saved: %s" % (fn,e)
    bsay("?",message)
    status.push(0,message)
    return False
  places[fileid]['changed'] = False
  return True