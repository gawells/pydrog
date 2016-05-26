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

def sum_partials(sel):
  pymol.stored.partial_charges = []
  pymol.stored.names = []
  cmd.iterate("%s"%sel,"stored.partial_charges.append((name,partial_charge))")
  sum = 0
  for (name,charge) in pymol.stored.partial_charges:
    sum += charge
    print "%s %s"%(name,charge)
  print sum


def readpsf(psffile,sel,label='0'):
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

  if label == '1':
    cmd.do("stored.fftypes_tmp = stored.%s_fftypes"%objname[0]) # use tmp list that gets consumed by 'alter'
    cmd.do("label "+sel+", \"%s %1.2f %s\"%(name, partial_charge, stored.fftypes_tmp.pop())")
  elif label == '2':
    cmd.do("stored.fftypes_tmp = stored.%s_fftypes"%objname[0]) # use tmp list that gets consumed by 'alter'
    cmd.do("label "+sel+", \"%s / %s\"%(name, stored.fftypes_tmp.pop())")
  elif label == '3':
    cmd.do("stored.fftypes_tmp = stored.%s_fftypes"%objname[0]) # use tmp list that gets consumed by 'alter'
    cmd.do("label "+sel+", \"%s\"%(stored.fftypes_tmp.pop())")
  print (objname)

def label_fftype(sel):
  objname = cmd.get_object_list('%s'%sel)
  cmd.do("stored.fftypes_tmp = stored.%s_fftypes"%objname[0]) # use tmp list that gets consumed by 'alter'
  cmd.do("label "+sel+", \"%s - %s\"%(name, stored.fftypes_tmp.pop())")
  

def nohydro(model="(all)"):
   '''
DESCRIPTION

   Hide hydrogens shown as lines or sticks.

USAGE

   spikes
   spikes selection

   '''
   
   cmd.do("hide lines, %s & (hydro)"%model)
   cmd.do("hide sticks,%s & (hydro)"%model)

cmd.extend("getpartial",getpartial)
cmd.extend("readpsf",readpsf)
cmd.extend("label_fftype",label_fftype)
cmd.extend("sum_partials",sum_partials)


