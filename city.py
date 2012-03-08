#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

import pygtk
pygtk.require('2.0')
import gtk
from math import floor


from backends import (loadCity,idExists,saveCity,getStateList,updateLocs,getPlacesIn,pushLoc)
from common import (addLoadSubmenuItem,displayStage1,displayStage2,askBox,\
validateFileid,buildarow,getInf,scrollOnTab,activateInfoEntry,placeCalendarButton,\
say,bsay,kill,markChanged)
from debug import printPretty
from globdata import (cities,worldList,config)
from place import displayPlace
from status import status

def addCityMenu(self):
  itemC = gtk.MenuItem("_City",True)
  itemC.show()
  self.mb.append(itemC)
  c = gtk.Menu()
  c.show()
  itemC.set_submenu(c)
  itemCN = gtk.MenuItem("_New",True)
  c.append(itemCN)
  itemCN.show()
  itemCN.connect("activate",getFileid,self.tabs)
  itemCL = gtk.MenuItem("_Load",True)
  c.append(itemCL)
  itemCL.show()
  cl = gtk.Menu()
  cl.show()
  itemCL.set_submenu(cl)
  cities = sorted(worldList['c'])
  num = len(cities)
  every = num
  cols = 1
  if num > 20:
    cols = int(floor(num/20)) + 1
    every = int(num / cols) - 1
  pos = 0
  countitem = gtk.MenuItem("Total Entries: " + str(num))
  cl.append(countitem)
  countitem.show()
  addCitySubmenu(self.tabs,cl,cities[pos:pos + every])
  if num > every:
    pos += every
    lsm = addLoadSubmenuItem(cl, num - pos)
    for i in range(cols):
      addCitySubmenu(self.tabs,lsm,cities[pos:pos + every])
      pos += every
      if num > pos + 1:
        lsm = addLoadSubmenuItem(lsm, num - pos)
      elif num == pos:
        addCitySubmenu(self.tabs,lsm,cities[-1:])

def addCitySubmenu(tabs,cl,cities):
  digits = "123456789ABCDEFGHIJKL"
  for i in cities:
    n = -1
    if cities.index(i) < len(digits): n = cities.index(i)
    item = i
    if n != -1: item = "_%s %s" % (digits[n],i)
    menu_items = gtk.MenuItem(item,True)
    cl.append(menu_items)
    menu_items.connect("activate",displayCity,i,tabs)
    menu_items.show()

def buildStateRow(scroll,data,fileid):
  row = gtk.HBox()
  row.show()
  label = gtk.Label("State:")
  label.show()
  row.pack_start(label,False,False,2)
  label.set_width_chars(20)
  label.set_alignment(1,0.5)
  choices = getStateList()
  path = ["info","state"]
  g = getInf(data,path)
#  loc = gtk.ComboBoxText()
  loc = gtk.combo_box_new_text()
  loc.show()
  selected = -1
  keys = []
  i = 0
  for key in sorted(choices.keys()):
    loc.append_text("%s" % choices[key])
    keys.append(key)
    if g == key or g == choices[key]:
      selected = i
    i += 1
  loc.set_active(selected)
  loc.connect("changed",setStateCombo,fileid)
  loc.connect("move-active",setStateCombo,fileid)
  loc.connect("focus",scrollOnTab,scroll)
  loc.connect("focus-in-event",scrollOnTab,scroll)
  row.pack_start(loc,True,True,2)
  if len(g) and selected == -1:
    value = gtk.Label(" %s " % g)
    value.show()
    row.pack_start(value,True,True,2)
  return row

def choosePlace():
  pass

def displayCity(callingWidget,fileid, tabrow):
  global cities
  warnme = False
  if cities.get(fileid,None):
    tab = cities[fileid].get("tab")
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
    cities[fileid] = {}
    cities[fileid]['info'] = loadCity(fileid)
    cities[fileid]['changed'] = False
    cities[fileid]['cat'] = 'c'
  displayStage1(tabrow,fileid,'c',saveThisC,showCity,preClose) # creates tabrow.vbox and tabrow.vbox.ftabs, et al
  tabrow.vbox.connect("destroy",tabdestroyed,fileid)
  tabrow.labeli = gtk.Label("Information")
  tabrow.vbox.ftabs.infpage = displayStage2(tabrow.vbox.ftabs,tabrow.labeli)
  if config['debug'] > 2: print "Loading " + tabrow.get_tab_label_text(tabrow.vbox)
  initCinfo(tabrow.vbox.ftabs.infpage, fileid,tabrow)
  tabrow.set_current_page(tabrow.page_num(tabrow.vbox))
  cities[fileid]["tab"] = tabrow.page_num(tabrow.vbox)

def getFileid(caller,tabs,one = "Please enter a new unique filing identifier.",two = "Fileid:",three = "This will be used to link records together and identify the record on menus. Valid characters are A-Z, 0-9, underscore, and dash. Do not include an extension, such as \".xml\".",four = "New city cancelled"):
  fileid = askBox(None,one,two,three)
  fileid = validateFileid(fileid)
  if fileid and len(fileid) > 0:
    mkCity(caller,fileid,tabs)
  else:
    say(four)

def initCinfo(self, fileid,tabs):
  data = {}
  scroll = self.get_parent()
  try:
    data = cities.get(fileid)
  except KeyError as e:
    print "initCinfo: An error occurred accessing %s: %s" % (fileid,e)
    return
  scroll = self.get_parent()
  label = gtk.Label("City:")
  label.set_alignment(0,0)
  label.show()
  self.pack_start(label,0,0,1)
  self.s1 = gtk.HSeparator()
  self.pack_start(self.s1,False,False,2)
  self.s1.show()
  name = buildarow(scroll,"Name:",data,fileid,'name')
  self.pack_start(name,0,0,2)
  state = buildStateRow(scroll,data,fileid)
  self.pack_start(state,0,0,2)
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
  self.notebox = gtk.VBox()
  self.notebox.show()
  self.pack_start(self.notebox,True,False,2)
  label = gtk.Label("Places")
  label.set_alignment(0,0)
  label.show()
  self.notebox.pack_start(label,0,0,1)
  s1 = gtk.HSeparator()
  self.notebox.pack_start(s1,False,False,2)
  s1.show()
  box = gtk.HBox()
  box.show()
  addbut = gtk.Button("Register Place")
  image = gtk.Image()
  image.set_from_file("img/add.png")
  image.show()
  addbut.set_image(image)
  addbut.show()
  path = ["info","places"]
  state = validateFileid(getInf(data,["info","statefile"],""))
  cityname = getInf(data,["info","name"],"")
  cityplaces = getInf(data,path,{})
  for l in cityplaces.keys():
    fi = l
    name = getInf(cityplaces,[l,"name"],"")
    pushLoc(state,"",fileid,cityname,fi,name)
  lbook = getPlacesIn(fileid)
  addbut.connect("clicked",choosePlace,self.notebox,lbook)
  box.pack_end(addbut,False,False,1)
  self.notebox.pack_start(box,False,False,1)
  for l in lbook.keys():
    if l != "_name":
      newplace = False
      if l not in cityplaces.keys():
        newplace = True
        pushPlace(fileid,l,lbook[l])
      packPlace(self.notebox,scroll,data,fileid,l,lbook[l],tabs,newplace)

def mkCity(callingWidget,fileid,tabs):
  global cities
  if idExists(fileid,'c'):
    say("Existing fileid! Loading instead...")
  else:
    cities[fileid] = {}
    cities[fileid]['info'] = loadCity(fileid)
    cities[fileid]['changed'] = False
    cities[fileid]['cat'] = 'c'
    saveThisC(callingWidget,fileid)
  displayCity(callingWidget,fileid,tabs)

def packPlace(box,scroll,data,cityf,placef,value,tabs,newplace):
  row = gtk.HBox()
  row.show()
  note = ""
  x = getInf(data,["info","places"],{})
  if x.get(placef) is not None: note = getInf(x,[placef,"note"],"")
  plbut = gtk.Button(value)
  plentry = gtk.Entry()
  plbut.show()
  plentry.show()
  plbut.set_size_request(100,12)
  plbut.connect("clicked",displayPlace,placef,tabs)
  row.pack_start(plbut,1,1,2)
  label = gtk.Label("Note:")
  label.show()
  row.pack_start(label,0,0,2)
  row.pack_start(plentry,1,1,2)
  plentry.set_text(note)
  activateInfoEntry(plentry,scroll,data,cityf,"places",2,[placef,"note"])
  if newplace: markChanged(plentry,'c',[cityf,"info","places",placef,"note"])
  killbut = gtk.Button("Unregister")
  killbut.show()
  image = gtk.Image()
  image.show()
  image.set_from_file("img/subtract.png")
  killbut.set_image(image)
  killbut.connect("clicked",unlinkPlace,row,cityf,placef)
  row.pack_start(killbut,0,0,1)
  box.pack_start(row,0,0,1)

def preClose(caller,fileid,target = None):
  result = -8
  if cities.get(fileid):
    if cities[fileid].get("changed"):
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

def pushPlace(city,fi,name):
  global cities
  if not cities.get(city) or not cities[city].get("info"):
    return False
  if not cities[city]["info"].get("places"):
    cities[city]["info"]["places"] = {}
  if not cities[city]["info"]["places"].get(fi):
    cities[city]["info"]["places"][fi] = {}
  cities[city]["info"]["places"][fi]["name"] = [name,True]
  return True

def saveThisC(caller,fileid):
  global status
  if cities.get(fileid):
    if saveCity(fileid,cities[fileid]):
      status.push(0,"%s saved successfully." % fileid)
    else:
      status.push(0,"Error encountered saving %s." % fileid)
  else:
    bsay(caller,"saveThisC: Could not find city %s." % fileid)

def setState(caller,fileid,key):
  global cities
  statekeys = {}
  if len(key) > 1:
    statekeys = getStateList(1)
    key = statekeys.get(key,'N')
    statekeys = getStateList()
    if config['debug'] > 3: print "new key: %s" % key
    print "%s (%s)" % (statekeys[key],key)
    if preReadc(False,[fileid,"info"],2):
      cities[fileid]['info']['statefile'] = [key,True]
      cities[fileid]['info']['state'] = [lockeys[key],True]
      cities[fileid]['changed'] = True
      if config['debug'] > 0: print "New State: %s" % key
      cityname = cities[fileid]['info'].get("name",None)
      if cityname: updateLocs(cityname,fileid,key)
  else:
    bsay(None,"setState: Could not set state for %s." % fileid)

def setStateCombo(widget,fileid):
  setState(None,fileid,widget.get_active_text())

def showCity(caller,fileid):
  if cities.get(fileid):
    printPretty(cities[fileid])

def tabdestroyed(caller,fileid):
  """Deletes the place's fileid key from places dict so the place can be reloaded."""
  global cities
  try:
    del cities[fileid]
  except KeyError:
    printPretty(cities)
    raise

def unlinkPlace(caller,row,cityf,placef):
  global cities
  caller.set_sensitive(False)
  path = [cityf,"info","places",placef]
  if cities.get(path[0]) is not None and cities[path[0]].get(path[1]) is not None and cities[path[0]][path[1]].get(path[2]) is not None and cities[path[0]][path[1]][path[2]].get(path[3]) is not None:
    del cities[path[0]][path[1]][path[2]][path[3]]
    cities[path[0]]["changed"] = True
  kill(caller,row)
