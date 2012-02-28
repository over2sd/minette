import pygtk
pygtk.require('2.0')
import gtk

from choices import getRelsP
from common import askBoxProcessor
from globdata import worldList

def getPersonConnections(cat,rgender = 'N',pgender = 'N'): # More likely to need relation's gender than person's
  d = {}
  if cat == "person":
    relsNN = getRelsP('N','N')
    relspr = getRelsP(pgender,rgender)
    d.update(relsNN)
    if pgender != 'N' or rgender != 'N':
      d.update(relspr)
#  elif cat == "place":
#  elif cat == "city":
#  elif cat == "state":
#  elif cat == "item":
#  elif cat == "animal":
  return d

def recordSelectBox(parent,fileid,title = "Select Record"):
  global worldList
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
  sepnames = {'p':("People","person"),'l':("Places","place"),'c':("Cities","city"),'s':("States","state"),'i':("Items","item")}
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
          button.connect("clicked",askBoxProcessor,askbox,rid)
          col.pack_start(button)
  width, height = askbox.get_size()
  askbox.move((gtk.gdk.screen_width() / 2) - (width / 2),(gtk.gdk.screen_height() / 2) - (height / 2))
  answers['86'] = ""
  answer = askbox.run()
  askbox.destroy()
  if answer < 0: answer = 86
  return answers[str(answer)]

