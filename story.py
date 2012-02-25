#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

import pygtk
pygtk.require('2.0')
import gtk
from backends import (config,)
from choices import (stories,myStories,saveStories)
from common import (askBox,kill,csplit,validateFileid)
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
  ed.vbox = gtk.VBox()
  ed.vbox.show()
  ed.add(ed.vbox)
  bar = gtk.HBox()
  bar.show()
  button = gtk.Button("Save List")
  button.show()
  button.connect("clicked",saveList,config['worlddir'])
  bar.pack_start(button,False,False,2)
  button = gtk.Button("Add Story")
  button.show()
  button.connect("clicked",addStoryRowNew,parent,ed,ed.vbox)
  bar.pack_start(button,True,True,2)
  button = gtk.Button("Close Editor")
  button.show()
  button.connect("clicked",kill,ed)
  bar.pack_start(button,False,False,2)
  ed.vbox.pack_start(bar,False,False,1)
  for key in sorted(stories.keys()):
    addStoryRow(parent,ed,ed.vbox,key,stories[key])
  refreshEd(parent,ed)

def saveList(caller,wdir):
  saveStories(wdir)

def addStoryRow(parent,ed,target,key,value):
  if key and value and len(key) > 0 and len(value) > 0:
    row = gtk.HBox()
    row.show()
    label = gtk.Label(key)
    label.show()
    label.set_width_chars(4)
    row.pack_start(label,False,False,2)
    entry = gtk.Entry()
    entry.set_width_chars(20)
    entry.set_text(value)
    entry.show()
    row.pack_start(entry,True,True,2)
    entry.connect("focus-out-event",setStory,key)
    target.pack_start(row,False,False,2)


def addStoryRowNew(caller,parent,ed,target):
  row = gtk.HBox()
  row.show()
  text = "Please enter the short code for this story"
  label = "Code:"
  subtext = "\
This will be what is displayed in your\n\
backend files. Once set, it cannot be\n\
changed within this program.  It may\n\
only contain spaces and word characters\n\
(A-Z,0-9,_,-)."
  code = askBox(ed,text,label,subtext)
  code = validateFileid(code)
  if code and len(code) > 0:
    label = gtk.Label(code)
    label.show()
    label.set_width_chars(4)
    row.pack_start(label,False,False,2)
    entry = gtk.Entry()
    entry.show()
    entry.set_width_chars(20)
    row.pack_start(entry,False,False,2)
    target.pack_start(row,False,False,2)
    entry.grab_focus()
    entry.connect("focus-out-event",setStory,code)
    refreshEd(parent,ed)
  else:
    status.push(0,"Story add cancelled.")
    return False

def refreshEd(parent,ed):
  (x,y,w,h) = ed.vbox.get_allocation()
  if w < 250: w = 250
  ed.resize(w + 5,h + 5)
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

picklist = []

def storyPicker(parent,name,value):
  global picklist
  global stories
  picklist = csplit(str(value))
  title = "Stories involving %s" % name
  if not len(stories):
    stories = myStories(config.get("worlddir"))
  askbox = gtk.Dialog(title,parent,gtk.DIALOG_DESTROY_WITH_PARENT,None)
  askbox.add_button("Cancel",1)
  askbox.add_button("Set",0)
  for key in sorted(stories.keys()):
    title = stories.get(key,"")
    if title and len(title) > 0:
      button = gtk.CheckButton(title)
      button.show()
      button.unset_flags(gtk.CAN_FOCUS)
      button.connect("toggled",updatePicklist,key)
      if key in picklist:
        button.set_active(True)
      askbox.vbox.pack_start(button,True,True,2)
# OK button closes dialog, turns keys into a csv string and returns it (nondefined values, plus defined that are checked)
  askbox.move(config['pos'][0] + 50,config['pos'][1] + 50)
  value = askbox.run()
  askbox.destroy()
  if value == 0:
    output = ""
    for k in range(len(picklist)):
      if k > 0:
        output += ", "
      output += picklist[k]
    return output
  else:
    status.push(0,"Cancel: Stories not modified.")
  return None

def updatePicklist(caller,key):
  global picklist
  if caller.get_active() and key not in picklist:
    picklist.append(key)
  elif not caller.get_active() and key in picklist:
    picklist.remove(key)

def expandTitles(value):
  global stories
  picklist = csplit(str(value))
  titles = ""
  if not len(stories):
    stories = myStories(config.get("worlddir"))
  for item in picklist:
    if config['debug'] > 5: print "'%s' - '%s'" % (item,stories.get(item))
    if stories.get(item):
      titles += "%s\n" % stories[item]
    else:
      titles += "\'%s\'\n" % item
  titles = titles[:-1]
  return titles

