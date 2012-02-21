#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

import pygtk
pygtk.require('2.0')
import gtk
from backends import (loadPerson, savePerson, config, writeListFile, idExists,worldList,killListFile)
from common import (say,bsay,askBox,validateFileid,recordSelectBox,askBoxProcessor)
from getmod import getPersonConnections
from status import status
from math import floor
people = {}

def getit(fileid,key):
  """deprecated function. will be removed eventually."""
  global people
  data = {}
  try:
    data = people[fileid]['info']
  except KeyError as e:
    print "Error getting info from %s: %s" % (fileid,e)
    return ""
  pair = data.get(key,None)
  if pair != None:
    return pair[0]
  else:
    return ""

def buildarow(name,fileid,key,style = 0):
  """Returns a row containing the given key description and value in a GTK HBox."""
  row = gtk.HBox()
  row.set_border_width(2)
  row.show()
  row.label = gtk.Label(name)
  row.label.set_width_chars(20)
  value = 0.5
  if style == 1: value = 0.03
  row.label.set_alignment(1,value)
  row.label.show()
  row.add(row.label)
  row.set_child_packing(row.label,0,0,2,gtk.PACK_START)
  if style == 0:
    value = getInf([fileid,"info",key])
    row.e = gtk.Entry()
    row.e.set_text(value)
    activateInfoEntry(row.e,fileid,key)
  if style == 1:
    row.e = buildaposition(fileid,key)
  row.e.show()
  row.add(row.e)
  row.set_child_packing(row.e,1,1,2,gtk.PACK_START)
  return row

def buildaposition(fileid,key):
  """Returns a GTK table containing the data values of the given position."""
  t = gtk.Table(1,4) # TODO: Move this out into the buildarow so we can pu multiple positions in the same table?
  # or do we want them separated so we have the headers and separation?
  t.show()
  global people
  data = {}
  try:
    data = people[fileid]['info']
  except KeyError as e:
    print "Error getting info from %s: %s" % (fileid,e)
    return ""
  data = data.get(key,None)
  value = data.get("pos")
  if value: value = value[0]
  if data.get("events"):
    rows = len(data['events'])
    cols = 4
#    t.addpos = gtk.Button("Add Position")
    t.addmile = gtk.Button("Add milestone")
    t.addmile.show()
    t.attach(t.addmile,3,4,1,2)
    t.addmile.connect("clicked",addOccMilestone,t,fileid,key)
    if rows > 0:
      t.resize(rows + 3,cols)
#      t.set_geometry_hints(None,790,440)
      t.phead = gtk.Label("Position")
      t.phead.show()
      t.attach(t.phead,0,1,0,1)
      t.mhead = gtk.Label("Milestone")
      t.mhead.show()
      t.attach(t.mhead,1,3,0,1)
      t.dhead = gtk.Label("Date")
      t.dhead.show()
      t.attach(t.dhead,1,2,1,2)
      t.ehead = gtk.Label("Event")
      t.ehead.show()
      t.attach(t.ehead,2,3,1,2)
      rpos = gtk.Entry()
      extraargs = ["pos",]
      activateInfoEntry(rpos,fileid,key,len(extraargs),extraargs)
      rpos.show()
      rpos.set_text(value)
      rpos.set_width_chars(12)
      t.attach(rpos,0,1,1,2)
      for i in range(rows):
        value = data['events'][str(i)].get("date","")
        if value: value = value[0]
        rda = gtk.Entry()
        extraargs = ["events",str(i),"date"]
        activateInfoEntry(rda,fileid,key,len(extraargs),extraargs)
        rda.show()
        rda.set_width_chars(12)
        rda.set_text(value)
        t.attach(rda,1,2,i + 2,i + 3)
        value = data['events'][str(i)].get("event","")
        if value: value = value[0]
        rev = gtk.Entry()
        extraargs = ["events",str(i),"event"]
        activateInfoEntry(rev,fileid,key,len(extraargs),extraargs)
        rev.show()
        rev.set_width_chars(10)
        rev.set_text(value)
        t.attach(rev,2,3,i + 2,i + 3)
#        print str(t.size_request())
  return t

def activateInfoEntry(self, fileid, key, extra = 0, exargs = []):
  path = [fileid,"info",key]
  for i in range(len(exargs)): path.append(exargs[i])
  self.connect("focus-out-event", checkForChange,path)

def activateRelEntry(self, fileid, key, extra = 0, exargs = []):
  path = [fileid,"info",key]
  for i in range(len(exargs)): path.append(exargs[i])
  self.connect("focus-out-event", checkForChange,path)

def checkForChange(self,event,path):
  if config['debug'] > 3: print "Checking " + str(path)
  if getInf(path) != self.get_text():
    if config['debug'] > 2 : print str(getInf(path)) + " vs " + self.get_text()
    markChanged(self,path)

def markChanged(self,path):
  global people
  self.modify_base(gtk.STATE_NORMAL,gtk.gdk.color_parse("#CCCCDD")) # change background for edited
  end = len(path)
  goforit = preReadp(True,path[:-1],end)
  value = ["",False]
  value[1] = True
  value[0] = self.get_text()
  if goforit:
    if end == 3:
      try:
        people[path[0]][path[1]][path[2]] = value
      except KeyError:
        print "Could not mark " + path[2] + " as changed."
        return
    elif end == 4:
      try:
        people[path[0]][path[1]][path[2]][path[3]] = value
      except KeyError:
        print "Could not mark " + path[3] + " as changed."
        return
    elif end == 5:
      try:
        people[path[0]][path[1]][path[2]][path[3]][path[4]] = value
      except KeyError:
        print "Could not mark " + path[4] + " as changed."
        return
    elif end == 6:
      try:
        people[path[0]][path[1]][path[2]][path[3]][path[4]][path[5]] = value
      except KeyError:
        print "Could not mark " + path[5] + " as changed."
        return
    elif end == 7:
      try:
        people[path[0]][path[1]][path[2]][path[3]][path[4]][path[5]][path[6]] = value
      except KeyError:
        print "Could not mark " + path[6] + " as changed."
        return
    else:
      say("Path too long")
      return
    people[path[0]]['changed'] = True
    print "Value set: " + getInf(path)
  else:
    print "Invalid path"
    return

def initPinfo(self, fileid):
  global people
  global config
  info = {}
  try:
    info = people[fileid]['info']
  except KeyError as e:
    print "An error occurred accessing %s: %s" % (fileid,e)
    return
  self.l1 = gtk.Label("Name:")
  self.l1.set_alignment(0,0)
  self.set_child_packing(self.l1,1,1,2,gtk.PACK_START)
  self.add(self.l1)
  self.namebox = gtk.HBox()
  self.namebox.set_border_width(2)
  self.add(self.namebox)
  self.namebox.show()
  self.l5 = gtk.Label("Title:")
  self.ctitle = gtk.Entry(5)
  self.l2 = gtk.Label("Family:")
  self.fname = gtk.Entry(25)
  self.l3 = gtk.Label("Given:")
  self.gname = gtk.Entry(25)
  self.l4 = gtk.Label("Middle/Maiden:")
  self.mname = gtk.Entry(25)
  self.namebox.add(self.l5)
  self.namebox.add(self.ctitle)
  self.ctitle.set_width_chars(4)
  self.fname.set_width_chars(10)
  self.gname.set_width_chars(10)
  self.mname.set_width_chars(10)
  self.namebox.set_child_packing(self.ctitle,0,0,2,gtk.PACK_START)
  self.ctitle.set_text(getit(fileid,'ctitle'))
  self.ctitle.show()
  if config['familyfirst'] == True:
    self.namebox.add(self.l2)
    self.namebox.add(self.fname)
  self.namebox.add(self.l3)
  self.namebox.add(self.gname)
  self.gname.set_text(getit(fileid,'gname'))
  self.gname.show()
  if config['usemiddle'] == True:
    self.namebox.add(self.l4)
    self.namebox.add(self.mname)
    self.mname.set_text(getit(fileid,'mname'))
    self.mname.show()
  if config['familyfirst'] == False:
    self.namebox.add(self.l2)
    self.namebox.add(self.fname)
  self.fname.set_text(getit(fileid,'fname'))
  self.fname.show()
  self.l1.show()
  self.l2.show()
  self.l3.show()
  self.l4.show()
  self.l5.show()
  self.cname = buildarow("Common Name:",fileid,'commonname') # TODO: Some day, maybe move all these labels into a dict and generate these things algorithmically? What about sections?
  self.add(self.cname)
  self.nname = buildarow("Nickname:",fileid,'nname')
  self.add(self.nname)
  self.gender = buildarow("Gender:",fileid,'gender') # TODO: Some day, this will be a radio button
  self.add(self.gender)
  self.bday = buildarow("Birth Date:",fileid,'bday')
  self.add(self.bday)
  self.dday = buildarow("Death Date:",fileid,'dday')
  self.add(self.dday)
  self.l6 = gtk.Label("Stories")
  self.l6.set_alignment(0,0)
  self.l6.show()
  self.add(self.l6)
  self.s1 = gtk.HSeparator()
  self.add(self.s1)
  self.s1.show()
  self.stories = buildarow("Stories:",fileid,'stories') # TODO: Some day, this will be a dynamic list of checkboxes
  self.add(self.stories)
  self.mention = buildarow("First Mention:",fileid,'mention')
  self.add(self.mention)
  self.appearch = buildarow("First appeared (chron):",fileid,'appear1ch')
  self.add(self.appearch)
  self.appearwr = buildarow("First appeared (writ):",fileid,'appear1wr')
  self.add(self.appearwr)
  self.conflict = buildarow("Conflict:",fileid,'conflict')
  self.add(self.conflict)
  self.leadrel = buildarow("Relation to lead:",fileid,'leadrel')
  self.add(self.leadrel)
  self.l7 = gtk.Label("Physical Appearance")
  self.l7.set_alignment(0,1)
  self.l7.show()
  self.add(self.l7)
  self.s2 = gtk.HSeparator()
  self.add(self.s2)
  self.s2.show()
  self.bodytyp = buildarow("Body Type:",fileid,'bodytyp')
  self.add(self.bodytyp)
  self.age = buildarow("Age:",fileid,'age')
  self.add(self.age)
  self.skin = buildarow("Skin:",fileid,'skin')
  self.add(self.skin)
  self.eyes = buildarow("Eyes:",fileid,'eyes')
  self.add(self.eyes)
  self.hair = buildarow("Hair:",fileid,'hair')
  self.add(self.hair)
  self.dmarks = buildarow("Distinguishing Marks:",fileid,'dmarks')
  self.add(self.dmarks)
  self.dress = buildarow("Dress:",fileid,'dress')
  self.add(self.dress)
  self.attpos = buildarow("Attached Possessions:",fileid,'attpos')
  self.add(self.attpos)
  self.asmell = buildarow("Associated Smell:",fileid,'asmell')
  self.add(self.asmell)
  self.l8 = gtk.Label("Personality Traits")
  self.l8.set_alignment(0,1)
  self.l8.show()
  self.add(self.l8)
  self.s3 = gtk.HSeparator()
  self.add(self.s3)
  self.s3.show()
  self.pers = buildarow("Personality:",fileid,'personality')
  self.add(self.pers)
  self.speech = buildarow("Distinct Speech:",fileid,'asmell')
  self.add(self.speech)
  self.formocc = buildarow("Former Occupation:",fileid,'formocc',1)
  self.add(self.formocc)
  self.curocc = buildarow("Current Occupation:",fileid,'currocc',1)
  self.add(self.curocc)
  self.strength = buildarow("Strengths:",fileid,'strength')
  self.add(self.strength)
  self.weak = buildarow("Weakness:",fileid,'weak')
  self.add(self.weak)
  self.mole = buildarow("Mole:",fileid,'mole')
  self.add(self.mole)
  self.hobby = buildarow("Hobby:",fileid,'hobby')
  self.add(self.hobby)
  self.l9 = gtk.Label("Miscellany")
  self.l9.set_alignment(0,1)
  self.l9.show()
  self.add(self.l9)
  self.s4 = gtk.HSeparator()
  self.add(self.s4)
  self.s4.show()
  self.misc = buildarow("Misc:",fileid,'misc') # make a textbox
  self.add(self.misc)
  self.ethnic = buildarow("Ethnic background:",fileid,'ethnic')
  self.add(self.ethnic)
  self.origin = buildarow("Origin:",fileid,'origin')
  self.add(self.origin)
  self.backs = buildarow("Background:",fileid,'backstory') # make a textbox someday?
  self.add(self.backs)
  self.residence = buildarow("Place of residence:",fileid,'residence')
  self.add(self.residence)
  self.minchar = buildarow("Minor related characters:",fileid,'minchar')
  self.add(self.minchar)
  self.talent = buildarow("Talents:",fileid,'talent')
  self.add(self.talent)
  self.abil = buildarow("Abilities:",fileid,'abil') # textbox someday?
  self.add(self.abil)
  self.sgoal = buildarow("Story goal:",fileid,'sgoal')
  self.add(self.sgoal)
  self.other = buildarow("Other notes:",fileid,'other') # textbox someday
  self.add(self.other)

def initPrels(self, fileid,tabs):
  global people
  global config
  name = []
  rels = {}
  nameperson = ""
  try:
    name = [people[fileid]['info']['commonname'][0],people[fileid]['info']['gname'][0],people[fileid]['info']['fname'][0]]
  except KeyError as e:
    print "An error occurred accessing %s: %s" % (fileid,e)
#    print str(people[fileid]['info'].get(e,None))
    return
  if people[fileid].get("relat"):
    rels = people[fileid]['relat']
  if len(name[0]) > 2:
    nameperson = name[0]
  elif config['familyfirst']:
    nameperson = name[2] + " " + name[1]
  else:
    nameperson = name[1] + " " + name[2]
  self.l1 = gtk.Label(nameperson + " - Character's Relationships")
  self.l1.show()
  self.l1.set_alignment(0,0)
  self.b1 = gtk.HBox()
  self.b1.show()
  self.addbutton = gtk.Button("Connect to a Related Record")
  self.addbutton.show()
  self.b1.add(self.l1)
  self.b1.add(self.addbutton)
  self.add(self.b1)
  self.b1.set_child_packing(self.l1,1,1,2,gtk.PACK_START)
  self.b1.set_child_packing(self.addbutton,0,0,2,gtk.PACK_START)
  self.set_child_packing(self.b1,0,0,2,gtk.PACK_START)
  uncatbox = gtk.VBox()
  uncatbox.show()
  if not len(rels):
    self.norels = gtk.Label("No relations found at load time. New relations added will be sorted in the next load.")
    self.norels.show()
    self.add(self.norels)
  else:
#    print str(rels)
    typed = {}
    typed['uncat'] = []
    unname = "New"
    keys = rels.keys()
    for key in keys:
      t = ""
      if rels[key].get("rtype"):
        t = rels[key]['rtype'][0]
      else:
        typed['uncat'].append(key)
      if not typed.get(t):
        typed[t] = []
      typed[t].append(key)
    types = ["fam","friend","work","place"]
    typedesc = ["Family","Friends","Work","Places"]
    for i in range(len(types)):
      if typed.get(types[i]):
        t = types[i]
        if len(typed[t]):
          if config['debug'] > 1: print t + ": " + str(len(typed[t]))
          label = gtk.Label("*** " + typedesc[i] + " ***")
          label.show()
          label.set_alignment(0.05,0.5)
          self.pack_start(label,0,0,2)
          rule = gtk.HSeparator()
          rule.show()
          self.pack_start(rule,0,0,1)
        keys = typed[t]
        keys.sort()
        for key in keys:
          r = rels[key]
          listRel(self,r,fileid,key,tabs)
    if typed.get("uncat"):
      unname = "Uncategorized/New"
    label = gtk.Label("*** %s ***" % unname)
    label.show()
    label.set_alignment(0.05,0.5)
    uncatbox.pack_start(label,0,0,2)
    rule = gtk.HSeparator()
    rule.show()
    uncatbox.pack_start(rule,0,0,1)
    if typed.get("uncat"):
      if config['debug'] > 1: print 'uncat' + ": " + str(len(typed['uncat']))
      keys = typed['uncat']
      keys.sort()
      for key in keys:
        r = rels[key]
        listRel(uncatbox,r,fileid,key,tabs)
  self.addbutton.connect("clicked",connectToPerson,uncatbox,tabs,fileid,"Connect to " + nameperson)
  self.add(uncatbox)
#  self.show_all()

def displayPerson(callingWidget,fileid, tabrow):
  global people
  warnme = False
  if people.get(fileid,None):
    warnme = True
    if not config['openduplicatetabs']: # If it's in our people variable, it's already been loaded
      status.push(0,"'" + fileid + "' is Already open. Switching to existing tab instead of loading...")
      for i in range(len(tabrow)):
        if fileid == tabrow.get_tab_label_text(tabrow.get_nth_page(i)):
          tabrow.set_current_page(i)
      return # No need to load again. If revert needed, use a different function
  else:
    p = loadPerson(fileid)
    people[fileid] = {}
    people[fileid]['info'] = p[0]
    people[fileid]['relat'] = p[1]
  tabrow.ptabs = gtk.Notebook()
  tabrow.ptabs.show()
  tabrow.labelname = gtk.Label(fileid)
  tabrow.labelname.show()
  tabrow.label = gtk.HBox()
  tabrow.label.add(tabrow.labelname)
  tabrow.label.show()
  tabrow.append_page(tabrow.ptabs,tabrow.label)
  tabrow.set_tab_label_text(tabrow.ptabs,fileid)
#  if warnme and config['openduplicatetabs']:
#    tabrow.ptabs.<function to change background color as warning>
#    Here, add a widget at the top of the page saying it's a duplicate, and that care must be taken not to overwrite changes on existing tab.
#    Here, attach ptabs to warning VBox
#  else:
#    Here, attach ptabs to tabrow

  tabrow.labeli = gtk.Label("Information")
  tabrow.labelr = gtk.Label("Relationships")
  tabrow.ptabs.swi = gtk.ScrolledWindow()
  tabrow.ptabs.swr = gtk.ScrolledWindow()
  tabrow.ptabs.swi.set_policy(gtk.POLICY_NEVER,gtk.POLICY_ALWAYS)
  tabrow.ptabs.swr.set_policy(gtk.POLICY_NEVER,gtk.POLICY_ALWAYS)
  tabrow.ptabs.swi.show()
  tabrow.ptabs.swr.show()
  tabrow.ptabs.append_page(tabrow.ptabs.swi,tabrow.labeli)
  tabrow.ptabs.append_page(tabrow.ptabs.swr,tabrow.labelr)
  tabrow.ptabs.set_tab_label_packing(tabrow.ptabs.swi,True,True,gtk.PACK_START)
  tabrow.ptabs.set_tab_label_packing(tabrow.ptabs.swr,True,True,gtk.PACK_START)
  tabrow.ptabs.swi.infpage = gtk.VBox()
  tabrow.ptabs.swr.relpage = gtk.VBox()
  tabrow.ptabs.swi.infpage.show()
  tabrow.ptabs.swr.relpage.show()
  tabrow.ptabs.swi.add_with_viewport(tabrow.ptabs.swi.infpage)
  tabrow.ptabs.swr.add_with_viewport(tabrow.ptabs.swr.relpage)
  tabrow.ptabs.swi.infpage.set_border_width(5)
  tabrow.ptabs.swr.relpage.set_border_width(5)
  if config['debug'] > 2: print "Loading " + tabrow.get_tab_label_text(tabrow.ptabs)
  initPinfo(tabrow.ptabs.swi.infpage, fileid)
  initPrels(tabrow.ptabs.swr.relpage, fileid,tabrow)
  tabrow.set_current_page(tabrow.page_num(tabrow.ptabs))
#  tabrow.show_all()
#  print "I got here, too!"

def addPersonMenu(self):
  itemP = gtk.MenuItem("_Person",True)
  itemP.show()
  self.mb.append(itemP)
  p = gtk.Menu()
  p.show()
  itemP.set_submenu(p)
  itemPN = gtk.MenuItem("_New",True)
  p.append(itemPN)
  itemPN.show()
  itemPN.connect("activate",getFileid,self.tabs)
  if config['uselistfile']:
    itemPC = gtk.MenuItem("_Clear list file",True)
    p.append(itemPC)
    itemPC.show()
    itemPC.connect("activate",killListFile)
  itemPL = gtk.MenuItem("_Load",True)
  p.append(itemPL)
  itemPL.show()
  pl = gtk.Menu()
  pl.show()
  itemPL.set_submenu(pl)
  persons = sorted(worldList['p'])
  num = len(persons)
  every = num
  cols = 1
  if num > 20:
    cols = int(floor(num/20)) + 1
    every = int(num / cols) - 1
  pos = 0
  countitem = gtk.MenuItem("Total Entries: " + str(num))
  pl.append(countitem)
  countitem.show()
  addPersonSubmenu(self.tabs,pl,persons[pos:pos + every])
  if num > every:
    pos += every
    lsm = addPersonSubmenuItem(pl, num - pos)
    for i in range(cols):
      addPersonSubmenu(self.tabs,lsm,persons[pos:pos + every])
      pos += every
      if num > pos + 1:
        lsm = addPersonSubmenuItem(lsm, num - pos)
      elif num == pos:
        addPersonSubmenu(self.tabs,lsm,persons[-1:])

def addPersonSubmenuItem(pl, num):
  itemMore = gtk.MenuItem(str(num) + " _More",True)
  pl.append(itemMore)
  itemMore.show()
  molo = gtk.Menu()
  molo.show()
  itemMore.set_submenu(molo)
  return molo

def addPersonSubmenu(tabs,pl,persons):
  for i in persons:
    menu_items = gtk.MenuItem(i)
    pl.append(menu_items)
    menu_items.connect("activate",displayPerson,i,tabs)
    menu_items.show()

def getFileid(caller,tabs,one = "Please enter a new unique filing identifier.",two = "Fileid:",three = "This will be used to link records together and identify the record on menus. Valid characters are A-Z, 0-9, underscore, and dash. Do not include an extension, such as \".xml\".",four = "New person cancelled"):
  fileid = askBox(None,one,two,three)
  fileid = validateFileid(fileid)
  if len(fileid) > 0:
    mkPerson(caller,fileid,tabs)
  else:
    say(four)

def mkPerson(callingWidget,fileid,tabs):
  global worldList
  if idExists(fileid,'p'):
    say("Existing fileid! Loading instead...")
  else:
    worldList['p'].append(fileid)
### This should go in the save function, check for its value in file?
#    if config['uselistfile'] == True:
#      writeListFile()
  displayPerson(callingWidget,fileid,tabs)

def listRel(self,r,fileid,relid,target = None):
  if not r.get("related"): return
  name = r['related'][0]
  if not r.get("cat"): return
  cat = r['cat'][0]
  if not target: target = self.get_parent().get_parent().get_parent().get_parent() #Which is better?
  namebutton = gtk.Button(relid)
  namebutton.connect("clicked",displayPerson,relid,target) # passing the target or figuring it from parentage?
  row1 = gtk.HBox()
  self.pack_start(row1,0,0,2)
  row1.pack_start(namebutton,1,1,2)
  row1.show()
  namebutton.show()
  namebutton.set_alignment(0.75,0.05)
  namebutton.set_size_request(int(self.size_request()[0] * 0.20),10)
  namelabel = gtk.Label("Name: ")
  namelabel.show()
  row1.pack_start(namelabel,0,0,2)
  namelabel.set_width_chars(6)
  nameentry = gtk.Entry()
  nameentry.show()
  nameentry.set_text(name)
  activateRelEntry(nameentry,fileid,relid,"related")
  row1.pack_start(nameentry,1,1)
  relation = gtk.Label(r['relation'][0])
  relation.show()
  relation.set_width_chars(8)
  row1.pack_start(relation,1,1)
  relset = gtk.Button("Set")
  relset.show()
  relset.set_alignment(0.5,0.5)
  relset.set_size_request(36,24)
  relset.connect("clicked",selectConnectionP,relation,fileid,relid,name,cat)
  row1.pack_start(relset,0,0,5)
  row2 = gtk.HBox()
  self.pack_start(row2,0,0,2)
  row2.show()
  mileadd = gtk.Button("New Milestone")
  mileadd.show()
  mileadd.set_alignment(0.75,0.05)
  mileadd.set_size_request(int(self.size_request()[0] * 0.50),24)
  row2.pack_start(mileadd,0,0,5)
  row2.pack_start(gtk.Label("Date"),1,1,3)
  row2.pack_start(gtk.Label("Event"),1,1,3)
  row2.show_all()
  row3 = gtk.VBox()
  row3.show()
  self.pack_start(row3,0,0,2)
  boxwidth = self.size_request()[0]
  mileadd.connect("clicked",addMilestone,row3,fileid,relid,boxwidth)
  if r.get("events"):
    for i in r['events']:
#      showMile(row3,r,i,fileid,relid)

#def showMile(row3,r,i,fileid,relid):
      events = r['events'][i]
#  print str(events)
      if events.get("date") and events.get("event"):
        rowmile = gtk.HBox()
        rowmile.show()
        blank = gtk.Label()
        blank.show()
        blank.set_size_request(int(boxwidth * 0.20),10)
        rowmile.pack_start(blank,1,1,2)
        d = gtk.Entry()
        d.show()
        d.set_text(events['date'][0])
        activateRelEntry(d,fileid,relid,"date",i)
        rowmile.pack_start(d,1,1,2)
        e = gtk.Entry()
        e.show()
        e.set_text(events['event'][0])
        activateRelEntry(e,fileid,relid,"event",i)
        rowmile.pack_start(e,1,1,2)
        row3.add(rowmile)

def activateRelEntry(self, fileid,relid,key,event = None):
  path = [fileid,"relat",relid]
  if event:
    path.extend(["events",event,key])
  else:
    path.append(key)
  self.connect("focus-out-event", checkForChange,path)

def addMilestone(caller,target,fileid,relid,boxwidth):
  global people
  i = 0
  err = False
  if people.get(fileid):
    if people[fileid].get("relat"):
      if people[fileid]['relat'].get(relid):
        if not people[fileid]['relat'][relid].get("events"):
          people[fileid]['relat'][relid]["events"] = {}
        i = str(len(people[fileid]['relat'][relid]['events']))
        people[fileid]['relat'][relid]['events'][i] = {}
        people[fileid]['relat'][relid]['events'][i]['date'] = ["",False]
        people[fileid]['relat'][relid]['events'][i]['event'] = ["",False]
      else:
        print "Could not find related person " + relid + "!"
        err = True
    else:
      print "Person " + fileid + " has no relations!"
      err = True
  else:
    print "Could not find person " + fileid + "!"
    err = True
  if config['debug'] > 0: print str(target)
  if not err:
    rowmile = gtk.HBox()
    rowmile.show()
    blank = gtk.Label()
    blank.show()
    blank.set_size_request(int(boxwidth * 0.20),10)
    rowmile.pack_start(blank,1,1,2)
    d = gtk.Entry()
    d.show()
    d.set_text(people[fileid]['relat'][relid]['events'][i]['date'][0])
    activateRelEntry(d,fileid,relid,"date",i)
    rowmile.pack_start(d,1,1,2)
    e = gtk.Entry()
    e.show()
    e.set_text(people[fileid]['relat'][relid]['events'][i]['event'][0])
    activateRelEntry(e,fileid,relid,"event",i)
    rowmile.pack_start(e,1,1,2)
    target.add(rowmile)

def connectToPerson(parent,target,tabs,fileid,title = None):
  global status
  relid = recordSelectBox(None,fileid,title)
  if relid and len(relid[1]):
    addRelToBox(parent,target,relid,fileid,tabs)
    status.push(0,"Added connection to %s on %s" % (relid,fileid))
  else:
    status.push(0,"Adding connection on %s cancelled" % fileid)

def addOccMilestone(caller,target,fileid,key):
  global people
  i = 0
  err = False
  if people.get(fileid):
    if people[fileid].get("info"):
      if people[fileid]['info'].get(key):
        if not people[fileid]['info'][key].get("events"):
          people[fileid]['info'][key]['events'] = {}
        i = len(people[fileid]['info'][key]['events'])
        people[fileid]['info'][key]['events'][str(i)] = {}
        people[fileid]['info'][key]['events'][str(i)]['date'] = ["",False]
        people[fileid]['info'][key]['events'][str(i)]['event'] = ["",False]
      else:
        print "Person " + fileid + " has no " + key + "!"
        err = True
    else:
      print "Person " + fileid + " has no info!"
      err = True
  else:
    print "Could not find person " + fileid + "!"
    err = True
  if config['debug'] > 0: print "Target: " + str(target)
  if not err:
    data = people[fileid]['info'][key] # we checked each step this far earlier, so no error check here
    value = data['events'][str(i)].get("date","")
    if value: value = value[0]
    rda = gtk.Entry()
    extraargs = ["events",str(i),"date"]
    activateInfoEntry(rda,fileid,key,len(extraargs),extraargs)
    rda.show()
    rda.set_width_chars(12)
    rda.set_text(value)
    target.attach(rda,1,2,i + 2,i + 3)
    value = data['events'][str(i)].get("event","")
    if value: value = value[0]
    rev = gtk.Entry()
    extraargs = ["events",str(i),"event"]
    activateInfoEntry(rev,fileid,key,len(extraargs),extraargs)
    rev.show()
    rev.set_width_chars(10)
    rev.set_text(value)
    target.attach(rev,2,3,i + 2,i + 3)

def preReadp(force,path,depth = 0):
  """Using the global dict 'people' and given a list of keys 'path' and an integer 'depth', prepares a path
  in the target dict for reading, to a depth of 'depth'. If 'force' is True, the function will build missing
  tree branches, to allow you to write to the endpoint. Do not call force with a path/depth ending in a list,
  tuple, or something other than a dict, which this function produces. Call force on one path higher.
  """
  global people
  if depth > len(path): depth = len(path)
  if depth > 7: depth = 7
  if people.get(path[0]):
    if depth <= 1:
      return True
    if people[path[0]].get(path[1]):
      if depth <= 2:
        return True
      if people[path[0]][path[1]].get(path[2]):
        if depth <= 3:
          return True
        if people[path[0]][path[1]][path[2]].get(path[3]):
          if depth <= 4:
            return True
          if people[path[0]][path[1]][path[2]][path[3]].get(path[4]):
            if depth <= 5:
              return True
            if people[path[0]][path[1]][path[2]][path[3]][path[4]].get(path[5]):
              if depth <= 6:
                return True
              if people[path[0]][path[1]][path[2]][path[3]][path[4]][path[5]].get(path[6]):
                return True # Maximum depth reached
              elif force:
                people[path[0]][path[1]][path[2]][path[3]][path[4]][path[5]][path[6]] = {}
                return preReadp(force,path,depth)
              else: # Not found, and not forcing it to be found
                return False
            elif force:
              people[path[0]][path[1]][path[2]][path[3]][path[4]][path[5]] = {}
              return preReadp(force,path,depth)
            else: # Not found, and not forcing it to be found
              return False
          elif force:
            people[path[0]][path[1]][path[2]][path[3]][path[4]] = {}
            return preReadp(force,path,depth)
          else: # Not found, and not forcing it to be found
            return False
        elif force:
          people[path[0]][path[1]][path[2]][path[3]] = {}
          return preReadp(force,path,depth)
        else: # Not found, and not forcing it to be found
          return False
      elif force:
        people[path[0]][path[1]][path[2]] = {}
        return preReadp(force,path,depth)
      else: # Not found, and not forcing it to be found
        return False
    elif force:
      people[path[0]][path[1]] = {}
      return preReadp(force,path,depth)
    else: # Not found, and not forcing it to be found
      return False
  else: # First level (fileid) can't be generated.
    return False

def getInf(path):
  """Returns the value of a key path, or an empty string."""
  global people
  end = len(path) - 1
  data = people[path[0]]
  i = 1
  while i < end:
    if data.get(path[i]):
      data = data[path[i]]
      i += 1
    else:
      return ""
  (value,mod) = data.get(path[-1],("",False))
  return value

def addRelToBox(self,target,relid,fileid,tabs):
  global people
  cat = relid[1]
  relid = relid[0]
  if preReadp(True,[fileid,"relat"],2):
    name = []
    rels = {}
    nameperson = ""
    if not preReadp(False,[fileid,"relat",relid],3):
      if not preReadp(False,fileid,1):
        p = loadPerson(relid)
        inf = p[0]
        try:
          inf.get("foo",None)
        except AttributeError:
          print "Load Error"
          return
        try:
          name = [inf['commonname'][0],inf['gname'][0],inf['fname'][0]]
        except KeyError as e:
          print "An error occurred accessing %s: %s" % (relid,e)
          return
      else:
        try:
          name = [people[relid]['info']['commonname'][0],people[relid]['info']['gname'][0],people[relid]['info']['fname'][0]]
        except KeyError as e:
          print "An error occurred accessing %s: %s" % (relid,e)
          return
      if len(name[0]) > 2:
        nameperson = name[0]
      elif config['familyfirst']:
        nameperson = name[2] + " " + name[1]
      else:
        nameperson = name[1] + " " + name[2]
      people[fileid]['relat'][relid] = {}
      people[fileid]['relat'][relid]['related'] = [nameperson,True]
      people[fileid]['relat'][relid]['relation'] = ["",False] # Add a dialog here
      people[fileid]['relat'][relid]['cat'] = [cat,True]
      people[fileid]['relat'][relid]['rtype'] = ["",False] # Perhaps all these things in one dialog
      people[fileid]['relat'][relid]['realm'] = ["",False] # Only write this one if user chooses a realm
      # Realm needs to be addressed in the DTD for XML files... not sure if it's hierarchically higher than relat or not, or if realm should just reference connections, rather than be part of their tree (people[fileid]['realm'][realm] = [list,of,relids]
      people[fileid]['relat'][relid]['events'] = {}
      listRel(target,people[fileid]['relat'][relid],fileid,relid,tabs)
    else:
      bsay(self,"Not clobbering existing connection to %s!" % relid)
      return
#  print str(relid) # Succeeded in getting name and type to this point. Going to save the rest for later.

def selectConnectionP(caller,relation,fileid,relid,nameR,cat,genderR = 'n',genderP = 'n'):
  global people
  nameP = ""
  try:
    name = [people[fileid]['info']['commonname'][0],people[fileid]['info']['gname'][0],people[fileid]['info']['fname'][0]]
  except KeyError as e:
    print "An error occurred accessing %s: %s" % (fileid,e)
    return
  if len(name[0]) > 2:
    nameP = name[0]
  elif config['familyfirst']:
    nameP = name[2] + " " + name[1]
  else:
    nameP = name[1] + " " + name[2]
  askbox = gtk.Dialog("Choose connection",None,gtk.DIALOG_DESTROY_WITH_PARENT,("Cancel",86))
  answers = {}
  options = getPersonConnections(cat,genderR,genderP)
  for i in options.keys():
    answers[i] = options[i][0]
  optlist = []
  for key, value in sorted(answers.iteritems(), key=lambda (k,v): (v,k)):
    optlist.append(key)
  row = gtk.HBox()
  row.show()
  label = gtk.Label(nameP)
  label.show()
  label.set_width_chars(20)
  row.pack_start(label,True,True,1)
  label = gtk.Label(nameR)
  label.show()
  label.set_width_chars(20)
  row.pack_start(label,True,True,1)
  askbox.vbox.pack_start(row,True,True,1)
  sw = gtk.ScrolledWindow()
  sw.set_policy(gtk.POLICY_NEVER,gtk.POLICY_ALWAYS)
  sw.set_size_request(400,150)
  sw.show()
  box = gtk.VBox()
  box.show()
  askbox.vbox.pack_start(sw,True,True,1)
  sw.add_with_viewport(box)
  for key in optlist:
    if len(answers[key]) > 0:
      rid = len(answers)
      row = gtk.HBox()
      row.show()
      label = gtk.Label(options[key][1])
      label.show()
      label.set_width_chars(25)
      row.pack_start(label,True,True,1)
      button = gtk.Button(options[key][0])
      button.show()
      button.set_size_request(150,-1)
      button.connect("clicked",askBoxProcessor,askbox,int(key))
      row.pack_start(button,True,True,1)
      box.pack_start(row,True,True,1)
  width, height = askbox.get_size()
  askbox.move((gtk.gdk.screen_width() / 2) - (width / 2),(gtk.gdk.screen_height() / 2) - (height / 2))
  answers['86'] = ""
  answer = askbox.run()
  askbox.destroy()
  if answer < 0: answer = 86
  value = str(answer)
  if len(value) < 2: # Expect 2
    return
  if not preReadp(True,[fileid,'relat',relid],3):
    return
  people[fileid]['relat'][relid]['rtype'] = options[value][2]
  people[fileid]['relat'][relid]['relation'] = options[value][0]
  people[fileid]['relat'][relid]['cat'] = cat
  relation.set_text(people[fileid]['relat'][relid]['relation'])
