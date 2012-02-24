#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

import pygtk
pygtk.require('2.0')
import gtk
from backends import (config,)
from choices import (stories,myStories,saveStories)
from common import (askBox,kill)
from status import status

def storyEditor(caller,parent):
  global stories
  myStories(config['worlddir'])
#  print "Story editor"
  ed = gtk.Window(gtk.WINDOW_TOPLEVEL)
  ed.show()
  ed.set_transient_for(parent)
  ed.set_destroy_with_parent(True)
  ed.set_border_width(5)
  ed.t = gtk.Table(3,1)
  ed.t.show()
  button = gtk.Button("Save List")
  button.show()
  button.set_size_request(50,24)
  button.connect("clicked",saveList,config['worlddir'])
  ed.t.attach(button,1,2,1,2)
  button = gtk.Button("Add Story")
  button.show()
  button.set_size_request(50,24)
  button.connect("clicked",addStoryRowNew,parent,ed,ed.t)
  ed.t.attach(button,2,3,1,2)
  button = gtk.Button("X")
  button.show()
  button.set_size_request(24,24)
  button.connect("clicked",kill,ed)
  ed.t.attach(button,3,4,1,2)
  ed.add(ed.t)
  i = 2
  for key in sorted(stories.keys()):
    addStoryRow(parent,ed,ed.t,key,stories[key],i)
    i += 1
  refreshEd(parent,ed)

def saveList(caller,wdir):
  saveStories(wdir)

def addStoryRow(parent,ed,t,key,value,i):
  if key and value and len(key) > 0 and len(value) > 0:
    label = gtk.Label(key)
    label.show()
    label.set_width_chars(4)
    t.attach(label,1,2,i,i + 1)
    entry = gtk.Entry()
    entry.set_width_chars(20)
    entry.set_text(value)
    entry.show()
    t.attach(entry,2,4,i,i + 1)
    entry.connect("focus-out-event",setStory,key)


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
    label.set_width_chars(4)
    t.attach(label,1,2,i,i + 1)
    entry = gtk.Entry()
    entry.show()
    entry.set_width_chars(20)
    t.attach(entry,2,4,i,i + 1)
    entry.grab_focus()
    entry.connect("focus-out-event",setStory,code)
  else:
    status.push(0,"Story add cancelled.")
    return False
  refreshEd(parent,ed)

def refreshEd(parent,ed):
  (x,y,w,h) = ed.t.get_allocation()
  ed.set_geometry_hints(None,w + 5,h + 5)
  (x,y) = parent.get_position()
  (w,h) = parent.get_size()
  x += int(w / 2)
  y += int(h / 2)
  (w,h) = ed.get_size()
  w = int(w/2)
  h = int(h/2)
  ed.move(x - w,y - h)

def setStory(widget,event,key):
  global stories
  if stories.get(key) != widget.get_text():
    stories[key] = widget.get_text()
    widget.modify_base(gtk.STATE_NORMAL,gtk.gdk.color_parse("#CCFFCC")) # change background for edited
