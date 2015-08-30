import ROOT

histInfos = []
histMap = {}
histMap["title"] = "jet_pt"
AxisVars = []
AxisVars.append("jet_pt")
AxisLow = []
AxisLow.append(0)
AxisHigh = []
AxisHigh.append(1000)
Bin = []
Bin.append(100)
histMap["vars"] = AxisVars
histMap["low"] = AxisLow
histMap["high"] = AxisHigh
histMap["bins"] = Bin
histInfos.append(histMap)


histList = []
variablesList = []
histVarMap = []
for histInfo in histInfos:
  theseVars = histInfo["vars"]
  histList.append( ROOT.TH1F(histInfo["title"], histInfo["title"], histInfo["bins"], histInfo["low"], histInfo["high"] ))
  for var in theseVars:
    if not var in variablesList:
      variablesList.append(var)
  histVarMap.append([])
  for var in theseVars:
    histVarMap[-1].append( variablesList.index(var) )



inputTree = "group.phys-exotics.mc15_13TeV.361024.Pythia8EvtGen_A14NNPDF23LO_jetjet_JZ4W.All_1.QCDPythia8_v3_20150817_tree.root"
inFile = ROOT.TFile(inputTree, "READ")
inTree = inFile.Get("outTree_Nominal")
for iBranch, thisBranch in enumerate(iTree.GetListOfBranches()):
  branchName = thisBranch.GetName()
  branchType = thisBranch.GetListOfLeaves().At(0).GetTypeName()

  if not branchName in variablesList:
    continue

  if "vector<vector<int> >" in branchType:
    variableList[iBranch] = std.vector(std.vector('int'))()
  elif "vector<vector<float> >" in branchType:
    variableList[iBranch] = std.vector(std.vector('float'))()
  elif "vector<vector<string> >" in branchType:
    variableList[iBranch] = std.vector(std.vector('string'))()
  elif "vector<int>" in branchType:
    variableList[iBranch] = std.vector('int')()
  elif "vector<float>" in branchType:
    variableList[iBranch] = std.vector('float')()
  elif "vector<string>" in branchType:
    variableList[iBranch] = std.vector('string')()
  elif "Int_t" in branchType:
    variableList[iBranch] = array.array('i', [0])
  elif "Float_t" in branchType:
    variableList[iBranch] = array.array('f', [0])
  else:
    print "Type of ", branchName, "(", branchType, ") Not recognized!!"
    continue

outFile = ROOT.TFile("tmp.root", "RECREATE")

for event in inTree:
  print event.jet_pt[0]
