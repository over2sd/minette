#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

import pygtk
pygtk.require('2.0')
import gtk

from os import path
from backends import (worldList,loadConfig,populateWorld,storeWindowExit,killListFile,\
writeListFile,getPlaceListGTK)
from city import addCityMenu
from common import addHelpMenu
from globdata import (config,mainWin)
from person import addPersonMenu
from place import addPlaceMenu
from state import addStateMenu
from status import status
from story import storyEditor
from getmod import recordSelectBox
import sys

class Base:
  def __init__(self,configfile):
    global status
    global config
    global mainWin
    self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    self.window.connect("delete_event", self.delete_event)
    self.window.connect("destroy", self.destroy)
    self.window.set_border_width(3)
    self.window.show()
    if not config.get("nowindowstore"):
      self.window.set_geometry_hints(None,config['size'][0],config['size'][1])
      self.window.move(config['pos'][0],config['pos'][1])
    mainWin = self.window
    self.box1 = gtk.VBox()
    self.window.add(self.box1)
    self.box1.show()
    self.tabs = gtk.Notebook()
    self.tabs.set_scrollable(True)
    if not path.exists(path.abspath(fn)): Base.firstRunTab(self,self.tabs)
    self.accgroup = gtk.AccelGroup() # for use on menus
    self.window.add_accel_group(self.accgroup)
    Base.makeMenus(self)
    self.box1.add(self.mb)
    self.box1.add(self.tabs)
    self.tabs.show()
#    self.menu1.connect("clicked", self.hello, None)
#    self.menu1.connect_object("clicked", gtk.Widget.destroy, self.window)
    status.set_border_width(2)
    status.show()
    self.box1.add(status)
    self.box1.set_child_packing(status,0,0,0,gtk.PACK_START)
    self.box1.set_child_packing(self.tabs,1,1,0,gtk.PACK_START)
    self.box1.set_child_packing(self.mb,0,0,0,gtk.PACK_START)
#    self.button1.set_border_width(2)
    self.mb.show()


  def main(self):
    status.push(0,"Load a record from the menus to begin.")
    if config['startnew']: getFileid(self,self.tabs)
    gtk.main()

  def firstRunTab(base,tabrow):
    tabrow.fr = gtk.VBox()
    tabrow.fr.show()
    tabrow.append_page(tabrow.fr,gtk.Label("First Run Tutorial"))
# ..............................................................................................
    tut1 = "\n\t\
This tutorial will only display as long as you do not use a configuration file. Load with a\
\nconfiguration file as the first argument, or create 'default.cfg' in the program's directory\
\nto stop seeing this welcome tab.\
\n\tTo begin, Use the Person menu to load an existing record or make a new record."
# ..............................................................................................
    tabrow.tut = gtk.Label(tut1)
    tabrow.tut.show()
    tabrow.fr.add(tabrow.tut)


  def makeMenus(self):
    self.mb = gtk.MenuBar()
    self.mb.show()
# File
    itemW = gtk.MenuItem("_World",True)
    itemW.show()
    self.mb.append(itemW)
    w = gtk.Menu()
    w.set_accel_group(self.accgroup)
    w.show()
    itemW.set_submenu(w)
    if config['debug'] > 0:
      itemWS = gtk.MenuItem("_Show placeList",True)
      itemWS.show()
      w.append(itemWS)
      itemWS.connect("activate",getPlaceListGTK)
    itemWT = gtk.MenuItem("S_tory Editor",True)
    itemWT.show()
    w.append(itemWT)
    itemWT.connect("activate",storyEditor,self.window)
    if config['uselistfile']:
      itemWC = gtk.MenuItem("_Clear list file",True)
      w.append(itemWC)
      itemWC.show()
      itemWC.connect("activate",killListFile)
    itemWQ = gtk.MenuItem("_Quit",True)
    itemWQ.show()
    k,m = gtk.accelerator_parse("<Control>Q")
    itemWQ.add_accelerator("activate",self.accgroup,k,m,gtk.ACCEL_VISIBLE)
    w.append(itemWQ)
    itemWQ.connect("activate", storeWindowExit,self.window)
# Person
    addPersonMenu(self)
    addPlaceMenu(self)
    addCityMenu(self)
    addStateMenu(self)
    addHelpMenu(self)

  def delete_event(self,widget,event,data=None):
    if config['debug'] > 3: print self.window.get_size()
#    print "delete event occurred"
    return False

  def destroy(self,widget,data=None):
    gtk.main_quit()

if __name__ == "__main__":
  fn = None
  if len(sys.argv) > 1:
    print "%s" % sys.argv
    fn = sys.argv[1] # for now, config must be first argument
  if fn is None:
    fn = "default.cfg" # using 3-letter extension for MSWin compatibility, I hope.
  loadConfig(fn)
  populateWorld()
  fn = path.join(config['worlddir'],"myworld.cfg")
  if config['uselistfile'] and not path.exists(fn):
    print " writing list file so you won't have to walk the directory again..."
    writeListFile()
  base = Base(fn)
  base.main()
