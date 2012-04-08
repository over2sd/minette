#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# Global Data Structures

import pygtk
pygtk.require('2.0')
import gtk

people = {}
places = {}
cities = {}
states = {}
items = {}
animals = {}
config = {}
placeList = {}
worldList = {}
stories = {}
relsP = {}
relsL = {}
menuBar = gtk.MenuBar()
menuBar.show()
realms = {}
mainWin = gtk.Window(gtk.WINDOW_TOPLEVEL)
rlmkeys = ["realmfile","specialrelsonly","uselistfile","centbreak","century","datestyle",
  "xslurl","dtdurl","dtddir","printemptyXMLtags","informat","outformat","realmname",
  "realmdir","usemiddle","familyfirst",]
cfgkeys = ["pos","size","seenfirstrun","debug","startnewperson","openduplicatetabs",""]