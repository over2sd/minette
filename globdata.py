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
orgs = {}
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
rlmkeys = ["agedate","centbreak","century","datestyle","dtddir","dtdurl","familyfirst",
  "hideage","informat","outformat","printemptyXMLtags","realmdir","realmname",
  "showstories","specialrelsonly","uselistfile","usemiddle","xslurl"]
cfgkeys = ["debug","pos","duplicatetabs","realmfile","seenfirstrun","size",
  "startnewperson","termcolors","saverealm","rlmincfg"]
version = "0.90"
