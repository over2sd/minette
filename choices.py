#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

import backends
from globdata import (config,stories,relsP,relsL)
import os

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

def getRelsL(cat):
  global relsL
  if not len(relsL):
    print "Loading place relations for the first time."
#    relsL = loadRelsL() # backends.loadRelsL()
#    r = ConfigOb(os.path.abspath("placeeconnections.ini"))
# TODO: INI file import
    # Some day, pull these values from a backend
    relsL['relsLL'] = { # [relation,autoreverse,rtype,required pairgenders,is reciprocal,reverse's key]
'171':['Branch Office','Main Office','place','LL'],
'172':['Main Office','Branch Office','place','LL'],
'173':['Sister Business','Sister Business','place','LL'],
'174':['Property','Management Agency','place','LL'],
    }
    relsL['relsLP'] = { # [relation,autoreverse,rtype,required pairgenders,is reciprocal,reverse's key]
'159':['Owner','Home','fam','LP'],
'160':['Owner','Business','empl','LP'],
'161':['Manager','Workplace','empl','LP'],
'162':['Employee','Workplace','empl','LP'],
'163':['Regular','Hangout','pat','LP'],
'164':['Patron','Hangout','pat','LP'],
'165':['Heir','Home','fam','LP'],
'166':['Resident','Home','fam','LP'],
'167':['Heir','Business','fam','LP'],
'168':['Inmate','Captivity','other','LP'],
'169':['Resident','Residence','pat','LP'],
'170':['Member','Institution','pat','LP'],
    }
  listtype = "relsL" + cat.upper()
  return relsL[listtype]

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
    relsP['relsNL'] = { # [relation,autoreverse,rtype,required pairgenders,is reciprocal,reverse's key]
'147':['Home','Owner','NL'],
'148':['Business','Owner','NL'],
'149':['Workplace','Manager','NL'],
'150':['Workplace','Employee','NL'],
'151':['Hangout','Regular','NL'],
'152':['Hangout','Patron','NL'],
'153':['Home','Heir','NL'],
'154':['Home','Resident','NL'],
'155':['Business','Heir','NL'],
'156':['Captivity','Inmate','NL'],
'157':['Residence','Resident','NL'],
'158':['Institution','Member','NL'],
    }
  listtype = "rels" + pgender.upper() + rgender.upper()
  return relsP[listtype]

def myStories(realmdir):
  global stories
  if len(stories) > 0:
    return stories
  else:
    fn = os.path.join(os.path.abspath(realmdir),"mystories.cfg")
    lines = backends.readfile(fn,False) # Try to read file, but quietly
    for line in lines:
      try:
        line = line.strip()
        if line:
          values = [x.strip() for x in line.split('=')]
          if not stories.get(values[0]): stories[values[0]] = values[1] # existing options will not be clobbered
      except Exception as e:
        print "There was an error in the configuration file: %s" % e
    return stories

def saveStories(realmdir):
  realmdir = os.path.abspath(realmdir)
  if os.path.exists(realmdir):
    lines = []
    for key in stories:
      lines.append("%s = %s\n" % (key,stories[key]))
    if config['debug'] > 3: print lines
    fn = os.path.join(realmdir,"mystories.cfg")
    backends.writefile(fn,lines,True)
  else:
    bsay(None,"The path %s does not exist.")
