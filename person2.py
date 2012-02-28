from globdata import people

def preReadp(force,path,depth = 0,retries = 0):
  """Using the global dict 'people' and given a list of keys 'path' and an integer 'depth', prepares a path
  in the target dict for reading, to a depth of 'depth'. If 'force' is True, the function will build missing
  tree branches, to allow you to write to the endpoint. Do not call force with a path/depth ending in a list,
  tuple, or something other than a dict, which this function produces. Call force on one path higher.
  """
  global people
  if depth > len(path): depth = len(path)
  if depth > 7: depth = 7
  if path[0] in people.keys():
    if depth <= 1:
      return True
    if path[1] in people[path[0]].keys():
      if depth <= 2:
        return True
      if path[2] in people[path[0]][path[1]].keys():
        if depth <= 3:
          return True
        if path[3] in people[path[0]][path[1]][path[2]].keys():
          if depth <= 4:
            return True
          if path[4] in people[path[0]][path[1]][path[2]][path[3]].keys():
            if depth <= 5:
              return True
            if path[5] in people[path[0]][path[1]][path[2]][path[3]][path[4]].keys():
              if depth <= 6:
                return True
              if path[6] in people[path[0]][path[1]][path[2]][path[3]][path[4]][path[5]].keys():
                return True # Maximum depth reached
              elif force:
                people[path[0]][path[1]][path[2]][path[3]][path[4]][path[5]][path[6]] = {}
                if retries >= depth: force = False
                return preReadp(force,path,depth,retries + 1)
              else: # Not found, and not forcing it to be found
                return False
            elif force:
              people[path[0]][path[1]][path[2]][path[3]][path[4]][path[5]] = {}
              if retries >= depth: force = False
              return preReadp(force,path,depth,retries + 1)
            else: # Not found, and not forcing it to be found
              return False
          elif force:
            people[path[0]][path[1]][path[2]][path[3]][path[4]] = {}
            if retries >= depth: force = False
            return preReadp(force,path,depth,retries + 1)
          else: # Not found, and not forcing it to be found
            return False
        elif force:
          people[path[0]][path[1]][path[2]][path[3]] = {}
          if retries >= depth: force = False
          return preReadp(force,path,depth,retries + 1)
        else: # Not found, and not forcing it to be found
          return False
      elif force:
        people[path[0]][path[1]][path[2]] = {}
        if retries >= depth: force = False
        return preReadp(force,path,depth,retries + 1)
      else: # Not found, and not forcing it to be found
        return False
    elif force:
      people[path[0]][path[1]] = {}
      if retries >= depth: force = False
      return preReadp(force,path,depth,retries + 1)
    else: # Not found, and not forcing it to be found
      return False
  else: # First level (fileid) can't be generated.
    return False

