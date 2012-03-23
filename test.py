#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

import pygtk
pygtk.require('2.0')
import gtk
import sys

import backends
import globdata
from common import askBox

class Base:
  def __init__(self,configfile):
    self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    self.window.connect("delete_event", self.delete_event)
    self.window.connect("destroy", self.destroy)
    self.window.set_border_width(3)
    self.window.show()
    config = {'size':[200,200],'pos':[200,200]}
    if not config.get("nowindowstore"):
      self.window.set_geometry_hints(None,config['size'][0],config['size'][1])
      self.window.move(config['pos'][0],config['pos'][1])
    mainWin = self.window
    self.box1 = gtk.VBox()
    self.window.add(self.box1)
    self.box1.show()
    self.tabs = gtk.Notebook()
    self.tabs.set_scrollable(True)
    self.accgroup = gtk.AccelGroup() # for use on menus
    self.window.add_accel_group(self.accgroup)
    self.box1.add(self.tabs)
    self.tabs.show()
    self.box1.set_child_packing(self.tabs,1,1,0,gtk.PACK_START)
    button = gtk.Button("Test")
    label = gtk.Label("Button")
    button.show()
    label.show()
    self.tabs.append_page(button,label)
    button.connect("clicked",testThis,mainWin)

  def main(self):
    gtk.main()

  def delete_event(self,widget,event,data=None):
    #if config['debug'] > 3: print self.window.get_size()
    return False

  def destroy(self,widget,data=None):
    gtk.main_quit()

def testThis(self,window = None,b = 0,c = 0):
  x = askBox(window,"Test","Value")
  print x

if __name__ == "__main__":
  fn = None
  if len(sys.argv) > 1:
    print "%s" % sys.argv
    fn = sys.argv[1] # for now, config must be first argument
  base = Base(fn)
  base.main()
