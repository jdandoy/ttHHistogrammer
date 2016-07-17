#!/usr/bin/env python

###########################################################
# reweightTrees.py                                        #
# A short script to reweight TTrees by their initial      #
# event number.  Allows for directly combining TTrees.    #
# For more information contact Jeff.Dandoy@cern.ch        #
###########################################################

import glob, array, argparse
##put argparse before ROOT call.  This allows for argparse help options to be printed properly (otherwise pyroot hijacks --help) and allows -b option to be forwarded to pyroot
#parser = argparse.ArgumentParser(description="%prog [options]", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
#parser.add_argument("--pathToTrees", dest='pathToTrees', default="./gridOutput/tree", help="Path to the input trees")
#parser.add_argument("--treeName", dest='treeName', default="outTree", help="Name of trees to be reweighted")
#
#args = parser.parse_args()


from ROOT import *

def splitTrees():
  treeName = "nominal"
  fileName = "user.nasbah.mc15_13TeV.410000.ttbar_hdamp172p5_nonallhad.Gradient_20160121_output.root"
  values = [0, 4, 5]
  outputName = ["L", "C", "B"]
#  values = [0]
#  outputName = ["L"]

  inFile = TFile.Open(fileName, "READ")
  tree = inFile.Get( treeName )
  TopFlag = array.array('i', [0])
  tree.SetBranchAddress("TopHeavyFlavorFilterFlag", TopFlag)

  for iV,value in enumerate(values):
    outFile = TFile.Open(fileName.replace('ttbar','ttbar_'+outputName[iV]), "RECREATE" )
    newTree = tree.CloneTree(0)

    i = 0
    maxEvents = 10000
    print "Running over ", tree.GetEntries()
    while tree.GetEntry(i):
#      if i > maxEvents:
#        break
      if (i%10000) == 0:
        print i
      i += 1
      if (TopFlag[0] != value):
        continue
      newTree.Fill()

    outFile.Write()
#    newTree.SetDirectory( outFile )
    sumWeightsTree = inFile.Get( "sumWeights" )
    outFile.cd()
    sumWeightsTree.CloneTree().Write()
#    sumWeightsTree.SetDirectory( outFile )
#    newTree.Write("", TObject.kOverwrite)
#    sumWeightsTree.Write("", TObject.kOverwrite)
    outFile.Close()

  inFile.Close()


if __name__ == "__main__":
  splitTrees()
  print "Finished splitTrees()"
