from backends import getRelsP

def getPersonConnections(cat,rgender = 'n',pgender = 'n'): # More likely to need relation's gender than person's
  d = {}
  if cat == "person":
    relsnn = getRelsP('n','n')
    relsnf = getRelsP('n','f')
    relsnm = getRelsP('n','m')
    relsmf = getRelsP('m','f')
    relsfm = getRelsP('f','m')
    relsff = getRelsP('f','f')
    relsmm = getRelsP('m','m')
    d.update(relsnn)
### For now, let it be dumb.
    if True:
#    if pgender == 'n' and rgender == 'f':
      d.update(relsnf)
#    elif pgender == 'f' and rgender == 'f':
      d.update(relsff)
#    elif pgender == 'm' and rgender == 'f':
      d.update(relsmf)
#    elif pgender == 'n' and rgender == 'm':
      d.update(relsnm)
#    elif pgender == 'f' and rgender == 'm':
      d.update(relsfm)
#    elif pgender == 'm' and rgender == 'm':
      d.update(relsmm)
#  elif cat == "place":
#  elif cat == "city":
#  elif cat == "state":
#  elif cat == "item":
#  elif cat == "animal":
  return d

