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
  treeName = "nominal_Loose"
  fileName = "user.nasbah.data15_13TeV.00280862.physics_Main.Gradient_20160208_output.root"
  #6times 9 for the new run number
  inFile = TFile.Open(fileName, "READ")
  tree = inFile.Get( treeName )
  newWeight = array.array('f', [0])
  tree.SetBranchAddress("fakesMM_weight_ejets_nominal", newWeight)

  newFileName = fileName.replace('Main','Main_Fake').replace('data15','fake15')
  outFile = TFile.Open(newFileName, "RECREATE" )
  newTree = tree.CloneTree(0) #strat with a new tree 
  newTree.SetName("nominal")

  #eventWeight *= weight_mc*weight_pileup*weight_leptonSF*weight_bTagSF
  weight_mc = array.array('f', [0])
  b_weight_mc = newTree.Branch( "weight_mc", weight_mc, "weight_mc/F")
  weight_pileup = array.array('f', [0])
  b_weight_pileup = newTree.Branch( "weight_pileup", weight_pileup, "weight_pileup/F")
  weight_leptonSF = array.array('f', [0])
  b_weight_leptonSF = newTree.Branch( "weight_leptonSF", weight_leptonSF, "weight_leptonSF/F")
  weight_bTagSF = array.array('f', [0])
  b_weight_bTagSF = newTree.Branch( "weight_bTagSF_77", weight_bTagSF, "weight_bTagSF_77/F")
  
  i = 0
  maxEvents = 100
  print "Running over ", tree.GetEntries()
  while tree.GetEntry(i):
#    if i > maxEvents:
 #     break
    if (i%100) == 0:
      print i

    weight_mc[0] = newWeight[0]
    weight_pileup[0] = 1.0
    weight_leptonSF[0] = 1.0
    weight_bTagSF[0] = 1.0
    newTree.Fill()
    i +=1 

  sumWeightsTree = inFile.Get( "sumWeights" )
  outFile.cd()

  newWeightsTree = sumWeightsTree.CloneTree(0)
  newDSID = array.array('i', [0])
  sumWeightsTree.SetBranchAddress("dsid", newDSID)
  newTotalEventsWeighted = array.array('f', [0])
  sumWeightsTree.SetBranchAddress("totalEventsWeighted", newTotalEventsWeighted)
  newTotalEvents = array.array('l', [0])
  sumWeightsTree.SetBranchAddress("totalEvents", newTotalEvents)

#  sumWeightsTree.GetEntry(0) 
  newDSID[0] = 999999
  newTotalEventsWeighted[0] = 1
  newTotalEvents[0] = 1
  newWeightsTree.Fill()

  outFile.Write()
 
  outFile.Close()
  inFile.Close()


if __name__ == "__main__":
  splitTrees()
  print "Finished splitTrees()"
