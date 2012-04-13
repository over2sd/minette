
import pygtk
pygtk.require('2.0')
import gtk

import os

import backends
import city
import common
import getmod
from globdata import (config, menuBar,worldList)
import options
import person
import place
import state
from status import status


def addHelpMenu(self,target):
  itemH = gtk.MenuItem("_Help",True)
  itemH.show()
  target.append(itemH)
  h = gtk.Menu()
  h.show()
  itemH.set_submenu(h)
  itemHT = gtk.MenuItem("_Tutorial",True)
  h.append(itemHT)
  itemHT.show()
  itemHT.connect("activate",firstRunTab,self.tabs)
  itemHA = gtk.MenuItem("_About",True)
  h.append(itemHA)
  itemHA.show()
  itemHA.connect("activate",showHelp,self)

def clearMenus(caller = None):
  global menuBar
  if menuBar:
    for i in menuBar.get_children():
      text =  i.get_label()
      if text not in ["_Realm","_Tools"]:
        i.destroy()
        if config['debug'] > 0: print "%s destroyed." % text
    print "Menus destroyed!"

def doMenus(self):
  global menuBar
  person.addPersonMenu(self,menuBar)
  place.addPlaceMenu(self,menuBar)
  city.addCityMenu(self,menuBar)
  state.addStateMenu(self,menuBar)
  addHelpMenu(self,menuBar)

def firstRunTab(base,tabrow):
  tabrow.fr = gtk.VBox()
  tabrow.fr.show()
  tabrow.append_page(tabrow.fr,gtk.Label("Tutorial"))
# ..............................................................................................
  tut1 = "\n\tWelcome to Minette, an electronic writer's companion.\
\n\tThis world information manager (sometimes called a writer's bible) aims to help you keep track of all your continuity information (sometimes called a literary canon), so that your writing can be consistent throughout your short story, novel, or series of stories.\
\n\tThis tutorial will only display as long as you do not use a configuration file. Load with a configuration file as the first argument, create 'default.cfg' in the program's directory, or click the checkbox below to stop seeing this welcome tab.\
\n\tEditing the options for this program/realm will also create the configuration file and stop this tab from being shown. However, you can always bring this tab back by visiting the Help menu.\
\n\tMinette helps you do this by keeping track of discrete records in several categories: Person (for most of your characters, even those who aren't human), Landmark (for places, locations, or other szettings that aren't cities), City, and State (for nations, states, or other overarching regions).\
\n\tYou may want to begin by visiting the options menu (Realm>Options), where you can set several options for this program overall and for each realm individually. Options include whether given names follow family names or precede them, whether your characters have and use middle names, and what storage method you wish to use for your data.\
\n\tIf you don't create a new realm, you will be working in the default realm, in the default realm directory. This is fine if your stories all take place in the same 'universe', but you may wish to create different realms for different stories, to make finding a character from a particular story or sage much easier.\
\n\tTo begin storing information for your realm, use the menus to load an existing record or make a new record.\
\n\tNote: To set a Landmark's location, you must have created at least one City and one State record."
# ..............................................................................................
  tabrow.tut = gtk.TextView()
  tabrow.tut.set_editable(False)
  tabrow.tut.set_wrap_mode(gtk.WRAP_WORD)
  buff = tabrow.tut.get_buffer()
  buff.set_text(tut1)
  tabrow.tut.show()
  tabrow.tut.set_border_width(2)
  tabrow.tut.set_left_margin(7)
  tabrow.tut.set_right_margin(7)
  sw = gtk.ScrolledWindow()
  sw.set_policy(gtk.POLICY_NEVER,gtk.POLICY_AUTOMATIC)
  sw.show()
  sw.add(tabrow.tut)
  tabrow.fr.pack_start(sw,1,1,4)
  tabrow.close = gtk.Button("Close Tutorial")
  tabrow.close.show()
  tabrow.close.connect("clicked",common.kill,tabrow.fr)
  tabrow.toggle = gtk.CheckButton("Don't show again")
  tabrow.toggle.show()
  tabrow.toggle.connect("clicked",setTutorialSeen)
  tabrow.fr.pack_start(tabrow.toggle,0,0,2)
  tabrow.fr.pack_start(tabrow.close,0,0,2)

def loadRealm(self,fn):
  global config
  global worldList
  status.push(0,"Destroying menus...")
  clearMenus()
  status.push(0,"Clearing worldList...")
  worldList = {} # clear worldList
  status.push(0,"Reloading config...")
  backends.killRealmOpts()
  status.push(0,"Loading realm...")
  config.update(backends.loadRealm(fn))
  status.push(0,"Populating realm...")
  common.updateTitle()
  backends.populateWorld()
  status.push(0,"Building menus...")
  doMenus(self)
  pass

def loadRealmCst(parent,self):
  f = ""
  options = backends.listRealms()
  (e,f,g) = getmod.listSelectBox("?",options,"Choose a realm to load",allownew=True,newname="Realm")
  if f is None:
    print "cancel"
  elif f == "":
    newRealm(self)
  else:
    f = "realms/%s.rlm" % f
    loadRealm(self,f)

def loadRealmStd(self,fileid): # From a menu list
  f = validateFileid(fileid)
  fn = "realms/%s.rlm" % fn # even for SQL backend, I need the realm file to tell me how to access data
  loadRealm(self,f)

def newRealm(parent,self):
  common.getFileid(parent,self,mkRealm,"realm","Please enter a new unique filing identifier.","Realmid:","This short identifier will be used to identify the realm in selection dialogs and realm files. Valid characters are A-Z, 0-9, underscore, and dash. Do not include spaces, directories, or an extension, such as \".rlm\".")

def mkRealm(caller,fileid,self):
  global config
  realms = backends.listRealms()
  (e,f,g) = getmod.listSelectBox("?",realms,"Choose a realm to mimic")
  if f is None or f == "":
    print "cancel"
  else:
    print "Creating %s from %s"% (fileid,f)
    old = backends.loadRealm(f)
    config.update(old)
  config['realmname'] = "New Realm"
  config['realmdir'] = "realms/default/"
  config['realmfile'] = fileid
  backends.saveRealm(fileid)
  loadRealm(self,"realms/%s.rlm" % fileid)
  options.optionSetter(caller,self.window,False)
  print "newRealm called. Does nothing."
  pass

def saveRealm(fn):
  print "saveRealm called."
  backends.saveRealm(config['realmfile'])
  common.bsay("?","Done")

def setTutorialSeen(caller,event = None):
  global config
  config['seenfirstrun'] = caller.get_active()
  if config['debug'] > 6:
    print "%s %s" % (caller,caller.get_active())
    printPretty(config)
  backends.saveConfig(config.get("file","default.cfg"))

def showHelp(caller,parent):
  common.bsay(parent,"Icons provided by http://www.fatcow.com/free-icons")

