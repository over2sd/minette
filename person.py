#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

import pygtk
pygtk.require('2.0')
import gtk
from chardb_backends import (loadPerson, savePerson, config, writeListFile, idExists,worldList)
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

def buildarow(name,fileid,key):
  value = getit(fileid,key)
  row = gtk.HBox()
  row.set_border_width(2)
  row.show()
  row.label = gtk.Label(name)
  row.label.set_width_chars(20)
  row.label.set_alignment(1,0.5)
  row.e = gtk.Entry()
  row.add(row.label)
  row.set_child_packing(row.label,0,0,2,gtk.PACK_START)
  row.add(row.e)
  row.set_child_packing(row.e,1,1,2,gtk.PACK_START)
  row.label.show()
  row.e.set_text(value)
  row.e.show()
  activateEntry(row.e,fileid,key)
  return row

def activateEntry(self, fileid, key):
  self.connect("focus-out-event", checkForChange,fileid, key)

def checkForChange(self,event,fileid, key):
  if getit(fileid,key) != self.get_text():
    markInfoChanged(self,fileid, key)

def markInfoChanged(self,fileid, key): # need some args here
  global people
  self.modify_base(gtk.STATE_NORMAL,gtk.gdk.color_parse("#CCCCDD")) # change background for edited
  goforit = False
  if people.get(fileid,None) != None:
    if people[fileid].get('info',None) != None:
      if people[fileid]['info'].get(key,None) != None:
        goforit = True
      else:
        people[fileid]['info'][key] = ["",False]
        goforit = True
    else:
      print "info not found in " + fileid; return
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
  self.cname = buildarow("Common Name:",fileid,'commonname')
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
  self.formocc = buildarow("Former Occupation:",fileid,'formocc')
  self.add(self.formocc)
  self.curocc = buildarow("Former Occupation:",fileid,'curocc')
  self.add(self.curocc)
  self.strength = buildarow("Strengths:",fileid,'strength')
  self.add(self.strength)
  self.weak = buildarow("Weakness:",fileid,'weak')
  self.add(self.weak)
  self.mole = buildarow("Mole:",fileid,'mole')
  self.add(self.mole)
  self.hobby = buildarow("Hobby:",fileid,'hobby')
  self.add(self.hobby)
  self.l9 = gtk.Label("Personality Traits")
  self.l9.set_alignment(0,1)
  self.l9.show()
  self.add(self.l9)
  self.s4 = gtk.HSeparator()
  self.add(self.s4)
  self.s4.show()
  self.misc = buildarow("Misc:",fileid,'misc')
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


def displayPerson(callingWidget,fileid, tabrow):
  global people
  p = loadPerson(fileid)
  people[fileid] = {}
  people[fileid]['info'] = p[0]
  people[fileid]['relat'] = p[1]
  tabrow.sw = gtk.ScrolledWindow()
  tabrow.sw.set_policy(gtk.POLICY_NEVER,gtk.POLICY_ALWAYS)
  tabrow.sw.show()
  tabrow.sw.personpage = gtk.VBox()
  tabrow.sw.personpage.show()
  tabrow.sw.add_with_viewport(tabrow.sw.personpage)
  tabrow.sw.personpage.set_border_width(5)
  tabrow.labelname = gtk.Label(fileid)
  tabrow.labelname.show()
  tabrow.label = gtk.HBox()
  tabrow.label.add(tabrow.labelname)
  tabrow.label.show()
  tabrow.append_page(tabrow.sw,tabrow.label)
  initPinfo(tabrow.sw.personpage, fileid)
  tabrow.set_current_page(tabrow.page_num(tabrow.sw))

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
  itemPL = gtk.MenuItem("_Load",True)
  p.append(itemPL)
  itemPL.show()
  pl = gtk.Menu()
  pl.show()
  itemPL.set_submenu(pl)
  persons = worldList['p']
  for i in persons:
    menu_items = gtk.MenuItem(i)
    pl.append(menu_items)
    menu_items.connect("activate",displayPerson,i,self.tabs)
    menu_items.show()

def getFileid(callingWidget,fileid,tabs):
  say("Haven't written this function.") # TODO: Write this text entry box.

def mkPerson(callingWidget,fileid,tabs):
  global worldList
  if idExists(fileid,'p'):
    say("Existing fileid! Loading instead...")
  else:
    worldList['p'].append(fileid)
    if config['uselistfile'] == True:
      writeListFile()
  displayPerson(callingWidget,fileid,tabs)
