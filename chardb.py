#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

import pygtk
pygtk.require('2.0')
import gtk

from os import path
from backends import (config,worldList,loadConfig,populateWorld)
from person import (displayPerson, addPersonMenu)
from status import status
import sys

class Base:
  def __init__(self,configfile):
    global status
    self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    self.window.connect("delete_event", self.delete_event)
    self.window.connect("destroy", self.destroy)
    self.window.set_border_width(3)
    self.window.set_geometry_hints(None,620,440)
    self.window.show()
    self.box1 = gtk.VBox()
    self.window.add(self.box1)
    self.box1.show()
    self.tabs = gtk.Notebook()
    self.tabs.set_scrollable(True)
    if not path.exists(path.abspath(fn)): Base.firstRunTab(self,self.tabs)
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

#    displayPerson("?","petekend",self.tabs)
#    displayPerson("?","kanemela",self.tabs)
#    displayPerson("?","mortgera",self.tabs)

    gtk.main()

  def firstRunTab(base,tabrow):
    tabrow.fr = gtk.VBox()
    tabrow.fr.show()
    tabrow.append_page(tabrow.fr,gtk.Label("First Run Tutorial"))
    tabrow.tut = gtk.TextBuffer()
    tabrow.tutv = gtk.TextView(tabrow.tut)
    tabrow.tutv.set_border_width(1)
    tabrow.tutv.set_left_margin(5)
    tabrow.tutv.set_right_margin(5)
    tabrow.tutv.show()
    tabrow.tutv.set_wrap_mode(gtk.WRAP_WORD)
    tabrow.tutv.modify_base(gtk.STATE_NORMAL,gtk.gdk.color_parse("#D4D4D4"))
    tabrow.tutv.set_editable(False)
    tabrow.tut.set_text("\n\t\
This tutorial will only display as long as you do not use a configuration \
file. Load with a configuration file as the first argument, or create \
'default.cfg' in the program's directory to stop seeing this welcome tab.\
\n\tTo begin, Use the Person menu to load an existing record or make a new\
 record.")
    tabrow.fr.add(tabrow.tutv)


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
    if config['debug'] > 0: print self.window.get_size()
#    print "delete event occurred"
    return False

  def destroy(self,widget,data=None):
    gtk.main_quit()

if __name__ == "__main__":
  fn = None
  if len(sys.argv) > 1:
    fn = sys.argv[1] # for now, config must be first argument
  if fn is None:
    fn = "default.cfg" # using 3-letter extension for MSWin compatibility, I hope.
  loadConfig(fn)
  populateWorld()
  base = Base(fn)
  base.main()
