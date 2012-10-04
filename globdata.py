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
defaults = {}
mainWin = gtk.Window(gtk.WINDOW_TOPLEVEL)
rlmkeys = ["agedate","centbreak","century","datestyle","defaultstory","dtddir","dtdurl","familyfirst",
  "hideage","informat","outformat","printemptyXMLtags","realmdir","realmname",
  "showstories","specialrelsonly","uselistfile","usemiddle","xslurl"]
cfgkeys = ["altcolor","debug","duplicatetabs","matchlike","pos","loadrealm","rlmincfg",
  "savecolor","saverealm","seenfirstrun","size","startnewperson","termcolors"]
version = "0.90.10"
