#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

import pygtk
pygtk.require('2.0')
import gtk
from backends import (config,)
from choices import (stories,myStories,saveStories)
from common import askBox
from status import status

def storyEditor(caller,parent):
  ed = gtk.Window(gtk.WINDOW_TOPLEVEL)
  ed.show()
  ed.set_transient_for(parent)
  ed.set_destroy_with_parent(True)
  ed.set_border_width(5)
  t = gtk.Table(3,1)
  t.show()
  ed.add(t)
  button = gtk.Button("Add New Story")
  button.show()
  t.attach(button,3,4,1,2)
  t.resize(3,len(stories) + 2)
  button.connect("clicked",addStoryRowNew,parent,ed,t)
  for key in sorted(stories.keys()):
    addStoryRow(parent,ed,t,key,stories[key])

def addStoryRow(parent,ed,t,key,value):
  i = len(stories) + 2
  if key and value and len(key) > 0 and len(value) > 0:
    label = gtk.Label(key)
    label.show()
    t.attach(label,1,2,i,i + 1)
    entry = gtk.Entry()
    entry.set_text(value)
    entry.show()
    t.attach(entry,2,4,i,i + 1)
    entry.connect("focus-out-event",setStory,code,entry)


def addStoryRowNew(caller,parent,ed,t):
  i = len(stories) + 2
  text = "Please enter the short code for this story"
  label = "Code:"
  subtext = "\
This will be what is displayed\n\
in your backend files. Once set,\n\
it cannot be changed within this\n\
program."
  code = askBox(ed,text,label,subtext)
  if code and len(code) > 0:
    label = gtk.Label(code)
    label.show()
    t.attach(label,1,2,i,i + 1)
    entry = gtk.Entry()
    entry.show()
    t.attach(entry,2,4,i,i + 1)
    entry.connect("focus-out-event",code,entry)
  else:
    status.push(0,"Story add cancelled.")
    return False
  (x,y) = parent.get_position()
  (w,h) = parent.get_size()
  x += int(w / 2)
  y += int(h / 2)
  (w,h) = ed.get_size()
  w = int(w/2)
  h = int(h/2)
  ed.move(x - w,y - h)

def setStory(caller,key,widget):
  print "%s %s %s" % (caller,key,widget)
