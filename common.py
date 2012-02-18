#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

import pygtk
pygtk.require('2.0')
import gtk

import re
from status import status
from backends import worldList

def say(text):
  print text # TODO: Make this a GTK dialog box.

def bsay(caller,text):
  say(text)

def askBoxProcessor(e,prompt,answer):
  prompt.response(answer)

def askBox(parent,text,label,subtext = None):
  askbox = gtk.MessageDialog(parent,gtk.DIALOG_DESTROY_WITH_PARENT,gtk.MESSAGE_QUESTION,gtk.BUTTONS_OK_CANCEL)
  askbox.set_markup(text)
  row = gtk.HBox()
  if subtext: askbox.format_secondary_markup(subtext)
  entry = gtk.Entry()
  entry.connect("activate",askBoxProcessor,askbox,gtk.RESPONSE_OK)
  row.pack_start(gtk.Label(label),False,False,5)
  row.pack_start(entry)
  askbox.vbox.pack_end(row,True,True,0)
  width, height = askbox.get_size()
  askbox.move((gtk.gdk.screen_width() / 2) - (width / 2),(gtk.gdk.screen_height() / 2) - (height / 2))
  askbox.show_all()
  askbox.move((gtk.gdk.screen_width() / 2) - (width / 2),(gtk.gdk.screen_height() / 2) - (height / 2))
  askbox.run()
  answer = entry.get_text()
  askbox.destroy()
  return answer

def validateFileid(fileid):
  output = ""
  match = re.match(r'^[\w-]+$',fileid)
  if match: output = match.group()
  if len(output) > 0: return output
  return None

def recordSelectBox(parent,fileid,title = "Select Record"):
  global worldList
  askbox = gtk.Dialog(title,parent,gtk.DIALOG_DESTROY_WITH_PARENT,("Cancel",86))
  answers = {}
  colbox = gtk.HBox()
  colbox.show()
  askbox.vbox.pack_start(colbox,True,True,1)
  col = gtk.VBox()
  col.show()
  colbox.pack_start(col,False,False,1)
  bound = 20
  sepcount = 0
  sepnames = {'p':("People","person"),'l':("Places","place"),'c':("Cities","city"),'s':("States","state"),'i':("Items","item")}
  for li in ['p','l','c','s','i']:
    if worldList.get(li):
      count = len(worldList[li])
      if count:
        sep = gtk.Label(sepnames.get(li,("Other","other"))[0])
        sep.show()
        sepcount += 1
        if len(answers) + sepcount >= bound:
          col = gtk.VBox()
          col.show()
          colbox.pack_start(col,False,False,1)
          sepcount = 1
          bound += 20
        col.pack_start(sep,True,True,1)
      for value in sorted(worldList[li]):
        if len(answers) + sepcount >= bound:
          col = gtk.VBox()
          col.show()
          colbox.pack_start(col,False,False,1)
          sepcount = 0
          bound += 20
        if value != fileid:
          rid = len(answers)
          answers[str(rid)] = (value,sepnames[li][1])
          button = gtk.Button(value)
          button.show()
          button.connect("clicked",askBoxProcessor,askbox,rid)
          col.pack_start(button)
  width, height = askbox.get_size()
  askbox.move((gtk.gdk.screen_width() / 2) - (width / 2),(gtk.gdk.screen_height() / 2) - (height / 2))
  answers['86'] = ""
  answer = askbox.run()
  askbox.destroy()
  if answer < 0: answer = 86
  return answers[str(answer)]
