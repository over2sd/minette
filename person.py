#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

import pygtk
pygtk.require('2.0')
import gtk
from math import floor

from backends import (loadPerson, savePerson, config, writeListFile, idExists,worldList)
from choices import allGenders
from common import (say,bsay,askBox,validateFileid,askBoxProcessor,kill,buildarow,getInf,\
activateInfoEntry,activateRelEntry,addMilestone,scrollOnTab,customlabel,expandTitles,\
displayStage1,displayStage2,addLoadSubmenuItem,getFileid,addLocButton)
from debug import printPretty
from getmod import (getPersonConnections,recordSelectBox)
from globdata import people
from preread import preReadp
from status import status
from story import storyPicker

def getit(fileid,key):
  """deprecated function. will be removed eventually."""
  raise NameError("Deprecated function getit")

def initPinfo(self, fileid):
  global people
  global config
  info = {}
  scroll = self.get_parent()
  try:
    info = people[fileid]['info']
  except KeyError as e:
    print "initPinfo: An error occurred accessing %s: %s" % (fileid,e)
    return
  scroll = self.get_parent()
  self.namelabelbox = gtk.HBox()
  self.namelabelbox.show()
  self.l1 = gtk.Label("Name:")
  self.l1.set_alignment(0,0)
  self.namelabelbox.pack_start(self.l1,1,1,2)
  self.nord = gtk.CheckButton("Order reversed")
  self.nord.show()
  self.nord.set_active(isOrderRev(fileid))
  self.nord.unset_flags(gtk.CAN_FOCUS)
  self.nord.connect("clicked",toggleOrder,fileid)
  self.namelabelbox.pack_start(self.nord,0,0,2)
  self.add(self.namelabelbox)
  self.namebox = gtk.HBox()
  self.namebox.set_border_width(2)
  self.add(self.namebox)
  self.namebox.show()
  self.l5 = gtk.Label("Title:")
  self.ctitle = gtk.Entry(5)
  self.l2 = gtk.Label("Family:")
  self.fname = gtk.Entry(25)
  activateInfoEntry(self.fname,scroll,people.get(fileid),fileid,"fname")
  self.l3 = gtk.Label("Given:")
  self.gname = gtk.Entry(25)
  activateInfoEntry(self.gname,scroll,people.get(fileid),fileid,"gname")
  self.l4 = gtk.Label("Middle/Maiden:")
  self.mname = gtk.Entry(25)
  activateInfoEntry(self.mname,scroll,people.get(fileid),fileid,"mname")
  self.namebox.add(self.l5)
  self.namebox.add(self.ctitle)
  self.ctitle.set_width_chars(4)
  self.fname.set_width_chars(10)
  self.gname.set_width_chars(10)
  self.mname.set_width_chars(10)
  self.namebox.set_child_packing(self.ctitle,0,0,2,gtk.PACK_START)
  data = people.get(fileid)
  self.ctitle.set_text(getInf(data,["info","ctitle"]))
  self.ctitle.show()
  activateInfoEntry(self.ctitle,scroll,people.get(fileid),fileid,"ctitle")
  if config['familyfirst'] == True:
    self.namebox.add(self.l2)
    self.namebox.add(self.fname)
  self.namebox.add(self.l3)
  self.namebox.add(self.gname)
  self.gname.set_text(getInf(data,["info","gname"]))
  self.gname.show()
  self.namebox.add(self.l4)
  self.namebox.add(self.mname)
  self.mname.set_text(getInf(data,["info","mname"]))
  if config['usemiddle'] == True:
    self.mname.show()
  if config['familyfirst'] == False:
    self.namebox.add(self.l2)
    self.namebox.add(self.fname)
  self.fname.set_text(getInf(data,["info","fname"]))
  self.fname.show()
  self.l1.show()
  self.l2.show()
  self.l3.show()
  self.l4.show()
  self.l5.show()
  self.cname = buildarow(scroll,"Common Name:",people.get(fileid),fileid,'commonname') # TODO: Some day, maybe move all these labels into a dict and generate these things algorithmically? What about sections?
  self.add(self.cname)
  self.nname = buildarow(scroll,"Nickname:",people.get(fileid),fileid,'nname')
  self.add(self.nname)
  self.gender = buildGenderRow(scroll,people.get(fileid),fileid)
  self.add(self.gender)
  self.bday = buildarow(scroll,"Birth Date:",people.get(fileid),fileid,'bday',3)
  self.add(self.bday)
  self.dday = buildarow(scroll,"Death Date:",people.get(fileid),fileid,'dday',3)
  self.add(self.dday)
  self.l6 = gtk.Label("Stories")
  self.l6.set_alignment(0,0)
  self.l6.show()
  self.add(self.l6)
  self.s1 = gtk.HSeparator()
  self.add(self.s1)
  self.s1.show()
  self.stories = buildarow(scroll,"Stories:",people.get(fileid),fileid,'stories',2)
  self.add(self.stories)
  self.mention = buildarow(scroll,"First Mention:",people.get(fileid),fileid,'mention')
  self.add(self.mention)
  self.appearch = buildarow(scroll,"First appeared (chron):",people.get(fileid),fileid,'appear1ch')
  self.add(self.appearch)
  self.appearwr = buildarow(scroll,"First appeared (writ):",people.get(fileid),fileid,'appear1wr')
  self.add(self.appearwr)
  self.conflict = buildarow(scroll,"Conflict:",people.get(fileid),fileid,'conflict')
  self.add(self.conflict)
  self.leadrel = buildarow(scroll,"Relation to lead:",people.get(fileid),fileid,'leadrel')
  self.add(self.leadrel)
  self.l7 = gtk.Label("Physical Appearance")
  self.l7.set_alignment(0,1)
  self.l7.show()
  self.add(self.l7)
  self.s2 = gtk.HSeparator()
  self.add(self.s2)
  self.s2.show()
  self.bodytyp = buildarow(scroll,"Body Type:",people.get(fileid),fileid,'bodytyp')
  self.add(self.bodytyp)
  self.age = buildarow(scroll,"Age:",people.get(fileid),fileid,'age')
  self.add(self.age)
  self.skin = buildarow(scroll,"Skin:",people.get(fileid),fileid,'skin')
  self.add(self.skin)
  self.eyes = buildarow(scroll,"Eyes:",people.get(fileid),fileid,'eyes')
  self.add(self.eyes)
  self.hair = buildarow(scroll,"Hair:",people.get(fileid),fileid,'hair')
  self.add(self.hair)
  self.dmarks = buildarow(scroll,"Distinguishing Marks:",people.get(fileid),fileid,'dmarks')
  self.add(self.dmarks)
  self.dress = buildarow(scroll,"Dress:",people.get(fileid),fileid,'dress')
  self.add(self.dress)
  self.attpos = buildarow(scroll,"Attached Possessions:",people.get(fileid),fileid,'attposs')
  self.add(self.attpos)
  self.asmell = buildarow(scroll,"Associated Smell:",people.get(fileid),fileid,'asmell')
  self.add(self.asmell)
  self.l8 = gtk.Label("Personality Traits")
  self.l8.set_alignment(0,1)
  self.l8.show()
  self.add(self.l8)
  self.s3 = gtk.HSeparator()
  self.add(self.s3)
  self.s3.show()
  self.pers = buildarow(scroll,"Personality:",people.get(fileid),fileid,'personality')
  self.add(self.pers)
  self.speech = buildarow(scroll,"Distinct Speech:",people.get(fileid),fileid,'speech')
  self.add(self.speech)
  self.formocc = buildarow(scroll,"Former Occupation:",people.get(fileid),fileid,'formocc',1)
  self.add(self.formocc)
  self.curocc = buildarow(scroll,"Current Occupation:",people.get(fileid),fileid,'currocc',1)
  self.add(self.curocc)
  self.strength = buildarow(scroll,"Strengths:",people.get(fileid),fileid,'strength')
  self.add(self.strength)
  self.weak = buildarow(scroll,"Weakness:",people.get(fileid),fileid,'weak')
  self.add(self.weak)
  self.mole = buildarow(scroll,"Mole:",people.get(fileid),fileid,'mole')
  self.add(self.mole)
  self.hobby = buildarow(scroll,"Hobby:",people.get(fileid),fileid,'hobby')
  self.add(self.hobby)
  self.l9 = gtk.Label("Miscellany")
  self.l9.set_alignment(0,1)
  self.l9.show()
  self.add(self.l9)
  self.s4 = gtk.HSeparator()
  self.add(self.s4)
  self.s4.show()
  self.misc = buildarow(scroll,"Misc:",people.get(fileid),fileid,'misc') # make a textbox
  self.add(self.misc)
  self.ethnic = buildarow(scroll,"Ethnic background:",people.get(fileid),fileid,'ethnic')
  self.add(self.ethnic)
  self.origin = buildarow(scroll,"Origin:",people.get(fileid),fileid,'origin')
  addLocButton(self.origin,entry=self.origin.e)
  self.origin.e.grab_focus()
  self.add(self.origin)
  self.backs = buildarow(scroll,"Background:",people.get(fileid),fileid,'backstory') # make a textbox someday?
  self.add(self.backs)
  self.residence = buildarow(scroll,"Place of residence:",people.get(fileid),fileid,'residence')
  self.add(self.residence)
  self.minchar = buildarow(scroll,"Minor related characters:",people.get(fileid),fileid,'minchar')
  self.add(self.minchar)
  self.talent = buildarow(scroll,"Talents:",people.get(fileid),fileid,'talent')
  self.add(self.talent)
  self.abil = buildarow(scroll,"Abilities:",people.get(fileid),fileid,'abil') # textbox someday?
  self.add(self.abil)
  self.sgoal = buildarow(scroll,"Story goal:",people.get(fileid),fileid,'sgoal')
  self.add(self.sgoal)
  self.other = buildarow(scroll,"Other notes:",people.get(fileid),fileid,'other') # textbox someday
  self.add(self.other)

def initPrels(self, fileid,tabs):
  scroll = self.get_parent()
  global people
  global config
  name = []
  rels = {}
  nameperson = ""
  try:
    name = [people[fileid]['info']['commonname'][0],people[fileid]['info']['gname'][0],people[fileid]['info']['fname'][0]]
  except KeyError as e:
    print "initPrels: An error occurred accessing %s: %s" % (fileid,e)
    if config['debug'] > 5: print str(people[fileid]['info'].get(e,None))
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
          listRel(self,r,fileid,key,scroll,tabs)
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
        listRel(uncatbox,r,fileid,key,scroll,tabs)
  self.addbutton.connect("clicked",connectToPerson,uncatbox,tabs,scroll,fileid,"Connect to " + nameperson)
  self.add(uncatbox)

def displayPerson(callingWidget,fileid, tabrow):
  global people
  warnme = False
  if people.get(fileid,None):
    tab = people[fileid].get("tab")
    if tab is not None:
      warnme = True
      if not config['openduplicatetabs']: # If it's in our people variable, it's already been loaded
        status.push(0,"'" + fileid + "' is Already open. Switching to existing tab instead of loading...")
        tabrow.set_current_page(tab)
        for i in range(len(tabrow)):
          if fileid == tabrow.get_tab_label_text(tabrow.get_nth_page(i)):
            tabrow.set_current_page(i)
        return # No need to load again. If revert needed, use a different function
  else:
    p = loadPerson(fileid)
    people[fileid] = {}
    people[fileid]['info'] = p[0]
    people[fileid]['relat'] = p[1]
    people[fileid]['changed'] = False
    people[fileid]['cat'] = 'p'
  displayStage1(tabrow,fileid,'p',saveThisP,showPerson,preClose,displayPerson)
  tabrow.vbox.connect("destroy",tabdestroyed,fileid)
  tabrow.labeli = gtk.Label("Information")
  tabrow.labelr = gtk.Label("Relationships")
  tabrow.vbox.ftabs.infpage = displayStage2(tabrow.vbox.ftabs,tabrow.labeli)
  tabrow.vbox.ftabs.relpage = displayStage2(tabrow.vbox.ftabs,tabrow.labelr)
  if config['debug'] > 2: print "Loading " + tabrow.get_tab_label_text(tabrow.vbox)
  initPinfo(tabrow.vbox.ftabs.infpage, fileid)
  initPrels(tabrow.vbox.ftabs.relpage, fileid,tabrow)
  tabrow.set_current_page(tabrow.page_num(tabrow.vbox))
  people[fileid]["tab"] = tabrow.page_num(tabrow.vbox)

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
  itemPN.connect("activate",getFileid,self.tabs,mkPerson,"person")
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
    lsm = addLoadSubmenuItem(pl, num - pos)
    for i in range(cols):
      addPersonSubmenu(self.tabs,lsm,persons[pos:pos + every])
      pos += every
      if num > pos + 1:
        lsm = addLoadSubmenuItem(lsm, num - pos)
      elif num == pos:
        addPersonSubmenu(self.tabs,lsm,persons[-1:])

def addPersonSubmenu(tabs,pl,persons):
  digits = "123456789ABCDEFGHIJKL"
  for i in persons:
    n = -1
    if persons.index(i) < len(digits): n = persons.index(i)
    item = i
    if n != -1: item = "_%s %s" % (digits[n],i)
    menu_items = gtk.MenuItem(item,True)
    pl.append(menu_items)
    menu_items.connect("activate",displayPerson,i,tabs)
    menu_items.show()

def mkPerson(callingWidget,fileid,tabs):
  global people
  if idExists(fileid,'p'):
    say("Existing fileid! Loading instead...")
  else:
    p = loadPerson(fileid)
    people[fileid] = {}
    people[fileid]['info'] = p[0]
    people[fileid]['relat'] = p[1]
    people[fileid]['changed'] = False
    people[fileid]['cat'] = 'p'
    saveThisP(callingWidget,fileid)
  displayPerson(callingWidget,fileid,tabs)

def listRel(self,r,fileid,relid,scroll,target = None):
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
  activateRelEntry(nameentry,scroll,people.get(fileid),fileid,relid,"related")
  row1.pack_start(nameentry,1,1)
  relation = gtk.Label(r['relation'][0])
  relation.show()
  relation.set_width_chars(8)
  row1.pack_start(relation,1,1)
  relset = gtk.Button("Set")
  relset.show()
  relset.set_alignment(0.5,0.5)
  relset.set_size_request(36,24)
  data = people.get(relid,None)
  genderR = ""
  if data: genderR = getInf(data,["info","gender"])
  if not genderR or genderR == "":
    p = loadPerson(relid)
    genderR = p[0].get("gender",['N',False])
    genderR = genderR[0]
  genderP = getInf(people.get(fileid),["info","gender"])
  relset.connect("clicked",selectConnectionP,relation,fileid,relid,name,cat,genderR,genderP)
  row1.pack_start(relset,0,0,5)
  row2 = gtk.HBox()
  self.pack_start(row2,0,0,2)
  row2.show()
  mileadd = gtk.Button("New Milestone")
  mileadd.show()
  mileadd.set_alignment(0.75,0.05)
#  mileadd.set_size_request(int(self.size_request()[0] * 0.30),24)
  row2.pack_start(mileadd,0,0,5)
  dhead = gtk.Label("Date")
  dhead.show()
  dhead.set_width_chars(8)
  row2.pack_start(dhead,1,1,2)
  ehead = gtk.Label("Event")
  ehead.show()
  ehead.set_width_chars(18)
  row2.pack_start(ehead,1,1,2)
  row2.show_all()
  row3 = gtk.VBox()
  row3.show()
  self.pack_start(row3,0,0,2)
  boxwidth = self.size_request()[0]
  mileadd.connect("clicked",addMilestone,scroll,row3,people.get(fileid),fileid,"relat",relid,boxwidth)
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
        blank.set_width_chars(12)
        rowmile.pack_start(blank,0,0,2)
        d = gtk.Entry()
        d.show()
        d.set_width_chars(12)
        d.set_text(events['date'][0])
        data = people.get(fileid)
        activateRelEntry(d,scroll,data,fileid,relid,"date",i)
        rowmile.pack_start(d,1,1,2)
        e = gtk.Entry()
        e.show()
        e.set_width_chars(18)
        e.set_text(events['event'][0])
        activateRelEntry(e,scroll,data,fileid,relid,"event",i)
        rowmile.pack_start(e,1,1,2)
        row3.add(rowmile)

def connectToPerson(parent,target,tabs,scroll,fileid,title = ""):
  global status
  relid = recordSelectBox(None,fileid,title)
  if relid and len(relid[1]):
    addRelToBox(parent,target,relid,fileid,tabs,scroll)
    status.push(0,"Added connection to %s on %s" % (relid,fileid))
  else:
    status.push(0,"Adding connection on %s cancelled" % fileid)

def addRelToBox(self,target,relid,fileid,tabs,scroll):
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
          print "addRelToBox: Load Error"
          return
        try:
          name = [inf['commonname'][0],inf['gname'][0],inf['fname'][0]]
        except KeyError as e:
          print "addRelToBox: An error occurred accessing relation %s: %s" % (relid,e)
          return
      else:
        try:
          name = [people[relid]['info']['commonname'][0],people[relid]['info']['gname'][0],people[relid]['info']['fname'][0]]
        except KeyError as e:
          print "addRelToBox: An error occurred accessing person %s: %s" % (relid,e)
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
      # Realm needs to be addressed in the DTD for XML files... not sure if it's hierarchically higher than relat or not, or if realm should just reference connections, rather than be part of their tree (people[fileid]['realm'][realm] = [list,of,relids])
      people[fileid]['relat'][relid]['events'] = {}
      listRel(target,people[fileid]['relat'][relid],fileid,relid,scroll,tabs)
    else:
      bsay(self,"Not clobbering existing connection to %s!" % relid)
      return

def selectConnectionP(caller,relation,fileid,relid,nameR,cat,genderR = 'N',genderP = 'N'):
  global people
  rl = len(str(genderR))
  pl = len(str(genderP))
  if rl > 1 or pl > 1:
    if config['debug'] > 5: print "Received R: %s P: %s" % (genderR,genderP)
    print "Gender must be a single character: Attempting to convert."
    choices = allGenders(1)
    if rl > 1:
      genderR = choices.get(genderR,'N')
    if pl > 1:
      genderP = choices.get(genderP,'N')
  nameP = ""
  try:
    name = [people[fileid]['info']['commonname'][0],people[fileid]['info']['gname'][0],people[fileid]['info']['fname'][0]]
  except KeyError as e:
    print "selectConnectionP: An error occurred accessing %s: %s" % (fileid,e)
    return
  if len(name[0]) > 2:
    nameP = name[0]
  elif config['familyfirst']:
    nameP = name[2] + " " + name[1]
  else:
    nameP = name[1] + " " + name[2]
  askbox = gtk.Dialog("Choose connection",None,gtk.DIALOG_DESTROY_WITH_PARENT,("Cancel",86))
  answers = {}
  options = getPersonConnections(cat,str(genderR),str(genderP))
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
  if not preReadp(True,[fileid,'relat',relid],3): # This should have been here already.
    return
  if value == "86": return # Cancel
  people[fileid]['relat'][relid]['rtype'] = options[value][2]
  people[fileid]['relat'][relid]['relation'] = options[value][0]
  people[fileid]['relat'][relid]['cat'] = cat
  relation.set_text(people[fileid]['relat'][relid]['relation'])
  # TODO: some day, maybe edit and save the other person with reciprocal relational information.

def showPerson(caller,fileid):
  if people.get(fileid):
    print people[fileid]

def saveThisP(caller,fileid):
  global status
  if people.get(fileid):
    if savePerson(fileid,people[fileid]):
      status.push(0,"%s saved successfully." % fileid)
    else:
      status.push(0,"Error encountered saving %s." % fileid)
  else:
    bsay(caller,"saveThisP: Could not find person %s." % fileid)

def isOrderRev(fileid):
  global config
  norm = "gf"
  if config['familyfirst']: norm = "fg"
  value = getInf(people.get(fileid),["info","nameorder"])
  if value == norm or not value:
    return False
  else:
    return True

def toggleOrder(caller,fileid):
  global people
  global config
  rev = "fg"
  norm = "gf"
  if config['familyfirst']:
    norm = rev
    rev = "gf"
  if not preReadp(True,[fileid,"info"],2):
    return
  if caller.get_active():
    print "Name is now reversed!"
    people[fileid]['info']['nameorder'] = [rev,True]
    people[fileid]['changed'] = True
  else:
    print "Name is now normal!"
    people[fileid]['info']['nameorder'] = [norm,True]
    people[fileid]['changed'] = True

def buildGenderRow(scroll,data,fileid,display = 0):
  row = gtk.HBox()
  row.show()
  label = gtk.Label("Gender:")
  label.show()
  label
  row.pack_start(label,False,False,2)
  label.set_width_chars(20)
  label.set_alignment(1,0.5)
  choices = allGenders()
  path = ["info","gender"]
  g = getInf(data,path)
  if display == 1:
    radio = gtk.VBox()
    radio.show()
    row.pack_start(radio,True,True,2)
    group = None
    for key in sorted(choices.keys()):
      rbut = gtk.RadioButton(group,choices[key])
      rbut.connect("clicked",setGender,fileid,key)
      if config['debug'] > 5: print "%s : %s : %s" % (g,key,choices[key])
      if g == key or g == choices[key]:
        rbut.set_active(True)
      rbut.show()
      group = rbut
      radio.pack_start(rbut,False,False,2)
  else:
#    gender = gtk.ComboBoxText()
    gender = gtk.combo_box_new_text()
    gender.show()
    selected = -1
    keys = []
    i = 0
    for key in sorted(choices.keys()):
      gender.append_text(choices[key])
      keys.append(key)
      if g == key or g == choices[key]:
        selected = i
      i += 1
    gender.set_active(selected)
    gender.connect("changed",setGenderCombo,None,fileid) # move-action sends an event, so must fill its place when change sends without one
    gender.connect("move-active",setGenderCombo,fileid)
    gender.connect("focus",scrollOnTab,scroll)
    gender.connect("focus-in-event",scrollOnTab,scroll)
    row.pack_start(gender,True,True,2)
  return row

def setGenderCombo(widget,event,fileid):
  setGender(None,fileid,widget.get_active_text())
  print "Gender changed."

def setGender(caller,fileid,key):
  global people
  if len(key) > 1:
    genderkeys = allGenders(1)
    key = genderkeys.get(key,'N')
    if config['debug'] > 3: print "new key: %s" % key
  if preReadp(False,[fileid,"info","gender"],2):
    people[fileid]['info']['gender'] = [key,True]
    people[fileid]['changed'] = True
    if config['debug'] > 2: print "New Gender: %s" % key
  else:
    bsay(None,"setGender: Could not set gender for %s." % fileid)

def preClose(caller,fileid,target = None):
  result = -8
  if people.get(fileid):
    if people[fileid].get("changed"):
      result = 0
      caller.set_sensitive(False)
      asker = gtk.MessageDialog(None,gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,gtk.MESSAGE_INFO,gtk.BUTTONS_YES_NO,None)
      asker.set_markup("Are you sure you want to close %s?\nYou will lose all unsaved changes." % fileid)
      asker.connect("destroy",lambda x: caller.set_sensitive(True))
      (x,y,w,h) = caller.get_allocation()
      asker.move(x - 50,y - 50)
      result = asker.run()
      asker.destroy()
  if result == -8: # Yes
    print "Destroying tab %s" % fileid
    kill(caller,target)
    return True
  else: # No
    print "Cancel"
    return False

def tabdestroyed(caller,fileid):
  """Deletes the person's fileid key from people dict so the person can be reloaded."""
  global people
  try:
    del people[fileid]
  except KeyError:
    printPretty(people)
    raise
