#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

import pygtk
pygtk.require('2.0')
import gtk

from globdata import (mainWin,config)

def optionSetter(caller,parent = "?"):
  global config
  print "caller: %s" % caller
  if parent == "?":
    parent = mainWin
    print "parent: %s" % parent
  optbox = gtk.Dialog("Setting Options",parent,gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_APPLY,gtk.RESPONSE_APPLY,gtk.STOCK_OK,gtk.RESPONSE_OK))
  cb = gtk.CheckButton("Family name comes first (Eastern style names)")
  cb.set_active(config.get("familyfirst"))
#  cb.connect("")
  cb.show()
  optbox.vbox.pack_start(cb)
  cb = gtk.CheckButton("Use middle/maiden names")
  cb.set_active(config.get("usemiddle"))

  cb.show()
  optbox.vbox.pack_start(cb)
  row = gtk.HBox()
  label = gtk.Label("Realm Directory: ")
  erealmdir = gtk.Entry()
  erealmdir.show()
  row.show()
  label.show()
  row.pack_start(erealmdir)
  row.pack_start(label)
  optbox.vbox.pack_start(row)
  """
  informat
  outformat
  realmdir
  realmname
  datestyle
  century
  centbreak
  """
  resp = 0
  while resp not in [-6,-5]:
    resp = optbox.run()
    if resp == -10:
      print "!!"
  if resp == -6:
    print "Cancelled"
    optbox.destroy()
    return
  elif resp == -5:
    print "Accepted!"
    print erealmdir.get_text()
    optbox.destroy()
    return
  print "Oops"
