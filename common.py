#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

import pygtk
pygtk.require('2.0')
import gtk
import os
import re
import datetime
import time

import backends
from choices import myStories
from debug import (printPretty,debugPath)
from globdata import (cities,config,people,places,states,stories,mainWin,menuBar,mainSelf)
from status import status
import story

def say(text):
  print text # TODO: Make this a GTK dialog box.

def bsay(caller,text):
  if caller == "?": caller = mainWin
  say(text)

def addLocButton(row,format,**kwargs):
  button = gtk.Button("Choose City")
  button.show()
  row.pack_start(button,False,False,2)
  button.connect("clicked",chooseCity,format,kwargs) # 0 = "city, state"

def askBoxProcessor(e,prompt,answer):
  prompt.response(answer)

def askBox(parent,text,label,**kwargs):
  subtext = None
  nospace = False
  for key in kwargs:
    if config['debug'] > 3: print "%s:%s" % (key,kwargs[key])
    if key == "nospace": nospace = kwargs[key]
    if key == "subtext": subtext = kwargs[key]
  if parent == "?": parent = mainWin
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
  if nospace: answer = answer.replace(' ','-') # Spaces not allowed.
  askbox.destroy()
  return answer

def askCityBox(parent):
  if parent == "?": parent = mainWin
  row = gtk.HBox()
  row.show()
  label = gtk.Label("Location:")
  label.set_width_chars(7)
  label.set_alignment(1,0.5)
  choices = backends.getCityList()
  loc = gtk.combo_box_new_text()
  loc.set_size_request(200,32)
  keys = []
  i = 0
  for key in sorted(choices.keys()):
    if choices.get(key) and choices[key][0] and choices[key][2]:
      loc.append_text("%s, %s" % (choices[key][0],choices[key][2]))
      keys.append(key)
      i += 1
  askBox = None
  if len(keys) > 0:
    askbox = gtk.MessageDialog(parent,gtk.DIALOG_DESTROY_WITH_PARENT,gtk.MESSAGE_QUESTION,gtk.BUTTONS_OK_CANCEL)
  else:
    askbox = gtk.MessageDialog(parent,gtk.DIALOG_DESTROY_WITH_PARENT,gtk.MESSAGE_WARNING,gtk.BUTTONS_OK)
  if len(keys) > 0:
    askbox.set_markup("Choose a city:")
    label.show()
    row.pack_start(label,False,False,2)
    loc.show()
    row.pack_start(loc,True,True,2)
  else:
    askbox.format_secondary_markup("Please create at least one city and state before using this dialog.")
  askbox.vbox.pack_end(row,True,True,0)
  width, height = askbox.get_size()
  askbox.move((gtk.gdk.screen_width() / 2) - (width / 2),(gtk.gdk.screen_height() / 2) - (height / 2))
  askbox.move((gtk.gdk.screen_width() / 2) - (width / 2),(gtk.gdk.screen_height() / 2) - (height / 2))
  askbox.run()
  key = None
  if len(keys) > 0:
    key = loc.get_active_text()
  askbox.destroy()
  loc.destroy()
  loc = [False,None,None,None,None]
  lockeys = {}
  if key is not None and len(key) > 0:
    lockeys = backends.getCityList(1)
    key = lockeys.get(key,'N')
    lockeys = backends.getCityList()
    if config['debug'] > 0: print "new key: %s" % key
    print "%s (%s), %s (%s)" % (lockeys[key][0],key,lockeys[key][2],lockeys[key][1])
    loc[1] = key
    loc[2] = lockeys[key][0]
    loc[3] = lockeys[key][1]
    loc[4] = lockeys[key][2]
    loc[0] = True
  if config['debug'] > 0: printPretty(loc)
  return loc

def chooseCity(caller,format,kwargs):
  entry = None
  citykey = None
  statekey = None
  cityfilekey = None
  statefilekey = None
  data = None
  for key in kwargs:
    if key == "entry": entry = kwargs[key]
    elif key == "city": citykey = kwargs[key]
    elif key == "state": statekey = kwargs[key]
    elif key == "cityfile": cityfilekey = kwargs[key]
    elif key == "statefile": statefilekey = kwargs[key]
    elif key == "data": data = kwargs[key]
  loc = [False,None,None,None,None]
  loc = askCityBox("?")
  entry.set_text("%s, %s" % (loc[2],loc[4]))
  if format == 0 and loc[0] is True:
    pass
  elif format == 1 and data is not None and citykey is not None and cityfilekey is not None and statekey is not None and statefilekey is not None:
    if data.get("info") is not None:
      data['info'][citykey] = [loc[2],True]
      data['info'][cityfilekey] = [loc[1],True]
      data['info'][statekey] = [loc[4],True]
      data['info'][statefilekey] = [loc[3],True]
      data['changed'] = True

def clearMenus(caller = None):
  global mainSelf
  m = mainSelf
  if m:
    printPretty(m.get_children())
  else:
    printPretty(m)
  print "Menus destroyed!"

def dateChoose(caller,target,data,path):
  askbox = gtk.MessageDialog(None,gtk.DIALOG_DESTROY_WITH_PARENT,gtk.MESSAGE_QUESTION,gtk.BUTTONS_OK_CANCEL)
  askbox.set_markup("Choose a date")
  cal = gtk.Calendar()
  cal.show()
  (y,m,d) = parseDate(target.get_text())
  cal.select_month(m-1,y)
  cal.select_day(d)
  month = gtk.Entry(3)
  month.set_text(str(m))
  year = gtk.Entry(5)
  year.set_text(str(y))
  row = gtk.HBox()
  row.show()
  month.connect("activate",lambda x: cal.select_month(int(month.get_text())-1,int(year.get_text())))
  year.connect("activate",lambda x: cal.select_month(int(month.get_text())-1,int(year.get_text())))
  row.pack_start(gtk.Label("Month:"),0,0,2)
  row.pack_start(month,0,0,2)
  row.pack_start(gtk.Label("Year:"),0,0,2)
  row.pack_start(year,0,0,2)
  row.show_all()
  askbox.vbox.pack_start(row,0,0,2)
  askbox.vbox.pack_start(cal,1,1,2)
  (x,y,w,h) = caller.get_allocation()
  (x2,y2,w,h) = askbox.get_allocation()
  w = int(w / 2)
  h = int(h / 2)
  askbox.move(x - w,y - h)
  result = askbox.run()
  if result == gtk.RESPONSE_OK:
    setDate(cal,target)
  askbox.destroy()
  checkForChange(target,None,data,path)

def displayStage1(target,fileid,cat,saveFunc,showFunc,preCloser,opener):
  target.vbox = gtk.VBox()
  target.vbox.show()
  target.vbox.ftabs = gtk.Notebook()
  target.vbox.ftabs.show()
  bbar = gtk.HButtonBox()
  bbar.show()
  bbar.set_spacing(2)
  save = gtk.Button("Save")
  image = gtk.Image()
  image.set_from_file("img/save.png")
  save.set_image(image)
  save.connect("clicked",saveFunc,fileid)
  save.show()
  bbar.pack_start(save)
  if config['debug'] > 0:
    report = gtk.Button("Report")
    image = gtk.Image()
    image.set_from_file("img/report.png")
    report.set_image(image)
    report.connect("clicked",showFunc,fileid)
    report.show()
    bbar.pack_start(report)
  # endif
  revert = gtk.Button("Reload")
  image = gtk.Image()
  image.set_from_file("img/rev.png")
  revert.set_image(image)
  revert.show_all()
  revert.connect("clicked",reloadThis,preCloser,opener,fileid,target.vbox,target)
  bbar.pack_start(revert)

# other buttons...   reload,etc.   ...go here

  close = gtk.Button("Close")
  image = gtk.Image()
  image.set_from_file("img/subtract.png")
  close.set_image(image)
  close.show_all()
  close.connect("clicked",preCloser,fileid,target.vbox)
  bbar.pack_end(close)
  target.vbox.pack_start(bbar,False,False,2)
  target.vbox.pack_start(target.vbox.ftabs,True,True,2)
  target.labelname = customlabel(cat,fileid,target.vbox)
  target.labelname.show_all()
  target.append_page(target.vbox,target.labelname)
#  if warnme and config['openduplicatetabs']:
#    target.vbox.ftabs.<function to change background color as warning>
#    Here, add a widget at the top of the page saying it's a duplicate, and that care must be taken not to overwrite changes on existing tab.
#    Here, attach ftabs to warning VBox
#  else:
#    Here, attach ftabs to target

def displayStage2(target,labelWidget):
  target.sw = gtk.ScrolledWindow()
  target.sw.set_policy(gtk.POLICY_NEVER,gtk.POLICY_ALWAYS)
  target.sw.show()
  target.append_page(target.sw,labelWidget)
  target.set_tab_label_packing(target.sw,True,True,gtk.PACK_START)
  page = gtk.VBox()
  page.show()
  target.sw.add_with_viewport(page)
  page.set_border_width(5)
  return page

def firstRunTab(base,tabrow):
  tabrow.fr = gtk.VBox()
  tabrow.fr.show()
  tabrow.append_page(tabrow.fr,gtk.Label("First Run Tutorial"))
# ..............................................................................................
  tut1 = "\n\t\
This tutorial will only display as long as you do not use a configuration file. Load with a\
\nconfiguration file as the first argument, or create 'default.cfg' in the program's directory\
\nto stop seeing this welcome tab.\
\n\tTo begin, Use the Person menu to load an existing record or make a new record.\
\n\tTo set a Landmark's location, you must create at least one City and one State record."
# ..............................................................................................
  tabrow.tut = gtk.Label(tut1)
  tabrow.tut.show()
  tabrow.fr.add(tabrow.tut)
  tabrow.close = gtk.Button("Close Tutorial")
  tabrow.close.show()
  tabrow.close.connect("clicked",kill,tabrow.fr)
  tabrow.toggle = gtk.CheckButton("Don't show again")
  tabrow.toggle.show()
  tabrow.toggle.connect("clicked",setTutorialSeen)
  tabrow.fr.add(tabrow.toggle)
  tabrow.fr.add(tabrow.close)

def getFileid(caller,tabs,makeThis,cat,one = "Please enter a new unique filing identifier.",two = "Fileid:",three = "This short identifier will be used to link records together and identify the record on menus. Valid characters are A-Z, 0-9, underscore, and dash. Do not include spaces or an extension, such as \".xml\"."):
  four = "New %s cancelled." % cat
  fileid = askBox("?",one,two,subtext=three,nospace=True)
  fileid = validateFileid(fileid)
  if fileid and len(fileid) > 0:
    makeThis(caller,fileid,tabs)
  else:
    say(four)

def loadRealm(fn):
  clearMenus()
  # clear worldList
  # loadConfig
  # populateWorld
  # reAddLoadMenus
  pass

def loadRealmCst(parent):
  fn = ""
  # file select dialog
  loadRealm(fn)
  pass

def loadRealmStd(fileid): # From a menu list
  fn = validateFileid(fileid)
  fn = "realms/%s.rlm" % fn
  loadRealm(fn)

def preRead(force,cat,path,depth = 0,retries = 0):
  """Using the global dict for the given category, and given a list of keys 'path' and an integer 'depth',
  checks a path in the target dict for reading, to a depth of 'depth'. If 'force' is True, the function
  will build missing tree branches, to allow you to write to the endpoint. Do not call force with a
  path/depth ending in a list, tuple, or something other than a dict, which this function produces. Call
  force on one path higher.
  """
  limit = 6 # Lower limit for printing debug messages in this function
  root = None
  if cat == 'p':
    global people
    root = people
  elif cat == 'l':
    global places
    root = places
  elif cat == 'c':
    global cities
    root = cities
  elif cat == 's':
    global states
    root = states
  elif cat == 'o':
    global orgs
    root = orgs
  elif cat == 'i':
    global items
    root = items
  else:
    print "ERR: Invalid category %s passed to markChanged." % cat
  if not root:
    print "preRead: Invalid category %s?" % cat
    return False
  if depth > len(path): depth = len(path)
  if depth > 7: depth = 7
  if path[0] in root.keys():
    if depth <= 1:
      return True
    if path[1] in root[path[0]].keys():
      if depth <= 2:
        return True
      if path[2] in root[path[0]][path[1]].keys():
        if depth <= 3:
          return True
        if path[3] in root[path[0]][path[1]][path[2]].keys():
          if depth <= 4:
            return True
          if path[4] in root[path[0]][path[1]][path[2]][path[3]].keys():
            if depth <= 5:
              return True
            if path[5] in root[path[0]][path[1]][path[2]][path[3]][path[4]].keys():
              if depth <= 6:
                return True
              if path[6] in root[path[0]][path[1]][path[2]][path[3]][path[4]][path[5]].keys():
                return True # Maximum depth reached
              elif force:
                root[path[0]][path[1]][path[2]][path[3]][path[4]][path[5]][path[6]] = {}
                if retries >= depth: force = False
                return preRead(force,cat,path,depth,retries + 1)
              else: # Not found, and not forcing it to be found
                if config['debug'] > limit: debugPath(root,path)
                return False
            elif force:
              root[path[0]][path[1]][path[2]][path[3]][path[4]][path[5]] = {}
              if retries >= depth: force = False
              return preRead(force,cat,path,depth,retries + 1)
            else: # Not found, and not forcing it to be found
              if config['debug'] > limit: debugPath(root,path)
              return False
          elif force:
            root[path[0]][path[1]][path[2]][path[3]][path[4]] = {}
            if retries >= depth: force = False
            return preRead(force,cat,path,depth,retries + 1)
          else: # Not found, and not forcing it to be found
            if config['debug'] > limit: debugPath(root,path)
            return False
        elif force:
          root[path[0]][path[1]][path[2]][path[3]] = {}
          if retries >= depth: force = False
          return preRead(force,cat,path,depth,retries + 1)
        else: # Not found, and not forcing it to be found
          if config['debug'] > limit: debugPath(root,path)
          return False
      elif force:
        root[path[0]][path[1]][path[2]] = {}
        if retries >= depth: force = False
        return preRead(force,cat,path,depth,retries + 1)
      else: # Not found, and not forcing it to be found
        if config['debug'] > limit: debugPath(root,path)
        return False
    elif force:
      root[path[0]][path[1]] = {}
      if retries >= depth: force = False
      return preRead(force,cat,path,depth,retries + 1)
    else: # Not found, and not forcing it to be found
      if config['debug'] > limit: debugPath(root,path)
      return False
  else: # First level (fileid) can't be generated.
    if config['debug'] > limit: debugPath(root,path)
    return False

def reAddLoadMenu(parent,cat):
  menuList[cat]['f'](parent,menuList[cat].get("m"))

def reloadThis(caller,closer,opener,fileid,mark,target):
  status.push(0,"Attempting to reload %s..." % fileid)
  closer(caller,fileid,mark)
  opener(caller,fileid,target)

def reorderTabs(tabs):
  """Functions looks at a notebook and reorders the tab numbers after one is closed"""
  # TODO: Write this... or figure out whether it's still needed.
  pass

def setDate(cal,target):
  (y,m,d) = cal.get_date()
  t = (y,m+1,d,0,0,0,0,0,0)
  style = config.get('datestyle',"%Y/%m/%db")
  if True: style = re.sub(r'%y',r'%Y',style)
  target.set_text(time.strftime(style,t))

def setTutorialSeen(caller,event = None):
  global config
  config['seenfirstrun'] = caller.get_active()
  if config['debug'] > 6:
    print "%s %s" % (caller,caller.get_active())
    printPretty(config)
  backends.saveConfig(config.get("file","default.cfg"))

def parseDate(date):
  now = datetime.datetime.now()
  y = now.year
  m = now.month
  d = now.day
  pattern = re.compile(r'.*?([0-9]+)[/\.]([0-9]+)[/\.]([0-9]+)b?')
  result = pattern.search(date)
  if result:
    y = long(result.group(1))
    if y < 100:
      if y > config['centbreak']: y -= 100
      y = config['century'] + y
    m = int(result.group(2))
    d = int(result.group(3))
  return (y,m,d)

def validateFileid(fileid):
  output = ""
  if fileid.find(".xml"): fileid = fileid.split('.')[0] # No file extension allowed
  match = re.match(r'^[\w-]+$',fileid)
  if match: output = match.group()
  if len(output) > 0: return output
  return None

def skrTimeStamp(style = "%y/%m/%db"):
  """Returns a timestamp in one of my preferred formats"""
  ts = ""
  now = datetime.datetime.now()
  ts = now.strftime(style)
  return ts

def kill(caller,widget):
  widget.destroy()

def csplit(s):
  values = None
  if not len(str(s)): return values
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
  if not values: values = []
  return values

def buildarow(scroll,name,data,fileid,key,style = 0):
  """Returns a row containing the given key description and value in a GTK HBox."""
  row = gtk.HBox()
  row.set_border_width(2)
  row.show()
  row.label = gtk.Label(name)
  row.label.set_width_chars(20)
  valign = 0.5
  if style == 0 or style == 3:
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
      if len(str(value)): row.e.set_text(expandTitles(value))
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
  if style == 3:
    path = [fileid,"info",key]
    placeCalendarButton(data,row,row.e,path)
  return row

def placeCalendarButton(data,row,target,path):
  """Puts a nice little calendar button in row. The calendar button updates
  target with the selected value."""
#  printPretty("args: %s %s %s %s" % (data,row,target,path))
  datebut = gtk.Button()
  datebut.show()
  image = gtk.Image()
  image.set_from_file("img/date.png")
  datebut.set_image(image)
  datebut.unset_flags(gtk.CAN_FOCUS)
  datebut.connect("clicked",dateChoose,target,data,path)
  row.pack_start(datebut,0,0,2)

def getInf(data,path,default = ""):
  """Returns the value of a key path (which must be a list) in the given data, a given default, or an empty string."""
  end = len(path) - 1
  if not data or end < 0:
    printPretty("Bad data to getInf: %s %s" % (data, path))
    return default
  i = 0
  while i < end:
    if config['debug'] > 5: printPretty(str(data) + '\n')
    if data.get(path[i]):
      if config['debug'] > 4: print "seeking %s in %s" % (path[i],data.keys())
      data = data[path[i]]
      i += 1
    else:
      return default
  value = default
  if default in [{},[]]: # expecting dict or list
    if config['debug'] > 4: print "expecting {}/[]"
    value = data.get(path[-1],default)
  else: # expecting string, numeric, etc, that should be part of a [value,bool] pair
    try:
      (value,mod) = data.get(path[-1],(default,False))
    except ValueError as e:
      printPretty("getInf: (nonfatal) %s yields %s with error %s" % (path,data.get(path[-1],(default,False)),e),False)
  return value

def activateInfoEntry(self, scroll, data, fileid, key, extra = 0, exargs = []):
  if config['debug'] > 4:
    printPretty("%s\n%s" % (data,[fileid,key,exargs]))
  cat = data.get("cat")
  path = []
#  if cat in ['p','l','c']:
  path = [fileid,"info",key]
  for i in range(len(exargs)): path.append(exargs[i])
  self.connect("focus-out-event", checkForChange,data,path)
  self.connect("activate", checkForChange,None,data,path)
  self.connect("focus-in-event",scrollOnTab,scroll)

def activateNoteEntry(self, scroll, data, fileid, i,date):
  cat = data.get("cat")
  path = []
  if cat == 'l': path = [fileid,"info","notes",i,"content"]
  self.connect("focus-out-event", checkForChange,data,path,date)
  self.connect("activate", checkForChange,None,data,path,date)
  self.connect("focus-in-event",scrollOnTab,scroll)

def checkForChange(self,event,data,path,optionaltarget = None):
  if config['debug'] > 3: print "Checking " + str(path)
  if getInf(data,path[1:]) != self.get_text():
    if config['debug'] > 2 : print str(getInf(data,path[1:])) + " vs " + self.get_text()
    markChanged(self,data.get("cat"),path)
    if optionaltarget: # Automatically update a linked date field
      optionaltarget.set_text(skrTimeStamp(config['datestyle']))
      markChanged(optionaltarget,data.get("cat"),path)

def markChanged(self,cat,path):
  if path == str(path):
    path = [path] # prevents string from being processed as a long list
  self.modify_base(gtk.STATE_NORMAL,gtk.gdk.color_parse("#CCCCDD")) # change background for edited
  end = len(path)
  value = ["",False]
  value[1] = True
  value[0] = self.get_text()
  root = None
  goforit = False
  if cat == 'p':
    global people
    root = people
  elif cat == 'l':
    global places
    root = places
  elif cat == 'c':
    global cities
    root = cities
  elif cat == 's':
    global states
    root = states
  elif cat == 'o':
    global orgs
    root = orgs
  elif cat == 'i':
    global items
    root = items
  else:
    print "ERR: Invalid category %s passed to markChanged." % cat
  if root:
    if config['debug'] > 6: printPretty(root)
    goforit = preRead(True,cat,path[:-1],end)
    if goforit:
      if end == 3:
        try:
          root[path[0]][path[1]][path[2]] = value
        except KeyError:
          print "Could not mark " + path[2] + " as changed."
          return
      elif end == 4:
        try:
          root[path[0]][path[1]][path[2]][path[3]] = value
        except KeyError:
          print "Could not mark " + path[3] + " as changed."
          return
      elif end == 5:
        try:
          root[path[0]][path[1]][path[2]][path[3]][path[4]] = value
        except KeyError:
          print "Could not mark " + path[4] + " as changed."
          return
      elif end == 6:
        try:
          root[path[0]][path[1]][path[2]][path[3]][path[4]][path[5]] = value
        except KeyError:
          print "Could not mark " + path[5] + " as changed."
          return
      elif end == 7:
        try:
          root[path[0]][path[1]][path[2]][path[3]][path[4]][path[5]][path[6]] = value
        except KeyError:
          print "Could not mark " + path[6] + " as changed."
          return
      else:
        say("Path too long: %s" % path)
        return
      root[path[0]]['changed'] = True
      if config['debug'] > 2: print "Value set: " + getInf(root.get(path[0]),path[1:])
    else:
      printPretty("markChanged: Invalid path (%s)" % path)
      debugPath(root,path)
      return

def expandTitles(value):
  global stories
  titles = ""
  if not len(str(value)): return titles
  picklist = csplit(str(value))
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

def setStories(caller,data,fileid,x,parent):
  name = getInf(data,["info","commonname"])
  cat = data.get("cat")
  value = ""
  if config.get('showstories') == "titlelist":
    value = getInf(data,["info","stories"])
  else:
    value = x.get_text()
  value = story.storyPicker(parent,name,value)
  if value:
    if cat == 'p':
      global people
      if preRead(False,cat,[fileid,"info","stories"],3):
        people[fileid]['info']['stories'] = [value,True]
        people[fileid]['changed'] = True
    elif cat == 'l':
      global places
      if preRead(False,cat,[fileid,"info","stories"],3):
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
    t.addmile.unset_flags(gtk.CAN_FOCUS)
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
        datebut = gtk.Button()
        datebut.show()
        datebut.unset_flags(gtk.CAN_FOCUS)
        image = gtk.Image()
        image.set_from_file("img/date.png")
        datebut.set_image(image)
        cat = data.get("cat")
        path = [fileid,"info",key,"events",str(i),"date"]
        datebut.connect("clicked",dateChoose,rda,data,path)
        r.pack_start(datebut,0,0,2)
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
      if config['debug'] > 0: printPretty("%s %s %s %s %s %s %s" % (caller,target,data,fileid,side,key,boxwidth))
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
    datebut = gtk.Button()
    datebut.show()
    image = gtk.Image()
    image.set_from_file("img/date.png")
    datebut.set_image(image)
    datebut.unset_flags(gtk.CAN_FOCUS)
    datebut.connect("clicked",dateChoose,d,data,[fileid,side,key,'events',i,'date'])
    rowmile.pack_start(datebut,0,0,2)
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
    target.pack_start(rowmile,0,0,1)

def activateRelEntry(self,scroll,data,fileid,relid,key,event = None):
  path = [fileid,"relat",relid]
  if event:
    path.extend(["events",event,key])
  else:
    path.append(key)
  self.connect("focus-out-event", checkForChange,data,path)
  self.connect("activate", checkForChange,None,data,path)
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
    icon = gtk.Image()
    icon.set_from_file("img/person.png")
  if cat == 'l':
    icon = gtk.Image()
    icon.set_from_file("img/place.png")
  if cat == 'c':
    icon = gtk.Image()
    icon.set_from_file("img/city.png")
  if cat == 's':
    icon = gtk.Image()
    icon.set_from_file("img/state.png")
  if cat == 'o':
    icon = gtk.Image()
    icon.set_from_file("img/org.png")
  if cat == 'i':
    icon = gtk.Image()
    icon.set_from_file("img/item.png")
  row = gtk.HBox()
  label = gtk.Label(text)
  image = None
  if icon:
    image = icon
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

def addLoadSubmenuItem(lm, num):
  itemMore = gtk.MenuItem(str(num) + " _More",True)
  lm.append(itemMore)
  itemMore.show()
  molo = gtk.Menu()
  molo.show()
  itemMore.set_submenu(molo)
  return molo

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

