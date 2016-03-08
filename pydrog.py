def getpartial(file,sel):
  '''
  Get partial charges from file. Must be in same order as external ids
  '''
  
   charges = open(file).read()
   chargearray = charges.split()
   cmd.do("print %s"%chargearray)
   i = 1
   for fx in chargearray:
      cmd.do("print %s"%fx)
      cmd.do("alter (id %s) and (%s), partial_charge=%s"%(i,sel,fx))
      i += 1



def readpsf(psffile,sel,label=False):
  '''
  Read partial charges and atom-types from a .psf topology file. 
  Atom types are stored in 'stored.<objectname>_fftyes'. If label 
  is True atoms are labelled as "atom_name partial_charge ff_type"

  '''
  infile = open(psffile,'r')
  atom_section = re.compile('NATOM')
  bond_section = re.compile('NBOND')
  found = False  
  partial_charges = []
  atom_fftypes = []

  #get names of objects corresponding to "sel", only first will be used
  objname = cmd.get_object_list('%s'%sel)

  # populate partial charge and atom type lists
  for line in infile:
    if atom_section.search(line):
      found = True            
      continue
    
    if found:
      line_arr = line.strip().split()      
      if len(line_arr) == 9:
        atom_fftypes.append(line_arr[5])
        partial_charges.append(line_arr[6])

      if bond_section.search(line):
        found = False

  # set partial charges in "sel" and atom types in corresponding "stored" object
  i = 1
  cmd.do("stored.%s_fftypes = []"%objname[0])
  for fx in partial_charges:
    cmd.do("alter (id %s) and (%s), partial_charge=%s"%(i,sel,fx))
    cmd.do("stored.%s_fftypes.append(\"%s\")"%(objname[0],atom_fftypes[i-1]))
    i += 1
  # reverse list since "alter" must consume elements from "stored" objects
  cmd.do("stored.%s_fftypes.reverse()"%objname[0])

  if label:
    cmd.do("stored.fftypes_tmp = stored.%s_fftypes"%objname[0]) # use tmp list that gets consumed by 'alter'
    cmd.do("label "+sel+", \"%s %1.2f %s\"%(name, partial_charge, stored.fftypes_tmp.pop())")
