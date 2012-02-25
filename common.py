#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

import pygtk
pygtk.require('2.0')
import gtk

import re
import datetime
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
  entry.grab_focus()
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

def skrTimeStamp(style):
  """Returns a timestamp in one of my preferred formats"""
  ts = ""
  now = datetime.datetime.now()
  if style == 1:
    ts = now.strftime("%y/%m/%db")
  return ts

def kill(caller,widget):
  widget.destroy()

def csplit(s):
  values = None
  if str(s)[0] == '[': # This is not very smart code. But it'll do a little, if the input isn't too wonky.
    pattern = re.compile(r'^\[(.+)\]$')
    match = pattern.search(s)
    s = match.group(1)
    pattern = re.compile(r'u?[\'\"](.+?)[\'\"],?')
    s = pattern.findall(s)
    for item in s:
      if not values: values = []
      values.append(re.sub(r"\'",r'',item))
  else:
    values = s.split(',')
  return values