from choices import getRelsP

def getPersonConnections(cat,rgender = 'N',pgender = 'N'): # More likely to need relation's gender than person's
  d = {}
  if cat == "person":
    relsNN = getRelsP('N','N')
    relspr = getRelsP(pgender,rgender)
    d.update(relsnn)
### For now, let it be dumb.
    if pgender != 'N' or rgender != 'N':
      d.update(relspr)
#  elif cat == "place":
#  elif cat == "city":
#  elif cat == "state":
#  elif cat == "item":
#  elif cat == "animal":
  return d

