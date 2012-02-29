#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

import pygtk
pygtk.require('2.0')
import gtk

import os
import re
import datetime
from choices import myStories
from globdata import (config,people,places,stories)
import preread
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
    values = [x.strip() for x in s.split(',')]
  return values

def buildarow(scroll,name,data,fileid,key,style = 0):
  """Returns a row containing the given key description and value in a GTK HBox."""
  row = gtk.HBox()
  row.set_border_width(2)
  row.show()
  row.label = gtk.Label(name)
  row.label.set_width_chars(20)
  valign = 0.5
  if style == 0:
    value = getInf(data,["info",key])
    row.e = gtk.Entry()
    row.e.set_text(value)
    activateInfoEntry(row.e,scroll,data,fileid,key)
  if style == 1:
    valign = 0.03
    row.e = buildaposition(scroll,data,fileid,key)
  if style == 2:
    value = getInf(data,["info",key])
    row.e = gtk.Label()
    if config.get('showstories') == "titlelist":
      valign = 0.03
      row.e.set_text(expandTitles(value))
    else: # elif config['showstories'] == "idlist":
      row.e.set_text(value)
    stbut = gtk.Button("Set")
    stbut.show()
    stbut.connect("clicked",setStories,data,fileid,row.e,None)
    row.pack_end(stbut,False,False,2)
    row.e.set_alignment(0.05,0)
  row.label.set_alignment(1,valign)
  row.label.show()
  row.pack_start(row.label,0,0,2)
  row.e.show()
  row.pack_start(row.e,1,1,2)
  return row

def getInf(data,path,default = ""):
  """Returns the value of a key path in the given data, a given default, or an empty string."""
  end = len(path) - 1
  if not data or end < 0:
    print "Bad data to getInf: %s %s" % (data, path)
    return default
  i = 0
  while i < end:
    if config['debug'] > 5: print str(data) + '\n'
    if data.get(path[i]):
      data = data[path[i]]
      i += 1
    else:
      return default
  value = default
  try:
    (value,mod) = data.get(path[-1],(default,False))
  except ValueError as e:
    print "%s yields %s with %s" % (path,data.get(path[-1],(default,False)),e)
  return value

def activateInfoEntry(self, scroll, data, fileid, key, extra = 0, exargs = []):
  cat = data.get("cat")
  path = []
  if cat == 'p' or cat == 'l': path = [fileid,"info",key]
  for i in range(len(exargs)): path.append(exargs[i])
  self.connect("focus-out-event", checkForChange,data,path)
  self.connect("focus-in-event",scrollOnTab,scroll)

def activateNoteEntry(self, scroll, data, fileid, i,date):
  cat = data.get("cat")
  path = []
  if cat == 'l': path = [fileid,"info","notes",i]
  self.connect("focus-out-event", checkForChange,data,path,date)
  self.connect("focus-in-event",scrollOnTab,scroll)

def checkForChange(self,event,data,path,optionaltarget = None):
  if config['debug'] > 3: print "Checking " + str(path)
  if getInf(data,path[1:]) != self.get_text():
    if config['debug'] > 2 : print str(getInf(data,path[1:])) + " vs " + self.get_text()
    markChanged(self,data.get("cat"),path)
    if optionaltarget: # Automatically update a linked date field
      optionaltarget.set_text(skrTimeStamp(1))
      markChanged(optionaltarget,data.get("cat"),path)

def markChanged(self,cat,path):
  self.modify_base(gtk.STATE_NORMAL,gtk.gdk.color_parse("#CCCCDD")) # change background for edited
  end = len(path)
  value = ["",False]
  value[1] = True
  value[0] = self.get_text()
  if cat == 'p':
    global people
    goforit = preread.preReadp(True,path[:-1],end)
    if goforit:
      if end == 3:
        try:
          people[path[0]][path[1]][path[2]] = value
        except KeyError:
          print "Could not mark " + path[2] + " as changed."
          return
      elif end == 4:
        try:
          people[path[0]][path[1]][path[2]][path[3]] = value
        except KeyError:
          print "Could not mark " + path[3] + " as changed."
          return
      elif end == 5:
        try:
          people[path[0]][path[1]][path[2]][path[3]][path[4]] = value
        except KeyError:
          print "Could not mark " + path[4] + " as changed."
          return
      elif end == 6:
        try:
          people[path[0]][path[1]][path[2]][path[3]][path[4]][path[5]] = value
        except KeyError:
          print "Could not mark " + path[5] + " as changed."
          return
      elif end == 7:
        try:
          people[path[0]][path[1]][path[2]][path[3]][path[4]][path[5]][path[6]] = value
        except KeyError:
          print "Could not mark " + path[6] + " as changed."
          return
      else:
        say("Path too long")
        return
      people[path[0]]['changed'] = True
      if config['debug'] > 2: print "Value set: " + getInf(people.get(path[0]),path[1:])
    else:
      print "Invalid path"
      return
  elif cat == 'l':
    global places
    goforit = preread.preReadl(True,path[:-1],end)
    if goforit:
      if end == 3:
        try:
          places[path[0]][path[1]][path[2]] = value
        except KeyError:
          print "Could not mark " + path[2] + " as changed."
          return
      elif end == 4:
        try:
          places[path[0]][path[1]][path[2]][path[3]] = value
        except KeyError:
          print "Could not mark " + path[3] + " as changed."
          return
      elif end == 5:
        try:
          places[path[0]][path[1]][path[2]][path[3]][path[4]] = value
        except KeyError:
          print "Could not mark " + path[4] + " as changed."
          return
      elif end == 6:
        try:
          places[path[0]][path[1]][path[2]][path[3]][path[4]][path[5]] = value
        except KeyError:
          print "Could not mark " + path[5] + " as changed."
          return
      elif end == 7:
        try:
          places[path[0]][path[1]][path[2]][path[3]][path[4]][path[5]][path[6]] = value
        except KeyError:
          print "Could not mark " + path[6] + " as changed."
          return
      else:
        say("Path too long")
        return
      places[path[0]]['changed'] = True
      if config['debug'] > 2: print "Value set: " + getInf(places.get(path[0]),path[1:])
    else:
      print "Invalid path"
      return

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
  titles = titles[:-1] # trim that last newline
  return titles

def setStory(widget,event,key):
  global stories
  if stories.get(key) != widget.get_text():
    stories[key] = widget.get_text()
    widget.modify_base(gtk.STATE_NORMAL,gtk.gdk.color_parse("#CCFFCC")) # change background for edited

def setStories(caller,data,fileid,x,parent):
  name = getInf(data,["info","commonname"])
  cat = data.get("cat")
  value = ""
  if config.get('showstories') == "titlelist":
    value = getInf(data,["info","stories"])
  else:
    value = x.get_text()
  value = storyPicker(parent,name,value)
  if value:
    if cat == 'p':
      global people
      if preread.preReadp(False,[fileid,"info","stories"],3):
        people[fileid]['info']['stories'] = [value,True]
        people[fileid]['changed'] = True
    elif cat == 'l':
      global places
      if preread.preReadl(False,[fileid,"info","stories"],3):
        places[fileid]['info']['stories'] = [value,True]
        places[fileid]['changed'] = True
    if config.get('showstories') == "titlelist":
      value = expandTitles(value)
    x.set_text(value)

def buildaposition(scroll,data,fileid,key): #only applicable to people, but can't put it back in people because of circular import :(
  """Returns a GTK VBox containing the data values of the given position."""
  t = gtk.VBox()
  t.show()
  data = {}
  try:
    data = people[fileid]
  except KeyError as e:
    print "Error getting info from %s: %s" % (fileid,e)
    return ""
  data2 = {}
  if data.get("info"): data2 = data["info"].get(key)
  value = data2.get("pos")
  if value: value = value[0]
  else:
    print "no data"
    return ""
  if data2.get("events"):
    rows = len(data2['events'])
#    t.addpos = gtk.Button("Add Position")
    t.addmile = gtk.Button("Add milestone")
    t.addmile.show()
    r = gtk.HBox()
    r.show()
    r.pack_end(t.addmile,False,False,2)
    if rows > 0:
      t.phead = gtk.Label("Position")
      t.phead.show()
      t.phead.set_width_chars(16)
      r.pack_start(t.phead,0,0,1)
      t.mhead = gtk.Label("Milestone")
      t.mhead.show()
      t.mhead.set_width_chars(18)
      r.pack_start(t.mhead,1,1,2)
      t.pack_start(r,False,False,1)
      r = gtk.HBox()
      r.show()
      rpos = gtk.Entry()
      extraargs = ["pos",]
      activateInfoEntry(rpos,scroll,data,fileid,key,len(extraargs),extraargs)
      rpos.show()
      rpos.set_text(value)
      rpos.set_width_chars(16)
      r.pack_start(rpos,0,0,2)
      t.dhead = gtk.Label("Date")
      t.dhead.show()
      t.dhead.set_width_chars(8)
      r.pack_start(t.dhead,1,1,2)
      t.ehead = gtk.Label("Event")
      t.ehead.show()
      t.ehead.set_width_chars(18)
      r.pack_start(t.ehead,1,1,2)
      t.pack_start(r,False,False,1)
      for i in range(rows):
        r = gtk.HBox()
        r.show()
        blank = gtk.Label()
        blank.set_width_chars(12)
        blank.show()
        r.pack_start(blank,0,0,2)
        value = data['info'][key]['events'][str(i)].get("date","")
        if value: value = value[0]
        rda = gtk.Entry()
        extraargs = ["events",str(i),"date"]
        activateInfoEntry(rda,scroll,data,fileid,key,len(extraargs),extraargs)
        rda.show()
        rda.set_width_chars(12)
        rda.set_text(value)
        r.pack_start(rda,1,1,2)
        value = getInf(data,["info",key,"events",str(i),"event"])
        if value: value = value[0]
        rev = gtk.Entry()
        extraargs = ["events",str(i),"event"]
        activateInfoEntry(rev,scroll,people.get(fileid),fileid,key,len(extraargs),extraargs)
        rev.show()
        rev.set_width_chars(18)
        rev.set_text(value)
        r.pack_start(rev,1,1,2)
        t.pack_start(r,False,False,1)
#        print str(t.size_request())
    (x,y,width,height) = r.get_allocation()
    t.addmile.connect("clicked",addMilestone,scroll,t,data,fileid,"info",key,width)
  return t

def addMilestone(caller,scroll,target,data,fileid,side,key,boxwidth):
  i = 0
  err = False
  if data:
    if data.get(side):
      if data[side].get(key):
        if not data[side][key].get("events"):
          data[side][key]["events"] = {}
        i = str(len(data[side][key]['events']))
        data[side][key]['events'][i] = {}
        data[side][key]['events'][i]['date'] = ["",False]
        data[side][key]['events'][i]['event'] = ["",False]
      else:
        print "Could not find %s in record %s!" % (key,fileid)
        err = True
    else:
      x = "relations"
      if side == "info": x = "info"
      if config['debug'] > 0: print "%s %s %s %s %s %s %s" % (caller,target,data,fileid,side,key,boxwidth)
      print "Record %s has no %s!" % (fileid,x)
      err = True
  else:
    print "Could not find " + fileid + "!"
    err = True
  if config['debug'] > 5: print str(target)
  if not err:
    rowmile = gtk.HBox()
    rowmile.show()
    blank = gtk.Label()
    blank.show()
    blank.set_width_chars(12)
#    blank.set_size_request(int(boxwidth * 0.20),10)
    rowmile.pack_start(blank,0,0,2)
    d = gtk.Entry()
    d.show()
    d.set_width_chars(12)
    d.set_text(getInf(data,[side,key,'events',i,'date']))
    rowmile.pack_start(d,1,1,2)
    d.grab_focus()
    e = gtk.Entry()
    e.show()
    e.set_width_chars(18)
    e.set_text(getInf(data,[side,key,'events',i,'event']))
    if side == "relat":
      activateRelEntry(d,scroll,data,fileid,key,"date",i)
      activateRelEntry(e,scroll,data,fileid,key,"event",i)
    elif side == "info":
      extraargs = ["events",i,"date"]
      activateInfoEntry(d,scroll,data,fileid,key,len(extraargs),extraargs)
      extraargs[2] = "event"
      activateInfoEntry(e,scroll,data,fileid,key,len(extraargs),extraargs)
    rowmile.pack_start(e,1,1,2)
    target.add(rowmile)

def activateRelEntry(self,scroll,data,fileid,relid,key,event = None):
  path = [fileid,"relat",relid]
  if event:
    path.extend(["events",event,key])
  else:
    path.append(key)
  self.connect("focus-out-event", checkForChange,data,path)
  self.connect("focus-in-event",scrollOnTab,scroll)

def scrollOnTab(caller,x,scroll):
  a = caller
  b = a.get_allocation().y
  c = a.get_allocation().height
  d = scroll.get_vadjustment().get_value()
  e = scroll.get_allocation().height
  f = b + c
  g = f - e
  h = e + d
  if f > h:
    adj = scroll.get_vadjustment()
    adj.set_value(g + 2)
    scroll.set_vadjustment(adj)
  elif d > b:
    adj = scroll.get_vadjustment()
    adj.set_value(b - 2)
    scroll.set_vadjustment(adj)

def customlabel(cat,text,tab,close = 0):
  icon = None
  if cat == 'p':
    icon = "img/person.png"
  if cat == 'l':
    icon = "img/place.png"
  if cat == 'c':
    icon = "img/city.png"
  if cat == 's':
    icon = "img/state.png"
  if cat == 'o':
    icon = "img/org.png"
  if cat == 'i':
    icon = "img/item.png"
  row = gtk.HBox()
  label = gtk.Label(text)
  image = None
  if icon:
    icon = os.path.abspath(icon)
  if os.path.exists(icon):
    image = gtk.Image()
    image.set_from_file(icon)
    image.show()
  label.show()
  row.show()
  if image:
    row.pack_start(image,False,False,1)
  row.pack_start(label,True,True,1)
  return row


def sayBox(parent,text,text2 = None,text3 = None,text4 = None,text5 = None):
  askbox = gtk.MessageDialog(parent,gtk.DIALOG_DESTROY_WITH_PARENT,gtk.MESSAGE_QUESTION,gtk.BUTTONS_OK)
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


def addHelpMenu(self):
  itemH = gtk.MenuItem("_Help",True)
  itemH.show()
  self.mb.append(itemH)
  h = gtk.Menu()
  h.show()
  itemH.set_submenu(h)
  itemHA = gtk.MenuItem("_About",True)
  h.append(itemHA)
  itemHA.show()
  itemHA.connect("activate",showHelp,self)

def showHelp(caller,parent):
  bsay(parent,"Icons provided by http://www.fatcow.com/free-icons")

