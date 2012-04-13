#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

import pygtk
pygtk.require('2.0')
import gtk

from debug import printPretty
from common import (scrollOnTab,updateTitle,placeCalendarButton)
from globdata import (mainWin,config)
from status import status

def copyOpts(o):
  global config
  config.update(o)

def optionSetter(caller,parent = "?",canskip = True):
  global config
  global status
  options = {}
  factor = 0.80
  if parent == "?":
    parent = mainWin
    print "parent: %s" % parent
  title = "Setting Options"
  optbox = gtk.Dialog(title,parent,gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_APPLY,gtk.RESPONSE_APPLY,gtk.STOCK_OK,gtk.RESPONSE_OK))
  if not canskip: optbox.get_action_area().get_children()[2].set_sensitive(False) # buttons seem to number right to left
  if not config.get("nowindowstore"):
    optbox.set_geometry_hints(None,int(config['size'][0] * factor),int(config['size'][1] * (factor - 0.05)))
#  optbox.set_decorated(False)
  sw = gtk.VBox()
  sw.show()
  sw.set_border_width(10)
  scroll = gtk.ScrolledWindow()
  scroll.show()
  scroll.set_policy(gtk.POLICY_NEVER,gtk.POLICY_AUTOMATIC)
  scroll.add_with_viewport(sw)
  optbox.vbox.add(scroll)
  label = gtk.Label("Realm-specific Options for %s" % config['realmfile'])
  label.show()
  sw.pack_start(label,False,False,7)
  row = gtk.HBox()
  label = gtk.Label("Name of this realm/setting/world: ")
  e = gtk.Entry()
  e.show()
  e.set_text(config.get("realmname","Unnamed Realm"))
  optbox.set_title("Setting Options - %s" % e.get_text())
  e.connect("changed",setOpt,None,options,"realmname",2)
  e.connect("focus-in-event",scrollOnTab,scroll)
  row.show()
  label.show()
  row.pack_start(label,False,False,2)
  row.pack_start(e,True,True,2)
  sw.pack_start(row)
  row = gtk.HBox()
  label = gtk.Label("Realm Directory: ")
  e = gtk.Entry()
  e.show()
  e.set_text(config.get("realmdir",""))
  e.connect("changed",setOpt,None,options,"realmdir",2)
  e.connect("focus-in-event",scrollOnTab,scroll)
  row.show()
  label.show()
  row.pack_start(label,False,False,2)
  row.pack_start(e,True,True,2)
  sw.pack_start(row)
  cb = gtk.CheckButton("Family name comes first (Eastern style names)")
  cb.set_active(config.get("familyfirst",False))
  cb.connect("toggled",setOpt,None,options,"familyfirst",1)
  cb.connect("focus-in-event",scrollOnTab,scroll)
  cb.show()
  sw.pack_start(cb)
  cb = gtk.CheckButton("Use middle/maiden names")
  cb.set_active(config.get("usemiddle",True))
  cb.connect("toggled",setOpt,None,options,"usemiddle",1)
  cb.connect("focus-in-event",scrollOnTab,scroll)
  cb.show()
  sw.pack_start(cb)

  sqlbox = gtk.Frame("SQL Options")
  xmlbox = gtk.Frame("XML Options")
  formats = ["xml","sql"]
  forms = [("informat","Input format"),("outformat","Output format")]
  for key in forms:
    label = key[1]
    key = key[0]
    group = None
    row = gtk.HBox()
    row.show()
    label = gtk.Label("%s:" % label)
    label.show()
    row.pack_start(label,False,False,2)
    c = gtk.combo_box_new_text()
    selected = -1
    options[key] = config.get(key,"xml")
    i = 0
    for f in formats:
      if f == options.get(key): selected = i
      c.append_text(f)
      i += 1
    c.set_active(selected)
    c.connect("changed",setOpt,None,options,key,3)
    c.connect("changed",toggleBoxes,None,sqlbox,xmlbox,options)
    c.connect("move-active",setOpt,options,key,3)
    c.connect("move-active",toggleBoxes,sqlbox,xmlbox,options)
    c.connect("focus",scrollOnTab,scroll)
    c.connect("focus-in-event",scrollOnTab,scroll)
    c.show()
    row.pack_start(c,False,False,2)
    sw.pack_start(row)
  sw.pack_start(sqlbox)
  sw.pack_start(xmlbox)
  toggleBoxes(None,None,sqlbox,xmlbox,options)
  xb = gtk.VBox()
  xb.show()
  xmlbox.add(xb)
  sb = gtk.VBox()
  sb.show()
  sqlbox.add(sb)
####### SQL box options
  label = gtk.Label("SQL input/output is not yet implemented.\nPlease use XML for the time being.")
  label.show()
  sb.pack_start(label)
####### XML box options
  cb = gtk.CheckButton("Include empty tags when saving XML files")
  cb.set_active(config.get("printemptyXMLtags",False))
  cb.connect("toggled",setOpt,None,options,"printemptyXMLtags",1)
  cb.connect("focus-in-event",scrollOnTab,scroll)
  cb.show()
  xb.pack_start(cb)
  row = gtk.HBox()
  label = gtk.Label("DTDs are found in this directory: ")
  e = gtk.Entry()
  e.show()
  e.set_text(config.get("dtddir",""))
  e.connect("changed",setOpt,None,options,"dtddir",2)
  e.connect("focus-in-event",scrollOnTab,scroll)
  row.show()
  label.show()
  row.pack_start(label,False,False,2)
  row.pack_start(e,True,True,2)
  xb.pack_start(row)
  row = gtk.HBox()
  label = gtk.Label("URL for DTD in XML files: ")
  e = gtk.Entry()
  e.show()
  e.set_text(config.get("dtdurl",""))
  e.connect("changed",setOpt,None,options,"dtdurl",2)
  e.connect("focus-in-event",scrollOnTab,scroll)
  row.show()
  label.show()
  row.pack_start(label,False,False,2)
  row.pack_start(e,True,True,2)
  xb.pack_start(row)
  row = gtk.HBox()
  label = gtk.Label("URL for XSL files in XML: ")
  e = gtk.Entry()
  e.show()
  e.set_text(config.get("xslurl",""))
  e.connect("changed",setOpt,None,options,"xslurl",2)
  e.connect("focus-in-event",scrollOnTab,scroll)
  row.show()
  label.show()
  row.pack_start(label,False,False,2)
  row.pack_start(e,True,True,2)
  xb.pack_start(row)
  row = gtk.HBox()
  label = gtk.Label("Century assumed for 2-digit years: ")
  test = gtk.Label("Test dates:")
  test.show()
  a = gtk.Adjustment(int(config.get("century",1900)/100),-499,500)
  s1 = gtk.SpinButton(a,1.0,0)
  s1.set_increments(1,10)
  s1.show()
  s1.connect("value-changed",setOpt,None,options,"century",5)
  s1.connect("focus-in-event",scrollOnTab,scroll)
  row.show()
  label.show()
  row.pack_start(label,False,False,2)
  row.pack_start(s1,False,False,2)
  label = gtk.Label("Split year: ")
  label.show()
  a = gtk.Adjustment(int(config.get("centbreak",77)),0,99)
  s2 = gtk.SpinButton(a,1.0,0)
  s2.set_increments(1,10)
  s2.show()
  s2.connect("value-changed",setOpt,None,options,"centbreak",4)
  s2.connect("focus-in-event",scrollOnTab,scroll)
  row.pack_start(label,False,False,2)
  row.pack_start(s2,True,True,2)
  setDates(None,s1,s2,test)
  s2.connect("value-changed",setDates,s1,s2,test)
  s1.connect("value-changed",setDates,s1,s2,test)
  sw.pack_start(row)
  sw.pack_start(test,True,True,2)

  cb = gtk.CheckButton("Show only calculated date")
  cb.set_active(config.get("hideage",True))
  cb.connect("toggled",setOpt,None,options,"hideage",1)
  cb.connect("focus-in-event",scrollOnTab,scroll)
  cb.show()
  sw.pack_start(cb)
  row = gtk.HBox()
  label = gtk.Label("Date for age calculations: ")
  label.show()
  e = gtk.Entry()
  e.set_text(config.get("agedate","06/08/10b"))
  e.connect("changed",setOpt,None,options,"agedate",2)
  e.show()
  row.show()
  row.pack_start(label,0,0,2)
  row.pack_start(e,1,1,2)
  placeCalendarButton(None,row,e,None,nomark=True)
  sw.pack_start(row,0,0,2)
  row = gtk.HBox()
  label = gtk.Label("Expert: Style for dates in this realm: ")
  e = gtk.Entry()
  e.show()
  e.set_text(config.get("datestyle","%y/%m/%db"))
  e.connect("changed",setOpt,None,options,"datestyle",2)
  e.connect("focus-in-event",scrollOnTab,scroll)
  row.show()
  label.show()
  row.pack_start(label,False,False,2)
  row.pack_start(e,True,True,2)
  sw.pack_start(row)
  cb = gtk.CheckButton("Use list files for this realm")
  cb.set_active(config.get("uselistfile",True))
  cb.connect("toggled",setOpt,None,options,"uselistfile",1)
  cb.connect("focus-in-event",scrollOnTab,scroll)
  cb.show()
  sw.pack_start(cb)
  cb = gtk.CheckButton("Use only realm-defined relationships, not free text")
  cb.set_active(config.get("uselistfile",True))
  cb.connect("toggled",setOpt,None,options,"uselistfile",1)
  cb.connect("focus-in-event",scrollOnTab,scroll)
  cb.show()
  sw.pack_start(cb)
  cb = gtk.CheckButton("Use list files for this realm")
  cb.set_active(config.get("uselistfile",True))
  row = gtk.HBox()
  row.show()
  label = gtk.Label("Story List Format:")
  label.show()
  row.pack_start(label,False,False,2)
  c = gtk.combo_box_new_text()
  selected = -1
  options["showstories"] = config.get("showstories","idlist")
  i = 0
  formats = ["idlist","titlelist"]
  for f in formats:
    if f == options.get("showstories"): selected = i
    c.append_text(f)
    i += 1
  c.set_active(selected)
  c.connect("changed",setOpt,None,options,"showstories",3)
  c.connect("move-active",setOpt,options,"showstories",3)
  c.connect("focus",scrollOnTab,scroll)
  c.connect("focus-in-event",scrollOnTab,scroll)
  c.show()
  row.pack_start(c,False,False,2)
  sw.pack_start(row)

####### >>>>>>>

  label = gtk.Label("Program-wide Options")
  label.show()
  sw.pack_start(label,False,False,7)

  cb = gtk.CheckButton("Don't store window size/position")
  cb.set_active(config.get("nowindowstore",False))
  cb.connect("toggled",setOpt,None,options,"nowindowstore",1)
  cb.connect("focus-in-event",scrollOnTab,scroll)
  cb.show()
  sw.pack_start(cb)
  cb = gtk.CheckButton("Accept realm-specific options in the config file")
  cb.set_active(config.get("rlmincfg",False))
  cb.connect("toggled",setOpt,None,options,"rlmincfg",1)
  cb.connect("focus-in-event",scrollOnTab,scroll)
  cb.show()
  sw.pack_start(cb)
  cb = gtk.CheckButton("Opening a new person file at startup")
  cb.set_active(config.get("startnewperson",False))
  cb.connect("toggled",setOpt,None,options,"startnewperson",1)
  cb.connect("focus-in-event",scrollOnTab,scroll)
  cb.show()
  sw.pack_start(cb)
  cb = gtk.CheckButton("Allow opening duplicate tabs")
  cb.set_active(config.get("duplicatetabs",False))
  cb.connect("toggled",setOpt,None,options,"duplicatetabs",1)
  cb.connect("focus-in-event",scrollOnTab,scroll)
  cb.show()
  sw.pack_start(cb)
  cb = gtk.CheckButton("Save the active realm file on exit")
  cb.set_active(config.get("saverealm",False))
  cb.connect("toggled",setOpt,None,options,"saverealm",1)
  cb.connect("focus-in-event",scrollOnTab,scroll)
  cb.show()
  sw.pack_start(cb)
  row = gtk.HBox()
  row.show()
  label = gtk.Label("Likerealm handling:")
  label.show()
  row.pack_start(label,False,False,2)
  c = gtk.combo_box_new_text()
  selected = -1
  options["matchlike"] = config.get("matchlike",2)
  i = 0
  formats = ["Keep likerealm and track which options are from where","Keep likerealm and save only options that differ","Save all options and omit likerealm"]
  for f in formats:
    if i == options.get("matchlike"): selected = i
    c.append_text(f)
    i += 1
  if selected != -1:
    c.set_active(selected)
  c.connect("changed",setOpt,None,options,"matchlike",1)
  c.connect("move-active",setOpt,options,"matchlike",1)
  c.connect("focus",scrollOnTab,scroll)
  c.connect("focus-in-event",scrollOnTab,scroll)
  c.show()
  row.pack_start(c,False,False,2)
  sw.pack_start(row)
  resp = 0
  while resp not in [-6,-5]:
    resp = optbox.run()
    if resp == -10:
      t = "Options applied."
      print t
      status.push(0,t)
      printPretty(options)
      copyOpts(options)
      if options.get("realmname") is not None: updateTitle()
      options = {}
      optbox.set_title("Setting Options - %s" % config.get("realmname","Unnamed Realm"))
    if resp == -6:
      t = "Cancelled"
      print t
      status.push(0,t)
      optbox.destroy()
      return
    elif resp == -5:
      t = "Options accepted."
      print t
      status.push(0,t)
      printPretty(options)
      optbox.destroy()
      copyOpts(options)
      if options.get("realmname") is not None: updateTitle()
#  saveConfig()
#  saveRealm()
  return

def setOpt(self,event,d = {},key = None,t = 1):
  if key == None: return
  if t == 1:
    d[key] = self.get_active()
  if t == 2:
    d[key] = self.get_text()
  if t == 3:
    d[key] = self.get_active_text()
  if t == 4:
    d[key] = self.get_value_as_int()
  if t == 5:
    d[key] = self.get_value_as_int() * 100

def toggleBoxes(self,event,sbox,xbox,o = {}):
  if o.get("informat") == "xml" or o.get("outformat") == "xml":
    xbox.show()
  else:
    xbox.hide()
  if o.get("informat") == "sql" or o.get("outformat") == "sql":
    sbox.show()
  else:
    sbox.hide()


def setDates(caller,acw,cbw,ow):
  out = "Test dates: "
  a = cbw.get_value_as_int()
  b = a - 1
  if b < 0: b += 100
  c = str(a)
  d = str(b)
  if len(c) == 1: c = "0%s" % c
  if len(d) == 1: d = "0%s" % d
  e = str(acw.get_value_as_int())
  x = 1
  if a == 0: x = 0
  if a < 0: x = -1
  f = str(acw.get_value_as_int() - x)
  out += "%s = %s%s\t" % (d,e,d)
  out += "%s = %s%s\t" % (c,f,c)
  ow.set_text(out)
