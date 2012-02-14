#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

import pygtk
pygtk.require('2.0')
import gtk

from chardb_backends import (config,loadConfig)
from person import displayPerson
from status import status

class Base:
  def __init__(self):
    global status
    self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    self.window.connect("delete_event", self.delete_event)
    self.window.connect("destroy", self.destroy)
    self.window.set_border_width(10)
    self.window.show()
    self.box1 = gtk.VBox()
    self.window.add(self.box1)
    self.box1.show()
    self.tabs = gtk.Notebook()
    self.box1.add(self.tabs)
    self.tabs.show()
    self.button1 = gtk.Button("Quit")
    self.button1.connect("clicked", self.hello, None)
    self.button1.connect_object("clicked", gtk.Widget.destroy, self.window)
    self.box1.add(self.button1)
    self.button1.set_border_width(2)
    self.button1.show()
    status.set_has_resize_grip(True)
    status.set_border_width(2)
    self.box1.add(status)
    status.show()

  def main(self):
    displayPerson("chamjack",self.tabs)
    displayPerson("chamiren",self.tabs)
    gtk.main()

  def hello(self,widget,data=None):
    print "Goodbye World"

  def delete_event(self,widget,event,data=None):
    print "delete event occurred"
    return False

  def destroy(self,widget,data=None):
    gtk.main_quit()

print __name__
if __name__ == "__main__":
  fn = None # TODO: take config file argument
  loadConfig(fn)
  base = Base()
  base.main()
