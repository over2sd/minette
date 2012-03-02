#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

import pygtk
pygtk.require('2.0')
import gtk

from globdata import (config,places,worldList)
from backends import (loadPlace, savePlace, config, writeListFile, idExists,worldList,killListFile,getCityList)
from common import (say,bsay,askBox,validateFileid,askBoxProcessor,kill,buildarow,getInf,\
activateInfoEntry,activateRelEntry,addMilestone,scrollOnTab,customlabel,activateNoteEntry,skrTimeStamp)
from preread import preReadl
"""
from choices import allPlaceCats
from getmod import (getPlaceConnections,recordSelectBox)
from status import status
from story import (storyPicker,expandTitles)
from math import floor
"""

def addNote(caller,scroll,target,fileid,dval = None,cval = None,i = 0):
  path = [fileid,"info","notes"]
  if not preReadl(True,path,3):
    return
  data = places.get(fileid)
  if i == 0:
    i = str(len(data['info'].get("notes")))
    path.append(i)
    if not preReadl(True,path,4):
      return
    else:
      places[path[0]][path[1]][path[2]][path[3]]['content'] = ["",False]
      places[path[0]][path[1]][path[2]][path[3]]['date'] = [skrTimeStamp(config['datestyle']),False]
  print i
  row = gtk.HBox()
  row.show()
  if not dval: dval = skrTimeStamp(config['datestyle'])
  date = gtk.Label(dval)
  date.show()
  date.set_width_chars(10)
  row.pack_end(date,0,0,2)
  content = gtk.Entry(500)
  content.show()
  if cval: content.set_text(cval)
  activateNoteEntry(content, scroll, data, fileid,i,date)
  row.pack_end(content,1,1,2)
  target.pack_start(row,False,False,2)

def addPlaceMenu(self):
#  displayPlace(self,"p-bleakf",self.tabs)
  pass

def buildLocRow(scroll,data,fileid):
  row = gtk.HBox()
  row.show()
  label = gtk.Label("Location:")
  label.show()
  label
  row.pack_start(label,False,False,2)
  label.set_width_chars(20)
  label.set_alignment(1,0.5)
  choices = getCityList()
  path = ["info","loc"]
  g = getInf(data,path)
#  loc = gtk.ComboBoxText()
  loc = gtk.combo_box_new_text()
  loc.show()
  selected = -1
  keys = []
  i = 0
  for key in sorted(choices.keys()):
    loc.append_text("%s, %s" % (choices[key][0],choices[key][2]))
    keys.append(key)
    if g == key or g == choices[key][0]:
      selected = i
    i += 1
  loc.set_active(selected)
  loc.connect("changed",setLocCombo,fileid)
  loc.connect("move-active",setLocCombo,fileid)
  loc.connect("focus",scrollOnTab,scroll)
  loc.connect("focus-in-event",scrollOnTab,scroll)
  row.pack_start(loc,True,True,2)
  if len(g) and selected == -1:
    path = ["info","state"]
    h = getInf(data,path)
    value = gtk.Label(" (%s, %s) " % (g,h))
    value.show()
    row.pack_start(value,True,True,2)
  return row

def displayPlace(callingWidget,fileid, tabrow):
  global places
  warnme = False
  if places.get(fileid,None):
    warnme = True
    if not config['openduplicatetabs']: # If it's in our people variable, it's already been loaded
      status.push(0,"'" + fileid + "' is Already open. Switching to existing tab instead of loading...")
      for i in range(len(tabrow)):
        if fileid == tabrow.get_tab_label_text(tabrow.get_nth_page(i)):
          tabrow.set_current_page(i)
      return # No need to load again. If revert needed, use a different function
  else:
    L = loadPlace(fileid)
    places[fileid] = {}
    places[fileid]['info'] = L[0]
    places[fileid]['relat'] = L[1]
    places[fileid]['changed'] = False
    places[fileid]['cat'] = 'l'
  tabrow.vbox = gtk.VBox()
  tabrow.vbox.show()
  tabrow.vbox.connect("destroy",tabdestroyed,fileid)
  tabrow.vbox.ltabs = gtk.Notebook()
  tabrow.vbox.ltabs.show()
  bbar = gtk.HButtonBox()
  bbar.show()
  bbar.set_spacing(2)
  save = gtk.Button("Save")
  image = gtk.Image()
  image.set_from_file("img/save.png")
  save.set_image(image)
  save.connect("clicked",saveThisL,fileid)
  save.show()
  bbar.pack_start(save)
  if config['debug'] > 0:
    report = gtk.Button("Report")
    image = gtk.Image()
    image.set_from_file("img/report.png")
    report.set_image(image)
    report.connect("clicked",showPerson,fileid)
    report.show()
    bbar.pack_start(report)
  # endif

# other buttons...   reload,etc.   ...go here

  close = gtk.Button("Close")
  image = gtk.Image()
  image.set_from_file("img/close.png")
  close.set_image(image)
  close.show_all()
  close.connect("clicked",preClose,fileid,tabrow.vbox)
  bbar.pack_end(close)
  tabrow.vbox.pack_start(bbar,False,False,2)
  tabrow.vbox.pack_start(tabrow.vbox.ltabs,True,True,2)
  tabrow.labelname = customlabel('l',fileid,tabrow.vbox)
  tabrow.labelname.show_all()
  tabrow.append_page(tabrow.vbox,tabrow.labelname)
#  if warnme and config['openduplicatetabs']:
#    tabrow.ltabs.<function to change background color as warning>
#    Here, add a widget at the top of the page saying it's a duplicate, and that care must be taken not to overwrite changes on existing tab.
#    Here, attach ltabs to warning VBox
#  else:
#    Here, attach ltabs to tabrow

  tabrow.labeli = gtk.Label("Information")
  tabrow.labelr = gtk.Label("Characters")
  tabrow.vbox.ltabs.swi = gtk.ScrolledWindow()
  tabrow.vbox.ltabs.swr = gtk.ScrolledWindow()
  tabrow.vbox.ltabs.swi.set_policy(gtk.POLICY_NEVER,gtk.POLICY_ALWAYS)
  tabrow.vbox.ltabs.swr.set_policy(gtk.POLICY_NEVER,gtk.POLICY_ALWAYS)
  tabrow.vbox.ltabs.swi.show()
  tabrow.vbox.ltabs.swr.show()
  tabrow.vbox.ltabs.append_page(tabrow.vbox.ltabs.swi,tabrow.labeli)
  tabrow.vbox.ltabs.append_page(tabrow.vbox.ltabs.swr,tabrow.labelr)
  tabrow.vbox.ltabs.set_tab_label_packing(tabrow.vbox.ltabs.swi,True,True,gtk.PACK_START)
  tabrow.vbox.ltabs.set_tab_label_packing(tabrow.vbox.ltabs.swr,True,True,gtk.PACK_START)
  tabrow.vbox.ltabs.swi.infpage = gtk.VBox()
  tabrow.vbox.ltabs.swr.relpage = gtk.VBox()
  tabrow.vbox.ltabs.swi.infpage.show()
  tabrow.vbox.ltabs.swr.relpage.show()
  tabrow.vbox.ltabs.swi.add_with_viewport(tabrow.vbox.ltabs.swi.infpage)
  tabrow.vbox.ltabs.swr.add_with_viewport(tabrow.vbox.ltabs.swr.relpage)
  tabrow.vbox.ltabs.swi.infpage.set_border_width(5)
  tabrow.vbox.ltabs.swr.relpage.set_border_width(5)
  if config['debug'] > 2: print "Loading " + tabrow.get_tab_label_text(tabrow.vbox)
  initLinfo(tabrow.vbox.ltabs.swi.infpage, fileid)
#  initLrels(tabrow.vbox.ltabs.swr.relpage, fileid,tabrow)
  tabrow.set_current_page(tabrow.page_num(tabrow.vbox))

def initLinfo(self, fileid):
  data = {}
  scroll = self.get_parent()
  try:
    data = places.get(fileid)
  except KeyError as e:
    print "An error occurred accessing %s: %s" % (fileid,e)
    return
  scroll = self.get_parent()
  self.namelabelbox = gtk.HBox()
  self.namelabelbox.show()
  label = gtk.Label("Place:")
  label.set_alignment(0,0)
  label.show()
  self.namelabelbox.pack_start(label,1,1,2)
  self.pack_start(self.namelabelbox)
  self.s1 = gtk.HSeparator()
  self.pack_start(self.s1,False,False,2)
  self.s1.show()
  name = buildarow(scroll,"Name:",data,fileid,'name')
  self.pack_start(name,0,0,2)
  commonname = buildarow(scroll,"Common Name:",data,fileid,'commonname')
  self.pack_start(commonname,0,0,2)
  row = gtk.HBox()
  row.show()
  path = ["info","start"]
  label = gtk.Label("Start Date:")
  label.show()
  row.pack_start(label,False,False,2)
  start = gtk.Entry(25)
  start.show()
  start.set_text(getInf(data,path))
  activateInfoEntry(start,scroll,data,fileid,"start")
  row.pack_start(start,True,True,2)
  label = gtk.Label("Cue:")
  label.show()
  row.pack_start(label,False,False,2)
  scue = gtk.Entry(25)
  scue.show()
  path[1] = "scue"
  scue.set_text(getInf(data,path))
  activateInfoEntry(scue,scroll,data,fileid,"scue")
  row.pack_start(scue,True,True,2)
  self.pack_start(row,False,False,2)
  row = gtk.HBox()
  row.show()
  label = gtk.Label("End Date:")
  label.show()
  row.pack_start(label,False,False,2)
  end = gtk.Entry(25)
  end.show()
  path[1] = "end"
  end.set_text(getInf(data,path))
  activateInfoEntry(end,scroll,data,fileid,"end")
  row.pack_start(end,True,True,2)
  label = gtk.Label("Cue:")
  label.show()
  row.pack_start(label,False,False,2)
  ecue = gtk.Entry(25)
  ecue.show()
  path[1] = "ecue"
  ecue.set_text(getInf(data,path))
  activateInfoEntry(ecue,scroll,data,fileid,"ecue")
  row.pack_start(ecue,True,True,2)
  self.pack_start(row,False,False,2)
  label = gtk.Label("Stories")
  label.set_alignment(0,0)
  label.show()
  self.pack_start(label,False,False,2)
  self.s1 = gtk.HSeparator()
  self.pack_start(self.s1,False,False,2)
  self.s1.show()
  self.stories = buildarow(scroll,"Stories:",data,fileid,'stories',2)
  self.pack_start(self.stories,False,False,2)
  self.mention = buildarow(scroll,"First Mentions:",data,fileid,'mention')
  self.pack_start(self.mention,False,False,2)
  self.l7 = gtk.Label("Specifications")
  self.l7.set_alignment(0,1)
  self.l7.show()
  self.pack_start(self.l7,False,False,2)
  self.s2 = gtk.HSeparator()
  self.pack_start(self.s2,False,False,2)
  self.s2.show()
  self.desc = buildarow(scroll,"Description:",data,fileid,'desc')
  self.pack_start(self.desc,False,False,2)
  self.address = buildarow(scroll,"Address:",data,fileid,'address')
  self.pack_start(self.address,False,False,2)
  self.location = buildLocRow(scroll,data,fileid)
  self.pack_start(self.location,False,False,2)
  label = gtk.Label("Notes")
  label.set_alignment(0,0)
  label.show()
  self.pack_start(label,False,False,2)
  self.s1 = gtk.HSeparator()
  self.pack_start(self.s1,False,False,2)
  self.s1.show()
  notebox = gtk.VBox()
  notebox.show()
  self.pack_start(notebox,True,True,2)
  newbut = gtk.Button("Add a note")
  newbut.show()
  image = gtk.Image()
  image.set_from_file("img/add.png")
  newbut.set_image(image)
  newbut.connect("clicked",addNote,scroll,notebox,fileid)
  box = gtk.HBox()
  box.show()
  box.pack_end(newbut,0,0,2)
  label = gtk.Label("Date")
  label.show()
  box.pack_end(label,0,0,2)
  label = gtk.Label("Note")
  label.show()
  box.pack_end(label,1,1,2)
  notebox.pack_start(box,0,0,2)
  notes = data.get("info")
  if notes: notes = notes.get("notes")
  if notes:
    for i in sorted(notes.keys()):
      dval = notes[i].get("date")
      cval = notes[i].get("content")
      if dval and cval: addNote(self,scroll,notebox,fileid,dval,cval,i)

def preClose(caller,fileid,target = None):
  result = -8
  if places.get(fileid):
    if places[fileid].get("changed"):
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
    print "Destroying tab"
    kill(caller,target)
    return True
  else: # No
    print "Cancel"
    return False

def saveThisL(caller,fileid):
  global status
  if places.get(fileid):
    if savePlace(fileid,places[fileid]):
      status.push(0,"%s saved successfully." % fileid)
    else:
      status.push(0,"Error encountered saving %s." % fileid)
  else:
    bsay(caller,"Could not find place %s." % fileid)

def setLoc(caller,fileid,key):
  global places
  lockeys = {}
  if len(key) > 1:
    lockeys = getCityList(1)
    key = lockeys.get(key,'N')
    lockeys = getCityList()
    if config['debug'] > 3: print "new key: %s" % key
    print "%s (%s), %s (%s)" % (lockeys[key][0],key,lockeys[key][2],lockeys[key][1])
    if preReadl(False,[fileid,"info"],2):
      places[fileid]['info']['locfile'] = [key,True]
      places[fileid]['info']['loc'] = [lockeys[key][0],True]
      places[fileid]['info']['statefile'] = [lockeys[key][1],True]
      places[fileid]['info']['state'] = [lockeys[key][2],True]
      places[fileid]['changed'] = True
      if config['debug'] > 0: print "New Loc: %s" % key
  else:
    bsay(None,"Could not set loc for %s." % fileid)

def setLocCombo(widget,fileid):
  setLoc(None,fileid,widget.get_active_text())

def showPlace(caller,fileid):
  if places.get(fileid):
    print places[fileid]

def tabdestroyed(caller,fileid):
  """Deletes the place's fileid key from places dict so the place can be reloaded."""
  global places
  del places[fileid]

