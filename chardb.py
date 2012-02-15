#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

import pygtk
pygtk.require('2.0')
import gtk

from chardb_backends import (config,worldList,loadConfig,populateWorld)
from person import (displayPerson, addPersonMenu)
from status import status

class Base:
  def __init__(self):
    global status
    self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    self.window.connect("delete_event", self.delete_event)
    self.window.connect("destroy", self.destroy)
    self.window.set_border_width(3)
    self.window.set_geometry_hints(None,790,440)
    self.window.show()
    self.box1 = gtk.VBox()
    self.window.add(self.box1)
    self.box1.show()
    self.tabs = gtk.Notebook()
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
    displayPerson("?","petekend",self.tabs)
#    displayPerson("?","kanemela",self.tabs)
#    displayPerson("?","mortgera",self.tabs)

    gtk.main()

  def makeMenus(self):
    self.mb = gtk.MenuBar()
    self.mb.show()
# File
    itemF = gtk.MenuItem("_File",True)
    itemF.show()
    self.mb.append(itemF)
    f = gtk.Menu()
    f.show()
    itemF.set_submenu(f)
    itemFQ = gtk.MenuItem("_Quit",True)
    itemFQ.show()
    f.append(itemFQ)
    itemFQ.connect("activate", gtk.main_quit)
# Person
    addPersonMenu(self)

  def delete_event(self,widget,event,data=None):
#    print self.window.get_size()
    print "delete event occurred"
    return False

  def destroy(self,widget,data=None):
    gtk.main_quit()

if __name__ == "__main__":
  fn = None # TODO: take config file argument
  loadConfig(fn)
  populateWorld()
  base = Base()
  base.main()
