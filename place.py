#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

import pygtk
pygtk.require('2.0')
import gtk
from math import floor

from backends import (loadPlace, savePlace, config, writeListFile, idExists,worldList,killListFile,getCityList)
from common import (say,bsay,askBox,validateFileid,askBoxProcessor,kill,buildarow,getInf,\
activateInfoEntry,activateRelEntry,addMilestone,scrollOnTab,customlabel,activateNoteEntry,\
skrTimeStamp,addLoadSubmenuItem,expandTitles,placeCalendarButton,preRead,displayStage1,\
displayStage2,dateChoose)
from debug import printPretty
from getmod import (getPlaceConnections,recordSelectBox)
from globdata import (config,places,worldList)
from status import status
from story import (storyPicker,)
"""
from choices import allPlaceCats
"""

def addNote(caller,scroll,target,fileid,dval = None,cval = None,i = 0):
  path = [fileid,"info","notes"]
  if not preRead(True,'l',path,3):
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
  row.pack_end(content,1,1,2)
  target.pack_start(row,False,False,2)
  activateNoteEntry(content, scroll, data, fileid,i,date)

def addPlaceMenu(self):
  itemL = gtk.MenuItem("P_lace",True)
  itemL.show()
  self.mb.append(itemL)
  l = gtk.Menu()
  l.show()
  itemL.set_submenu(l)
  itemLN = gtk.MenuItem("_New",True)
  l.append(itemLN)
  itemLN.show()
  itemLN.connect("activate",getFileid,self.tabs)
  itemLL = gtk.MenuItem("_Load",True)
  l.append(itemLL)
  itemLL.show()
  ll = gtk.Menu()
  ll.show()
  itemLL.set_submenu(ll)
  places = sorted(worldList['l'])
  num = len(places)
  every = num
  cols = 1
  if num > 20:
    cols = int(floor(num/20)) + 1
    every = int(num / cols) - 1
  pos = 0
  countitem = gtk.MenuItem("Total Entries: " + str(num))
  ll.append(countitem)
  countitem.show()
  addPlaceSubmenu(self.tabs,ll,places[pos:pos + every])
  if num > every:
    pos += every
    lsm = addLoadSubmenuItem(ll, num - pos)
    for i in range(cols):
      addPlaceSubmenu(self.tabs,lsm,places[pos:pos + every])
      pos += every
      if num > pos + 1:
        lsm = addLoadSubmenuItem(lsm, num - pos)
      elif num == pos:
        addPlaceSubmenu(self.tabs,lsm,places[-1:])

def addPlaceSubmenu(tabs,ll,places):
  digits = "123456789ABCDEFGHIJKL"
  for i in places:
    n = -1
    if places.index(i) < len(digits): n = places.index(i)
    item = i
    if n != -1: item = "_%s %s" % (digits[n],i)
    menu_items = gtk.MenuItem(item,True)
    ll.append(menu_items)
    menu_items.connect("activate",displayPlace,i,tabs)
    menu_items.show()

def addRelToBox(self,target,relid,fileid,tabs,scroll):
  global places
  cat = relid[1]
  relid = relid[0]
  if cat == 'p': global people
  if preRead(True,'l',[fileid,"relat"],2):
    name = []
    rels = {}
    nameperson = ""
    if not preRead(False,'l',[fileid,"relat",relid],3):
      if not preRead(False,'l',relid,1):
        pl = loadPlace(relid)
        inf = pl[0]
        try:
          inf.get("foo",None)
        except AttributeError:
          print "(l)addRelToBox: Load Error"
          return
        try:
          name = [inf['commonname'][0],inf["name"][0]]
        except KeyError as e:
          print "(l)addRelToBox: An error occurred accessing relation %s: %s" % (relid,e)
          return
      else:
        try:
          name = [people[relid]['info']['commonname'][0],people[relid]['info']['gname'][0],people[relid]['info']['fname'][0]]
        except KeyError as e:
          print "(l)addRelToBox: An error occurred accessing person %s: %s" % (relid,e)
          return
      if len(name[0]) > 2:
        nameperson = name[0]
      elif config['familyfirst']:
        nameperson = name[2] + " " + name[1]
      else:
        nameperson = name[1] + " " + name[2]
      places[fileid]['relat'][relid] = {}
      places[fileid]['relat'][relid]['file'] = [relid,True]
      places[fileid]['relat'][relid]['related'] = [nameperson,True]
      places[fileid]['relat'][relid]['relation'] = ["",False] # Add a dialog here
      places[fileid]['relat'][relid]['cat'] = [cat,True]
      places[fileid]['relat'][relid]['rtype'] = ["",False] # Perhaps all these things in one dialog
      places[fileid]['relat'][relid]['realm'] = ["",False] # Only write this one if user chooses a realm
      # Realm needs to be addressed in the DTD for XML files... not sure if it's hierarchically higher than relat or not, or if realm should just reference connections, rather than be part of their tree (people[fileid]['realm'][realm] = [list,of,relids])
      places[fileid]['relat'][relid]['events'] = {}
      places[fileid]['changed'] = True
      listRel(target,places[fileid]['relat'][relid],fileid,relid,scroll,tabs)
    else:
      bsay(self,"Not clobbering existing connection to %s!" % relid)
      return

def buildLocRow(scroll,data,fileid):
  row = gtk.HBox()
  row.show()
  label = gtk.Label("Location:")
  label.show()
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
    if choices.get(key) and choices[key][0] and choices[key][2]:
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

def connectToPlace(parent,target,tabs,scroll,fileid,title = ""):
  global status
  relid = recordSelectBox(None,fileid,title,['l','p']) # TODO: organizations?
  if relid and len(relid[1]):
    addRelToBox(parent,target,relid,fileid,tabs,scroll)
    status.push(0,"Added connection to %s on %s" % (relid[0],fileid))
  else:
    status.push(0,"Adding connection on %s cancelled" % fileid)

def displayPlace(callingWidget,fileid, tabrow):
  global places
  warnme = False
  if places.get(fileid,None):
    tab = places[fileid].get("tab")
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
    L = loadPlace(fileid)
    places[fileid] = {}
    places[fileid]['info'] = L[0]
    places[fileid]['relat'] = L[1]
    places[fileid]['changed'] = False
    places[fileid]['cat'] = 'l'
  displayStage1(tabrow,fileid,'l',saveThisL,showPlace,preClose,displayPlace)
  tabrow.vbox.connect("destroy",tabdestroyed,fileid)
  tabrow.labeli = gtk.Label("Information")
  tabrow.labelr = gtk.Label("Connections")
  tabrow.vbox.ftabs.infpage = displayStage2(tabrow.vbox.ftabs,tabrow.labeli)
  tabrow.vbox.ftabs.relpage = displayStage2(tabrow.vbox.ftabs,tabrow.labelr)
  if config['debug'] > 2: print "Loading " + tabrow.get_tab_label_text(tabrow.vbox)
  initLinfo(tabrow.vbox.ftabs.infpage, fileid)
  initLrels(tabrow.vbox.ftabs.relpage, fileid,tabrow)
  tabrow.set_current_page(tabrow.page_num(tabrow.vbox))
  places[fileid]["tab"] = tabrow.page_num(tabrow.vbox)

def getFileid(caller,tabs,one = "Please enter a new unique filing identifier.",two = "Fileid:",three = "This will be used to link records together and identify the record on menus. Valid characters are A-Z, 0-9, underscore, and dash. Do not include an extension, such as \".xml\".",four = "New place cancelled"):
  fileid = askBox(None,one,two,three)
  fileid = validateFileid(fileid)
  if fileid and len(fileid) > 0:
    mkPlace(caller,fileid,tabs)
  else:
    say(four)

def initLinfo(self, fileid):
  data = {}
  scroll = self.get_parent()
  try:
    data = places.get(fileid)
  except KeyError as e:
    print "initLinfo: An error occurred accessing %s: %s" % (fileid,e)
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
  if commonname.e.get_text() == "" and name.e.get_text() != "":
    commonname.e.set_text(name.e.get_text())
    commonname.e.emit("focus-out-event",gtk.gdk.Event(gtk.gdk.FOCUS_CHANGE))
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
  path2 = [fileid,"info"]
  path2.append(path[-1])
  placeCalendarButton(data,row,start,path2)
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
  path2 = [fileid,"info"]
  path2.append(path[-1])
  placeCalendarButton(data,row,end,path2)
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
      if dval: dval = dval[0]
      if cval: cval = cval[0]
      if dval and cval: addNote(self,scroll,notebox,fileid,dval,cval,i)

def initLrels(self, fileid,tabs):
  scroll = self.get_parent()
  global places
  global config
  name = []
  rels = {}
  nameplace = ""
  try:
    name = [places[fileid]['info']['commonname'][0],places[fileid]['info']['name'][0]]
  except KeyError as e:
    print "initLrels: An error occurred accessing %s: %s" % (fileid,e)
    if config['debug'] > 5: print str(places[fileid]['info'].get(e,None))
    return
  if places[fileid].get("relat"):
    rels = places[fileid]['relat']
  if len(name[0]) > 2:
    nameplace = name[0]
  else:
    nameplace = name[1]
  self.l1 = gtk.Label(nameplace + " - Place's Connections")
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
#    printPretty(rels,True)
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
    types = ["fam","empl","pat","place"]
    typedesc = ["Family","Employees","Patrons","Places"]
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
  self.add(uncatbox)
  self.addbutton.connect("clicked",connectToPlace,uncatbox,tabs,scroll,fileid,"Connect to " + nameplace)

def listRel(self,r,fileid,relid,scroll,target = None):
  if not r.get("related"): return
  name = r['related'][0]
  if not r.get("cat"): return
  cat = r['cat'][0]
  if not target: target = self.get_parent().get_parent().get_parent().get_parent() #Which is better?
  namebutton = gtk.Button(relid)
  namebutton.connect("clicked",displayPlace,relid,target) # passing the target or figuring it from parentage?
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
  activateRelEntry(nameentry,scroll,places.get(fileid),fileid,relid,"related")
  row1.pack_start(nameentry,1,1)
  relation = gtk.Label(r['relation'][0])
  relation.show()
  relation.set_width_chars(8)
  row1.pack_start(relation,1,1)
  relset = gtk.Button("Set")
  relset.show()
  relset.set_alignment(0.5,0.5)
  relset.set_size_request(36,24)
  data = places.get(relid,None)
  relset.connect("clicked",selectConnectionL,relation,fileid,relid,name,cat)
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
  mileadd.connect("clicked",addMilestone,scroll,row3,places.get(fileid),fileid,"relat",relid,boxwidth)
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
        data = places.get(fileid)
        activateRelEntry(d,scroll,data,fileid,relid,"date",i)
        rowmile.pack_start(d,1,1,2)
        datebut = gtk.Button()
        datebut.show()
        image = gtk.Image()
        image.set_from_file("img/date.png")
        datebut.set_image(image)
        datebut.unset_flags(gtk.CAN_FOCUS)
        datebut.connect("clicked",dateChoose,d,data,[fileid,'relat',relid,'events',i,'date'])
        rowmile.pack_start(datebut,0,0,2)
        e = gtk.Entry()
        e.show()
        e.set_width_chars(18)
        e.set_text(events['event'][0])
        activateRelEntry(e,scroll,data,fileid,relid,"event",i)
        rowmile.pack_start(e,1,1,2)
        row3.add(rowmile)

def mkPlace(callingWidget,fileid,tabs):
  global places
  if idExists(fileid,'l'):
    say("Existing fileid! Loading instead...")
  else:
    L = loadPlace(fileid)
    places[fileid] = {}
    places[fileid]['info'] = L[0]
    places[fileid]['relat'] = L[1]
    places[fileid]['changed'] = False
    places[fileid]['cat'] = 'l'
    saveThisL(callingWidget,fileid)
  displayPlace(callingWidget,fileid,tabs)

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
    print "Destroying tab %s" % fileid
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
    bsay(caller,"saveThisL: Could not find place %s." % fileid)

def selectConnectionL(caller,relation,fileid,relid,nameR,cat):
  global places
  nameL = ""
  try:
    name = [places[fileid]['info']['commonname'][0],places[fileid]['info']['name'][0]]
  except KeyError as e:
    print "selectConnectionL: An error occurred accessing %s: %s" % (fileid,e)
    return
  if len(name[0]) > 2:
    nameL = name[0]
  else:
    nameL = name[1]
  askbox = gtk.Dialog("Choose connection",None,gtk.DIALOG_DESTROY_WITH_PARENT,("Cancel",86))
  answers = {}
  options = getPlaceConnections(cat)
  for i in options.keys():
    answers[i] = options[i][0]
  optlist = []
  for key, value in sorted(answers.iteritems(), key=lambda (k,v): (v,k)):
    optlist.append(key)
  row = gtk.HBox()
  row.show()
  label = gtk.Label(nameL)
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
  if not preRead(True,'l',[fileid,'relat',relid],3): # This should have been here already.
    return
  if value == "86": return # Cancel
  places[fileid]['relat'][relid]['rtype'] = [options[value][2],True]
  places[fileid]['relat'][relid]['relation'] = [options[value][0],True]
  places[fileid]['relat'][relid]['cat'] = [cat,True]
  relation.set_text(places[fileid]['relat'][relid]['relation'][0])
  # TODO: some day, maybe edit and save the other record with reciprocal relational information.

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
    bsay(None,"setLoc: Could not set loc for %s." % fileid)

def setLocCombo(widget,fileid):
  setLoc(None,fileid,widget.get_active_text())

def showPlace(caller,fileid):
  if places.get(fileid):
    printPretty(places[fileid])

def tabdestroyed(caller,fileid):
  """Deletes the place's fileid key from places dict so the place can be reloaded."""
  global places
  try:
    del places[fileid]
  except KeyError:
    printPretty(places)
    raise

