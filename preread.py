#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

from globdata import (cities,people,places,printStack)
from common import preRead

def preReadc(force,path,depth = 0,retries = 0):
  printStack(1)
  print "\t!!!\tUsing deprecated function\t!!!"
  return preRead(force,'c',path,depth,retries)

def preReadl(force,path,depth = 0,retries = 0):
  printStack(1)
  print "\t!!!\tUsing deprecated function\t!!!"
  return preRead(force,'l',path,depth,retries)

def preReadp(force,path,depth = 0,retries = 0):
  printStack(1)
  print "\t!!!\tUsing deprecated function\t!!!"
  return preRead(force,'p',path,depth,retries)
