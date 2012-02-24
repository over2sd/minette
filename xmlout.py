#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

import xml.etree.ElementTree as etree
from backends import config

def wrapelement(tag,text,tabs,attr = None):
  aname = None
  aval = None
  if text is None: text = ""
  if attr:
   try:
    (aname,aval) = attr # Expecting a tuple
   except ValueError:
    print "Bad attribute encountered: %s. Returning tag without attribbute." % attr
  out = ""
  i = tabs
  while i > 0:
    out += '\t'
    i -= 1
  if len(text) and text[-1] == "\n":
    i = tabs
    while i > 0:
      text += '\t'
      i -= 1

  if len(text) and aname is None:
    out += "<%s>%s</%s>\n" % (tag,text,tag)
  elif len(text) and aname is not None:
    out += "<%s %s=\"%s\">%s</%s>\n" % (tag,aname,aval,text,tag)
  elif not len(text) and aname is not None:
    out += "<%s %s=\"%s\" />\n" % (tag,aname,aval)
  else:
    out += "<%s />\n" % tag
  return out

def prettyXML(root):
  global config
  out = "\n"
  for i in range(len(root)):
    if root[i].tag is not None:
      if root[i].tag == "relat" or root[i].tag == "formocc" or root[i].tag == "currocc":
        specialtext = "\n"
        for j in root[i]:
          if j.tag == "events":
            etext = "\n"
            for k in j:
              mtext = "\n"
              for m in k:
                if config['printemptyXMLtags'] or len(m.text) > 0:
                  mtext += wrapelement(m.tag,m.text,4)
              if config['printemptyXMLtags'] or len(mtext) > 2:
                etext += wrapelement(k.tag,mtext,3)
            if config['printemptyXMLtags'] or len(etext) > 2:
              specialtext += wrapelement(j.tag,etext,2)
          elif config['printemptyXMLtags'] or len(j.text) > 2:
            specialtext += wrapelement(j.tag,j.text,2)
        if config['printemptyXMLtags'] or len(specialtext) > 2:
          out += wrapelement(root[i].tag,specialtext,1)
      elif len(root[i].text) > 0:
        out += wrapelement(root[i].tag,root[i].text,1)
      elif config['printemptyXMLtags']:
        out += wrapelement(root[i].tag,'',1)
  return wrapelement(root.tag,out,0)
