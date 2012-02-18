#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

import pygtk
pygtk.require('2.0')
import gtk
from backends import (loadPerson, savePerson, config, writeListFile, idExists,worldList,killListFile)
from common import (say,bsay,askBox,validateFileid,recordSelectBox)
from status import status
people = {}

def getit(fileid,key):
  global people
  data = {}
  try:
    data = people[fileid]['info']
  except KeyError as e:
    print "Error getting info from " + fileid + ": %s" % e
    return ""
  pair = data.get(key,None)
  if pair != None:
    return pair[0]
  else:
    return ""

def buildarow(name,fileid,key,style = 0):
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
    value = getit(fileid,key)
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
  t = gtk.Table(1,4) # TODO: Move this out into the buildarow so we can pu multiple positions in the same table?
  # or do we want them separated so we have the headers and separation?
  t.show()
  global people
  data = {}
  try:
    data = people[fileid]['info']
  except KeyError as e:
    print "Error getting info from " + fileid + ": %s" % e
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
    t.addmile.connect("clicked",bsay,"This button does nothing yet.")
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
  self.connect("focus-out-event", checkInfoForChange,fileid, key,extra,exargs)

def checkInfoForChange(self,event,fileid,key,extra = 0,exargs = []):
  if extra == 0:
    if getit(fileid,key) != self.get_text():
      markInfoChanged(self,fileid, key)
  elif extra > 0:
    value = ""
    NOGOOD = "There was a missing key "
    if people.get(fileid,None) != None:
      if people[fileid].get('info',None) != None:
        if people[fileid]['info'].get(key,None) != None:
          if people[fileid]['info'][key].get(exargs[0]) != None:
            if extra == 1:
              try:
                value = people[fileid]['info'][key].get(exargs[0])
              except KeyError:
                value = ""
            elif extra == 2:
              try:
                value = people[fileid]['info'][key][exargs[0]].get(exargs[1])
              except KeyError:
                value = ""
            elif extra == 3:
              try:
                value = people[fileid]['info'][key][exargs[0]][exargs[1]].get(exargs[2])
              except KeyError:
                value = ""
            elif extra == 4:
              try:
                value = people[fileid]['info'][key][exargs[0]][exargs[1]][exargs[2]].get(exargs[3])
              except KeyError:
                value = ""
            elif extra == 5:
              try:
                value = people[fileid]['info'][key][exargs[0]][exargs[1]][exargs[2]][exargs[3]].get(exargs[4])
              except KeyError:
                value = ""
            else:
              say("A counting error occurred. Oops.")
            if value[0] != self.get_text():
              markInfoChanged(self,fileid, key,extra,exargs)
          else: say(NOGOOD + exargs[0])
        else: say(NOGOOD + key)
      else: say(NOGOOD + "info")
    else: say(NOGOOD + fileid)

def markInfoChanged(self,fileid, key,extra = 0,exargs = []): # need some args here
  if extra != len(exargs): say("Counting error! " + str(extra) + "/" + str(len(exargs)))
  global people
  self.modify_base(gtk.STATE_NORMAL,gtk.gdk.color_parse("#CCCCDD")) # change background for edited
  goforit = False
  if people.get(fileid,None) != None:
    if people[fileid].get('info',None) != None:
        if people[fileid]['info'].get(key,None) == None:
          people[fileid]['info'][key] = ["",False]
        if len(exargs) == 0:
          say("exargs empty!")
          return
        if people[fileid]['info'].get(key,None) == None:
          people[fileid]['info'][key] = {}
        if people[fileid]['info'][key].get(exargs[0]) != None:
          if extra >= 1:
            try:
              value = people[fileid]['info'][key].get(exargs[0])
            except KeyError:
              people[fileid]['info'][key][exargs[0]] = {}
            if extra == 1:
              try:
                people[fileid]['info'][key][exargs[0]] = ["",False]
                people[fileid]['info'][key][exargs[0]][1] = True
                people[fileid]['info'][key][exargs[0]][0] = self.get_text()
                print "Value set: " + str(people[fileid]['info'][key][exargs[0]][0])
                return
              except KeyError:
                print "Could not mark " + exargs[0] + " as changed."
                return
            elif extra > 1:
              try:
                value = people[fileid]['info'][key][exargs[0]].get(exargs[1])
              except KeyError:
                people[fileid]['info'][key][exargs[0]][exargs[1]] = {}
              if extra == 2:
                try:
                  people[fileid]['info'][key][exargs[0]][exargs[1]] = ["",False]
                  people[fileid]['info'][key][exargs[0]][exargs[1]][1] = True
                  people[fileid]['info'][key][exargs[0]][exargs[1]][0] = self.get_text()
                  print "Value set: " + str(people[fileid]['info'][key][exargs[0]][exargs[1]][0])
                  return
                except KeyError:
                  print "Could not mark " + exargs[1] + " as changed."
                  return
              elif extra > 2:
                try:
                  value = people[fileid]['info'][key][exargs[0]][exargs[1]].get(exargs[2])
                except KeyError:
                  people[fileid]['info'][key][exargs[0]][exargs[1]][exargs[2]] = {}
                if extra == 3:
                  try:
                    people[fileid]['info'][key][exargs[0]][exargs[1]][exargs[2]] = ["",False]
                    people[fileid]['info'][key][exargs[0]][exargs[1]][exargs[2]][1] = True
                    people[fileid]['info'][key][exargs[0]][exargs[1]][exargs[2]][0] = self.get_text()
                    print "Value set: " + str(people[fileid]['info'][key][exargs[0]][exargs[1]][exargs[2]][0])
                    return
                  except KeyError:
                    print "Could not mark " + exargs[2] + " as changed."
                    return
                elif extra > 3:
                  try:
                    value = people[fileid]['info'][key][exargs[0]][exargs[1]][exargs[2]].get(exargs[3])
                  except KeyError:
                    people[fileid]['info'][key][exargs[0]][exargs[1]][exargs[2]] = {}
                  if extra == 4:
                    try:
                      people[fileid]['info'][key][exargs[0]][exargs[1]][exargs[2]][exargs[3]] = ["",False]
                      people[fileid]['info'][key][exargs[0]][exargs[1]][exargs[2]][exargs[3]][1] = True
                      people[fileid]['info'][key][exargs[0]][exargs[1]][exargs[2]][exargs[3]][0] = self.get_text()
                      print "Value set: " + str(people[fileid]['info'][key][exargs[0]][exargs[1]][exargs[2]][exargs[3]][0])
                      return
                    except KeyError:
                      print "Could not mark " + exargs[3] + " as changed."
                      return
                  elif extra > 4:
                    try:
                      value = people[fileid]['info'][key][exargs[0]][exargs[1]][exargs[2]][exargs[3]].get(exargs[4])
                    except KeyError:
                      people[fileid]['info'][key][exargs[0]][exargs[1]][exargs[2]][exargs[3]] = {}
                    if extra == 5:
                      try:
                        people[fileid]['info'][key][exargs[0]][exargs[1]][exargs[2]][exargs[3]][exargs[4]] = ["",False]
                        people[fileid]['info'][key][exargs[0]][exargs[1]][exargs[2]][exargs[3]][exargs[4]][1] = True
                        people[fileid]['info'][key][exargs[0]][exargs[1]][exargs[2]][exargs[3]][exargs[4]][0] = self.get_text()
                        print "Value set: " + str(people[fileid]['info'][key][exargs[0]][exargs[1]][exargs[2]][exargs[3]][exargs[3]][exargs[4]][0])
                        return
                      except KeyError:
                        print "Could not mark " + exargs[3] + " as changed."
                        return
                    else:
                      say("Arguments out of bounds")
                      return
    else:
      print "info not found in " + fileid; return
    people[fileid]['changed'] = True
  else:
    print fileid + " not found in people"; return
  if goforit:
    try:
      people[fileid]['info'][key][1] = True
      people[fileid]['info'][key][0] = self.get_text()
      print "Value set: " + str(people[fileid]['info'][key][0])
    except KeyError:
      print "Could not mark " + key + " in " + fileid + " as changed."
      return

def initPinfo(self, fileid):
  global people
  global config
  info = {}
  try:
    info = people[fileid]['info']
  except KeyError as e:
    print "An error occurred accessing " + fileid + ": %s" % e
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
    print "An error occurred accessing " + fileid + ": %s" % e
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
        if len(typed['uncat']):
          if config['debug'] > 1: print 'uncat' + ": " + str(len(typed['uncat']))
          label = gtk.Label("*** Uncategorized/New ***")
          label.show()
          label.set_alignment(0.05,0.5)
          uncatbox.pack_start(label,0,0,2)
          rule = gtk.HSeparator()
          rule.show()
          uncatbox.pack_start(rule,0,0,1)
        keys = typed['uncat']
        keys.sort()
        for key in keys:
          r = rels[key]
          listRel(uncatbox,r,fileid,key,tabs)
  self.addbutton.connect("clicked",connectToPerson,uncatbox,fileid,"Connect to " + nameperson)
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
    cols = 2
    if num > 40:
      cols = 3
      if num > 60:
        cols = 4
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

def getFileid(caller,tabs):
  fileid = askBox(None,"Please enter a new unique filing identifier.","Fileid:","This will be used to link records together and identify the record on menus. Valid characters are A-Z, 0-9, underscore, and dash. Do not include an extension, such as \".xml\".")
  fileid = validateFileid(fileid)
  if len(fileid) > 0:
    mkPerson(caller,fileid,tabs)
  else:
    say("New person cancelled")

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
  row1.pack_start(relset,0,0,5)
  row2 = gtk.HBox()
  self.pack_start(row2,0,0,2)
  row2.show()
  mileadd = gtk.Button("New Milestone")
  mileadd.show()
  mileadd.set_alignment(0.75,0.05)
  mileadd.set_size_request(int(self.size_request()[0] * 0.25),24)
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
  self.connect("focus-out-event", checkRelForChange,fileid,relid,key,event)

def checkRelForChange(self,signal,fileid,relid,key,event = None):
  if getrel(fileid,relid,key,event) != self.get_text():
    print str(getrel(fileid,relid,key,event)) + " vs " + self.get_text()
    markRelChanged(self,fileid,relid,key,event)

def getrel(fileid,relid,key,event = None):
# TODO: This is broken, but I can't figure it out tonight. I'll tackle it later.
  value = ""
  if event:
    try:
      value = people[fileid]['relat'][relid]['events'][event][key][0]
    except KeyError as e:
      return ""
  else:
    try:
      value = people[fileid]['relat'][relid][key][0]
    except KeyError as e:
      return ""
  return value

def markRelChanged(self,fileid,relid,key,event = None): # need some args here
  global people
  self.modify_base(gtk.STATE_NORMAL,gtk.gdk.color_parse("#CCCCDD")) # change background for edited
  if people.get(fileid,None) != None:
    if people[fileid].get('relat',None) != None:
      if people[fileid]['relat'][relid].get(relid,None) == None:
        people[fileid]['relat'][relid] = {}
        if event:
          if people[fileid]['relat'][relid].get("events",None) == None:
            people[fileid]['relat'][relid]['events'] = {}
            if people[fileid]['relat'][relid]['events'].get(event,None) == None:
              people[fileid]['relat'][relid]['events'][event] = {}
          try:
            value = people[fileid]['relat'][relid]['events'][event].get(key)
          except KeyError:
            people[fileid]['relat'][relid]['events'][event][key] = {}
          try:
            people[fileid]['relat'][relid]['events'][event][key] = ["",False]
            people[fileid]['relat'][relid]['events'][event][key][1] = True
            people[fileid]['relat'][relid]['events'][event][key][0] = self.get_text()
            print "Value set: " + str(people[fileid]['relat'][relid]['events'][event][key][0])
            return
          except KeyError:
            print "Could not mark " + key + " as changed."
            return
        else:
          if people[fileid]['relat'][relid].get(key,None) == None:
            people[fileid]['relat'][relid][key] = ["",False]
          people[fileid]['relat'][relid][key] = [self.get_text(),True]
          print "Value set: " + str(people[fileid]['relat'][relid][key][0])

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

def connectToPerson(parent,target,fileid,title = None):
  global status
  relid = recordSelectBox(None,fileid,title)
  if len(relid[1]):
    addRelToBox(target,relid,fileid)
    status.push(0,"Added connection to %s on %s" % (relid,fileid))
  else:
    status.push(0,"Adding connection on %s cancelled" % fileid)

def addRelToBox(target,relid,fileid):
    print str(relid) # Succeeded in getting name and type to this point. Going to save the rest for later.