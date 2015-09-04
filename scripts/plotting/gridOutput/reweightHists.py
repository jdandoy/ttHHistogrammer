#!/usr/bin/env python

###########################################################
# reweightTrees.py                                        #
# A short script to reweight TTrees by their initial      #
# event number.  Allows for directly combining TTrees.    #
# For more information contact Jeff.Dandoy@cern.ch        #
###########################################################

import glob, array, argparse, os
#put argparse before ROOT call.  This allows for argparse help options to be printed properly (otherwise pyroot hijacks --help) and allows -b option to be forwarded to pyroot
parser = argparse.ArgumentParser(description="%prog [options]", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
#parser.add_argument("--pathToFiles", dest='pathToFiles', default="tmpDir/", help="Path to the input hists")
parser.add_argument("--pathToFiles", dest='pathToFiles', default="output.root/", help="Path to the input hists")
parser.add_argument("--XSFile", dest='XSFile', default="XS_Samples.txt", help="XSFile for corrections")
parser.add_argument("--dirName", dest='dirName', default="mu_jets", help="Name of hist dir to be reweighted")

args = parser.parse_args()

from ROOT import *

def reweightTrees():
  files = glob.glob(args.pathToFiles+"/user*.root")
  files = [file for file in files if not "Main" in file]

  for file in files:

    print "Reweighting file ", file

    inFile = TFile.Open(file, "READ")
    inDir = inFile.Get( args.dirName )

    sumWeightTree = inFile.Get("sumWeights")
    weightedSum = 0
    for event in sumWeightTree:
      weightedSum += event.totalEventsWeighted


    scaleFactor = 1./weightedSum

#    for key in inDir.GetListOfKeys():
#      if 'cutflow_mc_pu_zvtx' in key.GetName():
#        cutFlow = inDir.Get( key.GetName() )
#    if not cutFlow:
#      print "ERROR, no cutflow file found"
#      exit(1)

    #GET XS and kfactor
    ## Calculate new XS value from text file
    fileNum = os.path.basename(file).split('.')[3]
    newXS = 0
    with open(args.XSFile,'r') as XSFile:
      for line in XSFile:
        if fileNum in line:
          line = line.split()
          newXS = float(line[1])*float(line[2])
          break

    if newXS == 0:
      print "ERROR, could not find file number in ", args.XSFile
      continue

    print "Setting ", file, " XS weight to ", newXS
    scaleFactor *= newXS

    outFile = TFile.Open(os.path.dirname(file)+"/corrected_"+os.path.basename(file), "UPDATE")
    outFile.mkdir( args.dirName )
    outDir = outFile.Get( args.dirName )

    for key in inDir.GetListOfKeys():
      thisHist = inDir.Get( key.GetName() )
      if not 'cutflow' in thisHist.GetName():
        thisHist.Scale( scaleFactor )
      thisHist.SetDirectory(outDir)

    outFile.Write()

if __name__ == "__main__":
  reweightTrees()
  print "Finished reweightTrees()"
