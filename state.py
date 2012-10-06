#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

import pygtk
pygtk.require('2.0')
import gtk
from math import floor


from backends import (loadState,idExists,saveState,pushLoc,getCitiesIn,getCityList)
from common import (addLoadSubmenuItem,displayStage1,displayStage2,askBox,\
validateFileid,buildarow,getInf,scrollOnTab,activateInfoEntry,placeCalendarButton,\
say,bsay,kill,markChanged, getFileid,addMilestone,buildaspectrow,setRuletext)
from debug import printPretty
from getmod import recordSelectBox
from globdata import (states,cities,worldList,config)
from city import (displayCity,saveThisC)
from status import status

def addStateMenu(self,target):
  itemS = gtk.MenuItem("_State",True)
  itemS.show()
  target.append(itemS)
  s = gtk.Menu()
  s.show()
  itemS.set_submenu(s)
  itemSN = gtk.MenuItem("_New",True)
  s.append(itemSN)
  itemSN.show()
  itemSN.connect("activate",getFileid,self.tabs,mkState,"state")
  itemSL = gtk.MenuItem("_Load",True)
  s.append(itemSL)
  itemSL.show()
  sl = gtk.Menu()
  sl.show()
  itemSL.set_submenu(sl)
  states = sorted(worldList['s'])
  num = len(states)
  every = num
  cols = 1
  if num > 20:
    cols = int(floor(num/20)) + 1
    every = int(num / cols) - 1
  pos = 0
  countitem = gtk.MenuItem("Total Entries: " + str(num))
  sl.append(countitem)
  countitem.show()
  addStateSubmenu(self.tabs,sl,states[pos:pos + every])
  if num > every:
    pos += every
    lsm = addLoadSubmenuItem(sl, num - pos)
    for i in range(cols):
      addStateSubmenu(self.tabs,lsm,states[pos:pos + every])
      pos += every
      if num > pos + 1:
        lsm = addLoadSubmenuItem(lsm, num - pos)
      elif num == pos:
        addStateSubmenu(self.tabs,lsm,states[-1:])

def addStateSubmenu(tabs,sl,states):
  digits = "123456789ABCDEFGHIJKL"
  for i in states:
    n = -1
    if states.index(i) < len(digits): n = states.index(i)
    item = i
    if n != -1: item = "_%s %s" % (digits[n],i)
    menu_items = gtk.MenuItem(item,True)
    sl.append(menu_items)
    menu_items.connect("activate",displayState,i,tabs)
    menu_items.show()

"""
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
  loc.connect("focus",scrollOnTab,scroll)
  loc.connect("focus-in-event",scrollOnTab,scroll)
  row.pack_start(loc,True,True,2)
  if len(g) and selected == -1:
    value = gtk.Label(" %s " % g)
    value.show()
    row.pack_start(value,True,True,2)
  return row
"""

def chooseCity(parent,target,tabs,scroll,data,statef,ar,stalts,title = ""):
  global status
  global cities
  city = recordSelectBox(None,statef,title,'c')
  if city and city[1] == "city":
    cityname = ""
    citlist = getCityList(0)
    cityf = validateFileid(citlist.get(statef,["",""])[1])
    cityname = citlist.get(statef,["",""])[0]
    statename = citlist.get(statef,["","",""])[2]
    try:
      cityname = cities[city[0]]['info']['name'][0]
      cities[city[0]]['info']['state'] = [statename,True]
      cities[city[0]]['info']['statefile'] = [statef,True]
      cities[city[0]]['info']['loc'] = [cityname,True]
      cities[city[0]]['info']['locfile'] = [cityf,True]
      cities[city[0]]['changed'] = True
      saveThisC(parent,city[0])
#      reloadPlaceTab(place[0]) # TODO: Write a function like this
    except KeyError:
#      placename = getPlaceNameFromID(place[0])
      cityname = askBox("?","  Please type the city name that goes with %s" % city[0],"Name",subtext="  I tried to load this from memory, but you\ndon't have %s open. Without it open, I can't\nsynchronize its city and state values.\n  This requirement prevents unintentional\nchanges to your place records." % city[0])
      # Maybe some day, I'll make this grab the placename from the file, and automatically load its record for updating
    if cityname == "":
      status.push(0,"Registering place in %s cancelled" % cityf)
      return False
    packCity(target,scroll,data,statef,city[0],cityname,tabs,True,ar,stalts)
    status.push(0,"Registered %s in %s" % (city[1],statef))
    return True
  else:
    status.push(0,"Registering place in %s cancelled" % statef)
    return False

def displayState(callingWidget,fileid, tabrow):
  global states
  stalts = []
  ar = gtk.Label()
  warnme = False
  if states.get(fileid,None):
    tab = states[fileid].get("tab")
    if tab is not None:
      warnme = True
      if not config['duplicatetabs']:
        status.push(0,"'" + fileid + "' is Already open. Switching to existing tab instead of loading...")
        tabrow.set_current_page(tab)
        for i in range(len(tabrow)):
          if fileid == tabrow.get_tab_label_text(tabrow.get_nth_page(i)):
            tabrow.set_current_page(i)
        return # No need to load again. If revert needed, use a different function
  else:
    states[fileid] = {}
    states[fileid]['info'] = loadState(fileid)
    states[fileid]['changed'] = False
    states[fileid]['cat'] = 's'
  displayStage1(tabrow,fileid,'s',saveThisS,showState,preClose,displayState,ar,stalts) # creates tabrow.vbox and tabrow.vbox.ftabs, et al
  tabrow.vbox.connect("destroy",tabdestroyed,fileid)
  tabrow.labeli = gtk.Label("Information")
  tabrow.vbox.ftabs.infpage = displayStage2(tabrow.vbox.ftabs,tabrow.labeli)
  tabrow.labelm = gtk.Label("Milestones")
  tabrow.vbox.ftabs.milepage = displayStage2(tabrow.vbox.ftabs,tabrow.labelm)
  if config['debug'] > 2: print "Loading " + tabrow.get_tab_label_text(tabrow.vbox)
  ar.show()
  ar.set_alignment(0.5,0.5)
  setRuletext(ar,len(stalts))
  tabrow.vbox.pack_end(ar,0,0,2)
  initSinfo(tabrow.vbox.ftabs.infpage, fileid,tabrow,ar,stalts)
  initSmile(tabrow.vbox.ftabs.milepage, fileid,tabrow,ar,stalts)
  tabrow.set_current_page(tabrow.page_num(tabrow.vbox))
  states[fileid]["tab"] = tabrow.page_num(tabrow.vbox)

def initSinfo(self, fileid,tabs,ar,stalts):
  global states
  data = {}
  scroll = self.get_parent()
  try:
    data = states.get(fileid)
  except KeyError as e:
    print "initSinfo: An error occurred accessing %s: %s" % (fileid,e)
    return
  label = gtk.Label("General")
  label.set_alignment(0,0)
  label.show()
  self.pack_start(label,0,0,1)
  self.s1 = gtk.HSeparator()
  self.pack_start(self.s1,False,False,2)
  self.s1.show()
  name = buildarow(scroll,"Name:",data,fileid,'name',ar,stalts)
  self.pack_start(name,0,0,2)
  row = gtk.HBox()
  row.show()
  path = ["info","start"]
  label = gtk.Label("Start Date:")
  label.show()
  row.pack_start(label,False,False,2)
  start = gtk.Entry(25)
  start.show()
  start.set_text(getInf(data,path))
  activateInfoEntry(start,ar,stalts,scroll,data,fileid,"start")
  row.pack_start(start,True,True,2)
  path2 = [fileid,"info"]
  path2.append(path[-1])
  placeCalendarButton(data,row,start,path2,stalts,counter=ar)
  label = gtk.Label("Cue:")
  label.show()
  row.pack_start(label,False,False,2)
  scue = gtk.Entry(25)
  scue.show()
  path[1] = "scue"
  scue.set_text(getInf(data,path))
  activateInfoEntry(scue,ar,stalts,scroll,data,fileid,"scue")
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
  activateInfoEntry(end,ar,stalts,scroll,data,fileid,"end")
  row.pack_start(end,True,True,2)
  path2 = [fileid,"info"]
  path2.append(path[-1])
  placeCalendarButton(data,row,end,path2,stalts,counter=ar)
  label = gtk.Label("Cue:")
  label.show()
  row.pack_start(label,False,False,2)
  ecue = gtk.Entry(25)
  ecue.show()
  path[1] = "ecue"
  ecue.set_text(getInf(data,path))
  activateInfoEntry(ecue,ar,stalts,scroll,data,fileid,"ecue")
  row.pack_start(ecue,True,True,2)
  self.pack_start(row,False,False,2)
  '''
	Vitals:
		State (i.e., empire, kingdom, republic, grand tribe)
		Adjective (Florida businesses)
		People (Floridians)
		Head of state (Governor)
		Capital (Tallahassee)
		Population
		Major resources
	Politics:
		Capital governance
		Foreign relations
		Organization (general)
	Culture
		Expected behaviors
		Rumors
	History
	Geography
	Economy
	Demographics
'''
  self.aspects = buildaspectrow(scroll,states.get(fileid),fileid,ar,stalts) # ,display = 0)
  self.add(self.aspects)
  self.notebox = gtk.VBox()
  self.notebox.show()
  self.pack_start(self.notebox,True,False,2)
  label = gtk.Label("Cities")
  label.set_alignment(0,0)
  label.show()
  self.notebox.pack_start(label,0,0,1)
  s1 = gtk.HSeparator()
  self.notebox.pack_start(s1,False,False,2)
  s1.show()
  box = gtk.HBox()
  box.show()
  addbut = gtk.Button("Register City")
  image = gtk.Image()
  image.set_from_file("img/add.png")
  image.show()
  addbut.set_image(image)
  addbut.show()
  path = ["info","cities"]
  statename = getInf(data,["info","name"],"")
  statecities = getInf(data,path,{})
  for c in statecities.keys():
    fi = c
    cityname = getInf(statecities,[fi,"name"],"")
    pushLoc(fileid,statename,fi,cityname)
  cbook = getCitiesIn(fileid)
  addbut.connect("clicked",chooseCity,self.notebox,tabs,scroll,data,fileid,ar,stalts,"Register in %s..." % statename)
  box.pack_end(addbut,False,False,1)
  self.notebox.pack_start(box,False,False,1)
  for c in sorted(cbook.keys()):
    if c != "_name":
      newcity = False
      cityname = cbook[c].get('_name',cbook.get(c,None))
      if c not in statecities.keys():
        newcity = True
        pushCity(fileid,c,cityname)
      if cityname is not None:
        packCity(self.notebox,scroll,data,fileid,c,cityname,tabs,newcity)
      else:
        common.say("Error getting cityname.")
  el = gtk.Label("End of record")
  el.show()
  el.set_alignment(1,1)
  self.pack_start(el,0,0,3)

def initSmile(self,fileid,tabs,ar,stalts):
  global states
  data = {}
  scroll = self.get_parent()
  try:
    data = states.get(fileid)
  except KeyError as e:
    print "initSmile: An error occurred accessing %s: %s" % (fileid,e)
    return
  row = gtk.HBox()
  row.show()
  self.pack_start(row,False,False,2)
  mileadd = gtk.Button("New Milestone")
  mileadd.show()
  mileadd.set_alignment(0.75,0.05)
  row.pack_start(mileadd,0,0,5)
  dhead = gtk.Label("Date")
  dhead.show()
  dhead.set_width_chars(8)
  row.pack_start(dhead,1,1,2)
  ehead = gtk.Label("Event")
  ehead.show()
  ehead.set_width_chars(18)
  row.pack_start(ehead,1,1,2)
  row.show_all()
  row2 = gtk.VBox()
  row2.show()
  self.pack_start(row2,1,1,2)
  boxwidth = self.size_request()[0]
  if not states[fileid]['info'].get("m"): states[fileid]['info']['m'] = {}
  r = states[fileid]['info'].get('m')
  if not states[fileid]['info']['m'].get("events"): states[fileid]['info']['m']['events'] = {}
  mileadd.connect("clicked",addMilestone,scroll,row2,states.get(fileid),fileid,"info","m",boxwidth)
  if r.get("events"):
    for i in sorted(r['events']):
#      showMile(row2,r,i,fileid,relid)

#def showMile(row2,r,i,fileid,relid):
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
        data = states.get(fileid)
        activateInfoEntry(d,ar,stalts,scroll,data,fileid,"m",3,["events",i,"date"])
        rowmile.pack_start(d,1,1,2)
        placeCalendarButton(data,rowmile,d,[fileid,"m","events",i,"date"],stalts,counter=ar)
        e = gtk.Entry()
        e.show()
        e.set_width_chars(18)
        e.set_text(events['event'][0])
        activateInfoEntry(e,scroll,data,fileid,"m",3,["events",i,"event"])
        rowmile.pack_start(e,1,1,2)
        row2.pack_start(rowmile,0,0,2)
  pass
# """
  el = gtk.Label("End of record")
  el.show()
  el.set_alignment(1,1)
  self.pack_start(el,0,0,3)

def mkState(callingWidget,fileid,tabs):
  global states
  if idExists(fileid,'s'):
    say("Existing fileid! Loading instead...")
  else:
    states[fileid] = {}
    states[fileid]['info'] = loadState(fileid)
    states[fileid]['changed'] = False
    states[fileid]['cat'] = 's'
    pushLoc(fileid)
    saveThisS(callingWidget,fileid)
  displayState(callingWidget,fileid,tabs)

def packCity(box,scroll,data,statef,cityf,value,tabs,newcity,ar,stalts):
  row = gtk.HBox()
  row.show()
  note = ""
  x = getInf(data,["info","cities"],{})
  if x.get(cityf) is not None: note = getInf(x,[cityf,"note"],"")
  cbut = gtk.Button(value)
  centry = gtk.Entry()
  cbut.show()
  centry.show()
  cbut.set_size_request(100,12)
  cbut.connect("clicked",displayCity,cityf,tabs)
  row.pack_start(cbut,1,1,2)
  label = gtk.Label("Note:")
  label.show()
  row.pack_start(label,0,0,2)
  row.pack_start(centry,1,1,2)
  centry.set_text(note)
  activateInfoEntry(centry,ar,stalts,scroll,data,statef,"cities",2,[cityf,"note"])
  if newcity: markChanged(centry,'s',[statef,"info","cities",cityf,"note"],stalts,ar)
  killbut = gtk.Button("Unregister")
  killbut.show()
  image = gtk.Image()
  image.show()
  image.set_from_file("img/subtract.png")
  killbut.set_image(image)
  killbut.connect("clicked",unlinkCity,row,statef,cityf)
  row.pack_start(killbut,0,0,1)
  box.pack_start(row,0,0,1)

def preClose(caller,fileid,target = None):
  result = -8
  if states.get(fileid):
    if states[fileid].get("changed"):
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

def pushCity(state,fi,name):
  global states
  if not states.get(state) or not states[state].get("info"):
    return False
  if not states[state]["info"].get("cities"):
    states[state]["info"]["cities"] = {}
  if not states[state]["info"]["cities"].get(fi):
    states[state]["info"]["cities"][fi] = {}
  states[state]["info"]["cities"][fi]["name"] = [name,True]
  return True

def saveThisS(caller,fileid):
  global status
  if states.get(fileid):
    pushLoc(fileid,states[fileid].get('name'))
    if saveState(fileid,states[fileid]):
      status.push(0,"%s saved successfully." % fileid)
    else:
      status.push(0,"Error encountered saving %s." % fileid)
  else:
    bsay(caller,"saveThisS: Could not find state %s." % fileid)

def showState(caller,fileid):
  if states.get(fileid):
    printPretty(states[fileid])

def tabdestroyed(caller,fileid):
  """Deletes the place's fileid key from places dict so the place can be reloaded."""
  global states
  try:
    del states[fileid]
  except KeyError:
    printPretty(states)
    raise

def unlinkCity(caller,row,statef,cityf):
  global states
  caller.set_sensitive(False)
  path = [statef,"info","cities",cityf]
  if states.get(path[0]) is not None and states[path[0]].get(path[1]) is not None and states[path[0]][path[1]].get(path[2]) is not None and states[path[0]][path[1]][path[2]].get(path[3]) is not None:
    del states[path[0]][path[1]][path[2]][path[3]]
    states[path[0]]["changed"] = True
  # TODO: Also unlink from place record, if it's loaded
  kill(caller,row)
