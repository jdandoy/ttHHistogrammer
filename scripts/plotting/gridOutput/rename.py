import glob, os

files = glob.glob("output.root/*")

for file in files:
  if "physics_Main" in file:
    continue
  did = (file.split('.')[3])
  with open('Samples.txt', 'r') as newNameFile:
    for line in newNameFile:
      if did in line:
        otherName = line
        break
  newName = '.'.join( (file.split('.')[0:3]+otherName.split('.')[0:1]+file.split('.')[3:4]+otherName.split('.')[2:3])+file.split('.')[-2:] )
  print "file",file
  print "otherName",otherName
  print "newName",newName

  os.system("mv "+file+" "+newName)
