#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

import pygtk
pygtk.require('2.0')
import gtk

from os import path
import backends
import common
from globdata import (config,mainWin,menuBar,version)
import menu
from options import optionSetter
from status import status
from story import storyEditor
from getmod import recordSelectBox
import sys

class Base:
  def __init__(self,configfile):
    global status
    global config
    global mainWin
    global menuBar
    self.window = mainWin
    common.updateTitle()
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
    if not config.get("seenfirstrun"): menu.firstRunTab(self,self.tabs)
    self.accgroup = gtk.AccelGroup() # for use on menus
    self.window.add_accel_group(self.accgroup)
    Base.makeMenus(self)
    self.box1.add(menuBar)
    self.box1.add(self.tabs)
    self.tabs.show()
#    self.menu1.connect("clicked", self.hello, None)
#    self.menu1.connect_object("clicked", gtk.Widget.destroy, self.window)
    status.set_border_width(2)
    status.show()
    self.box1.add(status)
    self.box1.set_child_packing(status,0,0,0,gtk.PACK_START)
    self.box1.set_child_packing(self.tabs,1,1,0,gtk.PACK_START)
    self.box1.set_child_packing(menuBar,0,0,0,gtk.PACK_START)
#    self.button1.set_border_width(2)
    menuBar.show()

  def main(self):
    status.push(0,"Load a record from the menus to begin.")
    if config['startnewperson']: getFileid(self,self.tabs)
    gtk.main()

  def makeMenus(self):
    global menuBar
# Realm
    itemR = gtk.MenuItem("_Realm",True)
    itemR.show()
    menuBar.append(itemR)
    r = gtk.Menu()
    r.set_accel_group(self.accgroup)
    r.show()
    itemR.set_submenu(r)

    itemRN = gtk.MenuItem("_New",True)
    itemRN.show()
    k,m = gtk.accelerator_parse("<Control>N")
    itemRN.add_accelerator("activate",self.accgroup,k,m,gtk.ACCEL_VISIBLE)
    r.append(itemRN)
    itemRN.connect("activate",menu.newRealm,self)
    itemRL = gtk.MenuItem("_Load",True)
    itemRL.show()
    k,m = gtk.accelerator_parse("<Control>L")
    itemRL.add_accelerator("activate",self.accgroup,k,m,gtk.ACCEL_VISIBLE)
    r.append(itemRL)
    itemRL.connect("activate",menu.loadRealmCst,self)
    itemRS = gtk.MenuItem("_Save",True)
    itemRS.show()
    k,m = gtk.accelerator_parse("<Control>S")
    itemRS.add_accelerator("activate",self.accgroup,k,m,gtk.ACCEL_VISIBLE)
    r.append(itemRS)
    itemRS.connect("activate",menu.saveRealm)
    if config['debug'] > 0:
      itemRP = gtk.MenuItem("Show _PlaceList",True)
      itemRP.show()
      r.append(itemRP)
      itemRP.connect("activate",backends.getPlaceListGTK)
      itemRR = gtk.MenuItem("List _Records",True)
      itemRR.show()
      r.append(itemRR)
      itemRR.connect("activate",backends.listThingsGTK)
      """
      itemRM = gtk.MenuItem("Clear _Menus",True)
      itemRM.show()
      r.append(itemRM)
      itemRM.connect("activate",menu.clearMenus)
      """
    itemRO = gtk.MenuItem("_Options",True)
    itemRO.show()
    r.append(itemRO)
    itemRO.connect("activate",optionSetter,self.window)
    itemRT = gtk.MenuItem("S_tory Editor",True)
    itemRT.show()
    r.append(itemRT)
    itemRT.connect("activate",storyEditor,self.window)
    if config['uselistfile']:
      itemRC = gtk.MenuItem("_Clear list file",True)
      r.append(itemRC)
      itemRC.show()
      itemRC.connect("activate",backends.killListFile)
    itemRQ = gtk.MenuItem("_Quit",True)
    itemRQ.show()
    k,m = gtk.accelerator_parse("<Control>Q")
    itemRQ.add_accelerator("activate",self.accgroup,k,m,gtk.ACCEL_VISIBLE)
    r.append(itemRQ)
    itemRQ.connect("activate", backends.storeWindowExit,self.window)
# Person
#    if config['realmloaded']:
    menu.doMenus(self)

  def delete_event(self,widget,event,data=None):
    if config['debug'] > 3: print self.window.get_size()
#    print "delete event occurred"
    return False

  def destroy(self,widget,data=None):
    gtk.main_quit()

if __name__ == "__main__":
  print "Minette v%s loading..." % version
  fn = None
  if len(sys.argv) > 1:
    print "%s" % sys.argv
    fn = sys.argv[1] # for now, config must be first argument
  if fn is None:
    fn = "default.cfg" # using 3-letter extension for MSWin compatibility, I hope.
  backends.loadConfig(fn)
  backends.populateWorld()
  fn = path.join(config['realmdir'],"myrealm.cfg")
  if config['uselistfile'] and not path.exists(fn):
    print " writing list file so you won't have to walk the directory again..."
    backends.writeListFile()
  base = Base(fn)
  base.main()
