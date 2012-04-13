import pygtk
pygtk.require('2.0')
import gtk

from choices import (getRelsP, getRelsL)
import common
from debug import printPretty
from globdata import (worldList,mainWin,config)

def getPersonConnections(cat,rgender = 'N',pgender = 'N'): # More likely to need relation's gender than person's
  d = {}
  if cat == "person":
    relsNN = getRelsP('N','N')
    relspr = getRelsP(pgender,rgender)
    d.update(relsNN)
    if pgender != 'N' or rgender != 'N':
      d.update(relspr)
  elif cat == "place":
    rels = getRelsP('N','L')
    d.update(rels)
#  elif cat == "city":
#  elif cat == "state":
#  elif cat == "item":
#  elif cat == "animal":
  return d

def getPlaceConnections(cat):
  d = {}
  if cat == "person":
    rels = getRelsL('p')
    d.update(rels)
  return d

def listSelectBox(parent = "?",items = [],**kwargs):
  lt = 0
  rows = 20
  cannew = False
  newname = "Value"
  abort = "Cancel"
  title = ""
  for key in kwargs:
    if config['debug'] > 3: print "%s:%s" % (key,kwargs[key])
    if key == "listtype": lt = kwargs[key]
    if key == "height": rows = kwargs[key]
    if key == "allownew": cannew = kwargs[key]
    if key == "type": newname = kwargs[key]
    if key == "abort": abort = kwargs[key]
    if key == "title": title = kwargs[key]
  global mainWin
  if parent == "?": parent = mainWin
  end = len(items) + 1
  if title is None or len(title) == 0: title = "Select Record"
  askbox = gtk.Dialog(title,parent,gtk.DIALOG_DESTROY_WITH_PARENT,(abort,end))
  ilist = []
  answers = {}
  sepnames = {}
  if lt == 0:
    for i in items:
      ilist.append(["a",i,i]) # I thought I would need to make this a tuple, and I will, when I expand the function to include lists that are cat,value,descriptive triplets
    sepnames['a'] = "All"
  colbox = gtk.HBox()
  colbox.show()
  askbox.vbox.pack_start(colbox,True,True,1)
  col = gtk.VBox()
  col.show()
  colbox.pack_start(col,True,True,1)
  bound = rows
  sepcount = 0
  if cannew:
    rid = len(answers)
    answers[str(rid)] = ["","",""]
    newbut = gtk.Button("New %s" % newname)
    newbut.show()
    newbut.connect("clicked",common.askBoxProcessor,askbox,rid)
    col.pack_start(newbut)
  if True: # Placeholders for cat processing
    if True:
      if True:
        """
  for li in sepnames.keys():
    if worldList.get(li):
      count = len(worldList[li])
      if count > 0 and len(worldList[li][0]) > 0:
        sep = gtk.Label(sepnames.get(li,("Other","other"))[0])
        sep.show()
        sepcount += 1
        if len(answers) + sepcount >= bound:
          col = gtk.VBox()
          col.show()
          colbox.pack_start(col,False,False,1)
          sepcount = 1
          bound += rows
          col.pack_start(sep,True,True,1)
        """
        for value in sorted(ilist):
          if len(answers) + sepcount >= bound:
            col = gtk.VBox()
            col.show()
            colbox.pack_start(col,True,True,1)
            sepcount = 0
            bound += rows
          if len(value[1]) > 0:
            rid = len(answers)
            answers[str(rid)] = (value[0],value[1],value[2])
            button = gtk.Button(value[2])
            button.show()
            button.connect("clicked",common.askBoxProcessor,askbox,rid)
            col.pack_start(button)
  width, height = askbox.get_size()
  if len(title) > width / 10: width = (len(title) * 9 + 90)
  askbox.resize(width,height)
  askbox.move((gtk.gdk.screen_width() / 2) - (width / 2),(gtk.gdk.screen_height() / 2) - (height / 2))
  answers[str(end)] = [None,None,None]
  answer = askbox.run()
  askbox.destroy()
  if answer < 0: answer = end
  return answers[str(answer)]


def recordSelectBox(parent,fileid,title = "",fromtypes = ['l','o','p']):
  global mainWin
  if parent == "?": parent = mainWin
  global worldList
  if len(title) == 0: title = "Select Record"
  askbox = gtk.Dialog(title,parent,gtk.DIALOG_DESTROY_WITH_PARENT,("Cancel",86))
  answers = {}
  colbox = gtk.HBox()
  colbox.show()
  askbox.vbox.pack_start(colbox,True,True,1)
  col = gtk.VBox()
  col.show()
  colbox.pack_start(col,False,False,1)
  bound = 20
  sepcount = 0
  #TODO: Move these to the backends module
  sepnames = {}
  if 'p' in fromtypes: sepnames.update({'p':("People","person")})
  if 'l' in fromtypes: sepnames.update({'l':("Places","place")})
  if 'c' in fromtypes: sepnames.update({'c':("Cities","city")})
  if 'i' in fromtypes: sepnames.update({'i':("Items","item")})
  if 's' in fromtypes: sepnames.update({'s':("States","state")})
  if 'o' in fromtypes: sepnames.update({'o':("Organaizations","org")})
  for li in sepnames.keys():
    if worldList.get(li):
      count = len(worldList[li])
      if count > 0 and len(worldList[li][0]) > 0:
        sep = gtk.Label(sepnames.get(li,("Other","other"))[0])
        sep.show()
        sepcount += 1
        if len(answers) + sepcount >= bound:
          col = gtk.VBox()
          col.show()
          colbox.pack_start(col,False,False,1)
          sepcount = 1
          bound += 20
        col.pack_start(sep,True,True,1)
      for value in sorted(worldList[li]):
        if len(answers) + sepcount >= bound:
          col = gtk.VBox()
          col.show()
          colbox.pack_start(col,False,False,1)
          sepcount = 0
          bound += 20
        if value != fileid and len(value) > 0:
          rid = len(answers)
          answers[str(rid)] = (value,sepnames[li][1])
          button = gtk.Button(value)
          button.show()
          button.connect("clicked",common.askBoxProcessor,askbox,rid)
          col.pack_start(button)
  width, height = askbox.get_size()
  askbox.move((gtk.gdk.screen_width() / 2) - (width / 2),(gtk.gdk.screen_height() / 2) - (height / 2))
  answers['86'] = ""
  answer = askbox.run()
  askbox.destroy()
  if answer < 0: answer = 86
  return answers[str(answer)]

