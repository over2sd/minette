#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

import pygtk
pygtk.require('2.0')
import gtk

import re
from status import status

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
  output = match.group()
  if len(output) > 0: return output
  return None