#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

from backends import (config,readfile,writefile)
import os

stories = {}
relsP = {}

def allGenders(order = 0):
  # TODO: Gender editor/config file, where user can define sci-fi genders, etc.
  genders = {'M':"Male",'F':"Female",'N':"Unknown"}
  if order == 1:
    gendercodes = {}
    for key in genders.keys():
      gendercodes[genders[key]] = key
    return gendercodes
  else:
    return genders

def getRelsP(pgender = 'N',rgender = 'N'):
  global relsP
  if not len(relsP):
    print "Loading people relations for the first time."
#    relsP = loadRelsP() # backends.loadRelsP()
#    r = ConfigOb(os.path.abspath("peopleconnections.ini"))
# TODO: INI file import
    # Some day, pull these values from a backend
    relsP['relsNN'] = { # [relation,autoreverse,rtype,required pairgenders,is reciprocal,reverse's key]
      '101':['Friend','Friend','friend',"NN"],
      '102':['Boss',"Subordinate",'work',"NN",True,'103'],
      '103':['Subordinate','Boss','work',"NN",True,'102'],
      '104':['Running Partner','Running Partner','casual',"NN"],
      '105':['Sibling','Sibling','fam',"NN"],
      '106':['Cousin','Cousin','fam',"NN"],
    }
    relsP['relsNF'] = {
'107':['Sister','Sibling','fam',"NF"],
'108':['Mother','Child','fam',"NF"],
'109':['Sister-in-law','Sibling-in-law','fam',"NF"],
'110':['Mother-in-law','Child-in-law','fam',"NF"],
'111':['Stepsister','Stepsibling','fam',"NF"],
'112':['Stepmother','Stepchild','fam',"NF"],
    }
    relsP['relsNM'] = {
'113':['Brother','Sibling','fam',"NM"],
'114':['Father','Child','fam',"NM"],
'115':['Brother-in-law','Sibling-in-law','fam',"NM"],
'116':['Father-in-law','Child-in-law','fam',"NM"],
'117':['Stepbrother','Stepsibling','fam',"NM"],
'118':['Stepfather','Stepchild','fam',"NM"],
    }
    relsP['relsMF'] = {
'119':['Lover','Lover','other',"MF"],
'120':['Wife','Husband','fam',"MF"],
'121':['Sister','Brother','fam',"MF"],
'122':['Mother','Son','fam',"MF"],
'123':['Sister-in-law','Brother-in-law','fam',"MF"],
'124':['Mother-in-law','Son-in-law','fam',"MF"],
'125':['Stepsister','Stepbrother','fam',"MF"],
'126':['Stepmother','Stepson','fam',"MF"],
    }
    relsP['relsFM'] = {
'127':['Lover','Lover','other',"FM"],
'128':['Husband','Wife','fam',"FM"],
'129':['Brother','Sister','fam',"FM"],
'130':['Father','Daughter','fam',"FM"],
'131':['Brother-in-law','Sister-in-law','fam',"FM"],
'132':['Father-in-law','Daughter-in-law','fam',"FM"],
'133':['Stepbrother','Stepsister','fam',"FM"],
'134':['Stepfather','Stepdaughter','fam',"FM"],
    }
    relsP['relsFF'] = {
'135':['Sister','Sister','fam',"FF"],
'136':['Mother','Daughter','fam',"FF"],
'137':['Sister-in-law','Sister-in-law','fam',"FF"],
'138':['Mother-in-law','Daughter-in-law','fam',"FF"],
'139':['Stepsister','Stepsister','fam',"FF"],
'140':['Stepmother','Stepdaughter','fam',"FF"],
    }
    relsP['relsMM'] = {
'141':['Brother','Brother','fam',"MM"],
'142':['Father','Son','fam',"MM"],
'143':['Brother-in-law','Brother-in-law','fam',"MM"],
'144':['Father-in-law','Son-in-law','fam',"MM"],
'145':['Stepbrother','Stepbrother','fam',"MM"],
'146':['Stepfather','Stepson','fam',"MM"],
    }
  listtype = "rels" + pgender.upper() + rgender.upper()
  return relsP[listtype]

def myStories(worlddir):
  global stories
  if len(stories) > 0:
    return stories
  else:
    fn = os.path.join(os.path.abspath(worlddir),"mystories.cfg")
    lines = readfile(fn,False) # Try to read file, but quietly
    for line in lines:
      try:
        line = line.strip()
        if line:
          values = [x.strip() for x in line.split('=')]
          if not stories.get(values[0]): stories[values[0]] = values[1] # existing options will not be clobbered
      except Exception as e:
        print "There was an error in the configuration file: %s" % e
    return stories

def saveStories(worlddir):
  worlddir = os.path.abspath(worlddir)
  if os.path.exists(worlddir):
    lines = []
    for key in stories:
      lines.append("%s = %s\n" % (key,stories[key]))
    if config['debug'] > 3: print lines
    fn = os.path.join(worlddir,"mystories.cfg")
    writefile(fn,lines,True)
  else:
    bsay(None,"The path %s does not exist.")