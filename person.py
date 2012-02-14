#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

import pygtk
pygtk.require('2.0')
import gtk
from chardb_backends import (loadPerson, savePerson, config)

def getit(data,key):
  pair = data.get(key,None)
  if pair != None:
    return pair[0]
  else:
    return ""

def buildarow(name,value):
  row = gtk.HBox()
  row.set_border_width(2)
  row.show()
  row.label = gtk.Label(name)
  row.label.set_width_chars(15)
  row.label.set_justify(gtk.JUSTIFY_RIGHT)
  row.e = gtk.Entry()
  row.add(row.label)
  row.set_child_packing(row.label,0,0,2,gtk.PACK_START)
  row.add(row.e)
  row.set_child_packing(row.e,1,1,2,gtk.PACK_END)
  row.label.show()
  row.e.set_text(value)
  row.e.show()
  return row

def initPinfo(self, info = {}):
  self.l1 = gtk.Label("Name:")
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
  self.ctitle.set_width_chars(5)
  self.namebox.set_child_packing(self.ctitle,0,0,2,gtk.PACK_START)
  self.ctitle.set_text(getit(info,'ctitle'))
  self.ctitle.show()
  if config['familyfirst'] == True:
    self.namebox.add(self.l2)
    self.namebox.add(self.fname)
  self.namebox.add(self.l3)
  self.namebox.add(self.gname)
  self.gname.set_text(getit(info,'gname'))
  self.gname.show()
  self.namebox.add(self.l4)
  self.namebox.add(self.mname)
  self.mname.set_text(getit(info,'mname'))
  self.mname.show()
  if config['familyfirst'] == False:
    self.namebox.add(self.l2)
    self.namebox.add(self.fname)
  self.fname.set_text(getit(info,'fname'))
  self.fname.show()
  self.l1.show()
  self.l2.show()
  self.l3.show()
  self.l4.show()
  self.l5.show()
  self.cname = buildarow("Common Name:",getit(info,'commonname'))
  self.add(self.cname)
  self.nname = buildarow("Nickname:",getit(info,'nname'))
  self.add(self.nname)
  self.gender = buildarow("Gender:",getit(info,'gender')) # TODO: Some day, this will be a radio button
  self.add(self.gender)
  self.bday = buildarow("Birth Date:",getit(info,'bday'))
  self.add(self.bday)
  self.dday = buildarow("Death Date:",getit(info,'dday'))
  self.add(self.dday)
  self.stories = buildarow("Stories:",getit(info,'stories')) # TODO: Some day, this will be a dynamic list of checkboxes
  self.add(self.stories)
  self.mention = buildarow("First Mention:",getit(info,'mention'))
  self.add(self.mention)
  self.appearch = buildarow("1st Appeared (chron):",getit(info,'appear1ch'))
  self.add(self.appearch)
  self.appearwr = buildarow("1st Appeared (writ):",getit(info,'appear1wr'))
  self.add(self.appearwr)
  self.conflict = buildarow("Conflict:",getit(info,'conflict'))
  self.add(self.conflict)
  self.leadrel = buildarow("Relation to lead:",getit(info,'leadrel'))
  self.add(self.leadrel)
  """
bodytyp
age
skin
eyes
hair
dmarks
dress
attpos
asmell

  #"""


def displayPerson(fileid, tabrow):
  p = loadPerson(fileid)
  info = p[0]
  relat = p[1]
  tabrow.personpage = gtk.VBox()
  tabrow.personpage.show()
  tabrow.personpage.set_border_width(5)
  tabrow.labelq = gtk.Label(fileid)
  tabrow.labelq.show()
  tabrow.append_page(tabrow.personpage,tabrow.labelq)
  initPinfo(tabrow.personpage, info)
