###############################################
#  plotUtils.py                               #
#                                             #
#  purpose: collect common plotting functions #
#                                             #
###############################################

import ROOT
from array import array
import re, sys, os, math

##############################################################################################
##############################################################################################
# LIST OF FUNCTIONS BELOW AND DESCRIPTION
#  getMassBins : get an array with the standard binning for the mJJ histogram
#  getMassHist : get histogram using the standard binning for the mJJ histogram
#  printHist   : dump hist content
#  checkHistPoissonianErrors : compare errors to sqrt(N) - print out only
#  setHistPoissonianErrors : set bin errors to sqrt(N)
#  roundHistogram : round histogram bin content to int - fill bin i N_i times with weight 1
#  getSignalMass : get signal mass tag from a string - NEEDS UPDATING
#  getQStarXSec  : get QStar XSEC - currently 8 TeV - NEEDS UPDATING
#  getQBHXSec    : get QBH XSEC - currently 8 TeV - NEEDS UPDATING
#  getScaleFactor: get xsec * lumi / nEvents - lumi and nEvents are inputs
#  getHistogramContainingPercentage : NEED TO READ
#  getEffectiveEntriesHistogram : returns hist w/ N event (weight=1) with equal error to input hist
#  createPseudoDataHist : fill hist from PDF crated from input hist
#  getDataLikeHist : given effective entries and input hist at desired lumi, give hist with weight=1 with shape and lumi of input hist
##############################################################################################
##############################################################################################

###############################################
# Get an array which defines the bin boundaries for the standard dijet mass plot
def getMassBins( opt = "13TeV" ):

  binLowE = []

  if "Coarse13TeV" == opt:
    ## Brian's May 7th 43 bins ##
    binLowE = [0, 30, 70, 110, 160, 210, 260, 310, 370, 440, 510, 590, 670, 760, 850, 950, 1060, 1180, 1310, 1450, 1600, 1760, 1940, 2120, 2330, 2550, 2780, 3040, 3310, 3610, 3930, 4270, 4640, 5040, 5470, 5940, 6440, 7000, 7540, 8140, 8850, 9440, 10000]

  elif "UnprescaledMass13TeV" == opt:
    # this binning is used (among other things, possibly) for m13 and m23 (masses involving second and third jets).
    # before reducing the minimum bin below 1 TeV, check that you aren't going to unblind the future >=3-jet analyses!
    binLowE = [1180, 1310, 1450, 1600, 1760, 1940, 2120, 2330, 2550, 2780, 3040, 3310, 3610, 3930, 4270, 4640, 5040, 5470, 5940, 6440, 7000, 7540, 8140, 8850, 9440, 10000]

  elif "smoother" == opt:
    ## To use: Brian's May 22nd 64 bins Option 8 alternate ##
    binLowE = [1000, 1052, 1105, 1160, 1216, 1275, 1335, 1400, 1466, 1534, 1607, 1681, 1759, 1838, 1923, 2010, 2100, 2194, 2291, 2392, 2496, 2604, 2714, 2832, 2951, 3073, 3203, 3340, 3479, 3623, 3772, 3928, 4090, 4258, 4430, 4609, 4791, 4987, 5183, 5389, 5601, 5821, 6048, 6286, 6533, 6778, 7049, 7331, 7611, 7905, 8218, 8538, 8869, 9234, 9579, 9973, 10360, 10728, 11441]

  elif "13TeVOpt7" == opt:
    ## Brian's May 22nd 78 bins Option 7 ##
    binLowE = [800, 835, 872, 909, 948, 989, 1029, 1070, 1112, 1156, 1201, 1247, 1295, 1348, 1403, 1460, 1518, 1579, 1642, 1706, 1772, 1840, 1910, 1983, 2058, 2135, 2215, 2297, 2382, 2469, 2559, 2650, 2743, 2839, 2937, 3039, 3142, 3249, 3362, 3478, 3598, 3721, 3848, 3978, 4111, 4248, 4404, 4564, 4731, 4903, 5080, 5264, 5454, 5649, 5850, 6058, 6273, 6495, 6724, 6960, 7204, 7455, 7714, 7981, 8256, 8540, 8833, 9136, 9447, 9769, 10100, 10441, 10792, 11182, 11587, 12006, 12440, 12890, 13356]

  elif "13TeVOpt8" == opt:
    ## To use: Brian's May 22nd 64 bins Option 8 ##
    binLowE = [800, 845, 890, 937, 987, 1037, 1088, 1142, 1196, 1253, 1312, 1374, 1438.48, 1506, 1577, 1649, 1722, 1800, 1880, 1965, 2056, 2146, 2241, 2337, 2439, 2545.33, 2653.47, 2766.2, 2883.73, 3006, 3132, 3263, 3396, 3534, 3682, 3832, 3991, 4157, 4325, 4499, 4681, 4864, 5052, 5253, 5467, 5685, 5904, 6132, 6371, 6619, 6869, 7136, 7414, 7694, 7994, 8305, 8626, 8951, 9317, 9668, 10032, 10389, 10758, 13000]

  elif "Original13TeV" == opt:
    # Double the first pass binning
    # For exclusion tests
    binLowE = [0, 15, 30, 50, 70, 90, 110, 135, 160, 185, 210, 235, 260, 285, 310, 340, 370, 405, 440, 475, 510, 550, 590, 630, 670, 715, 760, 805, 850, 900, 950, 1005, 1060, 1120, 1180, 1245, 1310, 1380, 1450, 1525, 1600, 1680, 1760, 1850, 1940, 2030, 2120, 2225, 2330, 2440, 2550, 2665, 2780, 2910, 3040, 3175, 3310, 3460, 3610, 3770, 3930, 4100, 4270, 4455, 4640, 4840, 5040, 5255, 5470, 5705, 5940, 6190, 6440, 6770, 7000, 7250, 7495, 7800, 8104, 8410, 8735, 9040, 9353, 9700, 10000]
  elif "13TeV" == opt:
      ## To use: Brian updated those from June 18th 96 bins Option 9
## change : extend to 13 TeV
      binLowE = [ 946, 976, 1006, 1037, 1068, 1100, 1133, 1166, 1200, 1234, 1269, 1305, 1341, 1378, 1416, 1454, 1493, 1533, 1573, 1614, 1656, 1698, 1741, 1785, 1830, 1875, 1921, 1968, 2016, 2065, 2114, 2164, 2215, 2267, 2320, 2374, 2429, 2485, 2542, 2600, 2659, 2719, 2780, 2842, 2905, 2969, 3034, 3100, 3167, 3235, 3305, 3376, 3448, 3521, 3596, 3672, 3749, 3827, 3907, 3988, 4070, 4154, 4239, 4326, 4414, 4504, 4595, 4688, 4782, 4878, 4975, 5074, 5175, 5277, 5381, 5487, 5595, 5705, 5817, 5931, 6047, 6165, 6285, 6407, 6531, 6658, 6787, 6918, 7052, 7188, 7326, 7467, 7610, 7756, 7904, 8055, 8208, 8364, 8523, 8685, 8850, 9019, 9191, 9366, 9544, 9726, 9911, 10100, 10292, 10488, 10688, 10892, 11100, 11312, 11528, 11748, 11972, 12200, 12432, 12669, 12910, 13156 ]
    ## To use: Brian's June 18th 96 bins Option 9 ##
    #binLowE = [946, 976, 1006, 1037, 1068, 1100, 1133, 1166, 1200, 1234, 1269, 1305, 1341, 1378, 1416, 1454, 1493, 1533, 1573, 1614, 1656, 1698, 1741, 1785, 1830, 1875, 1921, 1968, 2016, 2065, 2114, 2164, 2215, 2267, 2320, 2374, 2429, 2485, 2542, 2600, 2659, 2719, 2780, 2842, 2905, 2969, 3034, 3100, 3167, 3235, 3305, 3376, 3448, 3521, 3596, 3672, 3749, 3827, 3907, 3988, 4070, 4154, 4239, 4326, 4414, 4504, 4595, 4688, 4782, 4878, 4975, 5074, 5175, 5277, 5381, 5487, 5595, 5705, 5817, 5931, 6047, 6165, 6285, 6407, 6531, 6658, 6787, 6918, 7052, 7188, 7326, 7467, 7610, 7756, 7904, 8055]
    ## Brian's May 7th 67 bins ##
    #binLowE = [0, 30, 70, 110, 160, 210, 260, 310, 370, 440, 510, 590, 670, 760, 850, 950, 1060, 1120, 1180, 1240, 1310, 1380, 1450, 1520, 1600, 1680, 1760, 1850, 1940, 2030, 2120, 2220, 2330, 2440, 2550, 2660, 2780, 2910, 3040, 3170, 3310, 3460, 3610, 3770, 3930, 4100, 4270, 4460, 4640, 4840, 5040, 5250, 5470, 5700, 5940, 6190, 6440, 6710, 7000, 7270, 7540, 7860, 8140, 8450, 8850, 9440, 10000]
    # original binning - 8 TeV + some guesses afterwards
    #binLowE = [96.0, 105, 116, 127, 138, 151, 164, 177, 192, 207, 222, 239, 256, 274, 293, 312, 333, 354, 376, 400, 424, 449, 475, 502, 530, 558, 587, 618, 650, 682, 716, 750, 787, 825, 865, 906, 949, 994, 1040, 1088, 1138, 1189, 1242, 1297, 1353, 1410, 1469, 1531, 1595, 1663, 1733, 1807, 1884, 1964, 2047, 2132, 2221, 2313, 2407, 2503, 2602, 2703, 2807, 2916, 3028, 3146, 3267, 3394, 3525, 3660, 3801, 3946, 4096, 4250, 4409, 4571, 4738, 4909, 5085, 5267, 5453, 5644, 5843, 6066, 6311, 6566, 6831, 7107, 7394, 7692, 8003, 8326, 8662, 9012, 9376, 9755, 10149, 10559, 10985, 11429, 11890, 12370, 12870, 13390, 13930, 14493]
    # binning 1st pass in collaboration with SM jet group
    #binLowE = [0, 30, 70, 110, 160, 210, 260, 310,  370, 440, 510, 590, 670, 760, 850, 950, 1060, 1180, 1310, 1450, 1600, 1760, 1940, 2120, 2330, 2550, 2780, 3040, 3310, 3610, 3930, 4270, 4640, 5040, 5470, 5940, 6440, 7000, 7495, 8104, 8735, 9353, 10000]

  elif "8TeV" == opt:
    binLowE = [0.0,20.0,40.0,60.0,80.0,100.0,120.0,140.0,160.0,180.0,200.0,216.0,234.0,253.0,272.0,294.0,316.0,339.0,364.0,390.0,417.0,445.0,474.0,504.0,535.0,566.0,599.0,633.0,668.0,705.0,743.0,782.0,822.0,864.0,907.0,952.0,999.0,1048.0,1098.0,1150.0,1203.0,1259.0,1316.0,1376.0,1437.0,1501.0,1567.0,1635.0,1706.0,1779.0,1854.0,1932.0,2012.0,2095.0,2181.0,2269.0,2360.0,2454.0,2551.0,2650.0,2753.0,2860.0,2970.0,3084.0,3202.0,3324.0,3450.0,3581.0,3716.0,3855.0,3999.0,4149.0,4303.0,4463.0,4629.0,4800.0,4977.0,5160.0,5350.0,5546.0,5748.0,5958.0,6174.0,6397.0,6628.0,6866.0,7112.0,7366.0,7628.0,7898.0,8177.0]
    #Ning Binning
    #binLowE = [0,100,200,300,400,500,600,700,800,900,1000,1100,1200,1300,1400,1500,1600,1700,1800,1900,2000,2100,2200,2300,2400,2500,2600,2700,2800,2900,3000,3100,3200,3300,3400,3500,3600,3700,3800,3900,4000,4100,4200,4300,4400,4500,4600,4700,4800,4900,5000]
  else:
    print "Error, rquested binning ", opt, "not found"
    return None

  return binLowE

###############################################
# Get an array which defines the bin boundaries for the standard chi distribution plot
def getChiBins():

  binLowE = [1., 1.34986, 1.82212, 2.4596, 3.32012, 4.48169, 6.04965, 8.16617, 11.0232, 14.8797, 20.0855, 30.0]

  return binLowE

###############################################
# Get an array which defines the mass range used to make chi plots
def getChiMassBins(opt = ""):
  binLowE = []

  if "13TeV" in opt:
     binLowE = [1.8e3, 2e3, 2.25e3, 2.5e3, 2.8e3, 3.1e3, 3.4e3, 3.7e3, 4e3, 4.3e3, 4.6e3, 4.9e3, 5.4e3, 6.5e3, 8e3, 10e3, 13e3]

  if "8TeV" in opt:
    binLowE =  [0.6e3, 0.8e3, 1.2e3, 1.6e3, 2e3, 2.6e3, 3.2e3, 8e3]

  if "10pb" in opt or "Week1" in opt :
    binLowE = [0.4e3, 0.6e3, 0.9e3, 1.2e3, 1.6e3, 2e3, 2.6e3, 13e3]

  else :
    binLowE = [0.4e3, 0.6e3, 0.9e3, 1.2e3, 1.6e3, 1.8e3, 2e3, 2.25e3, 2.5e3, 2.8e3, 3.1e3, 3.4e3, 3.7e3, 4e3, 4.3e3, 4.6e3, 4.9e3, 5.4e3, 6.5e3, 8e3, 10e3, 13e3]

  return binLowE


###############################################
# get the mjj index corresponding to the chi plot mjj window
def getMjjIdx( mjj, opt = "13TeV" ):
  bins = getMjjBins( opt )

  iB = -1
  for binEdge in bins :
    if mjj > binEdge :
      iB = iB+1
      if iB > len(bins)-1 :
        return -1
    else :
      return iB

  return -1

###############################################
def getEtaBinsForJets():
  #binLowE = [0,0.8,1.2,1.8,2.1,2.8,3.1,4.9]
  binLowE = [0,0.8,1.2,1.3,1.6,2.1,2.8,3.1,4.9]
  return binLowE

def getPtBinsForJets():
  binLowE = [100, 290, 556, 786, 1012, 1530, 2500]
  return binLowE

###############################################
def getJetPtBins():
# Get an array which defines the bin boundaries for the standard pT distribution plot

#  binLowE = [15. ,20. ,25. ,35. ,45. ,55. ,70. ,85. ,100. ,116. ,134. ,152. ,172. ,194. ,216. ,240. ,264. ,290. ,318. ,346.,376.,408.,442.,478.,516.,556.,598.,642.,688.,736.,786.,838.,894.,952.,1012.,1076.,1162.,1310.,1530.,1992.,2500.]

  binLowE = [15. ,20. ,25. ,35. ,45. ,55. ,70. ,85. ,100. ,116. ,134. ,152. ,172. ,194. ,216. ,240. ,264. ,290. ,318. ,346.,376.,408.,442.,478.,516.,556.,598.,642.,688.,736.,786.,838.,894.,952.,1012.,1076.,1162.,1310.,1530.,1992.,2500.,3200]

  return binLowE

###############################################
# Get an array which defines the bin boundaries for high pT jet checks
def getCoarseJetPtBins():

  binLowE = [50., 100., 152., 240., 408., 598., 1012., 2500.]

  return binLowE

###############################################
# Get an array which defines the eta bin boundaries for high pT jet checks
def getJetEtaBins():
  binLowE = [-4.9,-3.1,-2.8,-2.1,-1.8,-1.5,-1.2,-0.8,0,0.8,1.2,1.5,1.8,2.1,2.8,3.1,4.9]
  return binLowE

def getJetAbsEtaBins():
  #binLowE = [0,0.8,1.2,1.5,1.8,2.1,2.8,3.1,4.9]
  binLowE = [0,0.8,1.2,1.5,1.8,2.1,2.8,3.1,4.9]
  return binLowE

###############################################
# Get an array which defines the eta bin boundaries for high pT jet checks
def getJetEtaBinsFine():
  binLowE = [-4.8+0.08*x for x in range(0,121)]
  return binLowE

###############################################
# Get an array which defines the eta bin boundaries for high pT jet checks
def getJetPhiBins():
  #binLowE = [-math.pi + (math.pi/4)*x for x in range(0,9)] # 8 bins
  binLowE = [-math.pi + (math.pi/32)*x for x in range(0,65)]
  return binLowE

###############################################
# Get an array which defines the eta bin boundaries for high pT jet checks
def getJetPhiBinsFine():
  binLowE = [-3.2 + (6.4/120)*x for x in range(0,121)]
  return binLowE

###############################################
# Get an array which defines some jet mass bins
def getJetMassBins():
  binLowE = [10*x for x in range(0,50)]
  return binLowE

###############################################
# Get an array of edges which divide run number range into
# bins of roughly equivalent luminosity
def getRunBins( opt = "2015" ):
  # no other bins defined
  if opt!="2015": print "warning: using 2015 run bins\n"
  # no data yet, so one bin for every five runs or something
  # starting from may 23
  bins = [265500+5*x for x in range(0,200)]
  return bins

def getNPVBins( opt = "2015" ):
  # no other bins defined
  if opt!="2015": print "warning: using 2015 NPV bins\n"
  bins = [5*x for x in range(0,12)]
  return bins

def getMuBins( opt = "2015" ):
  # no other bins defined
  if opt!="2015": print "warning: using 2015 mu bins\n"
  bins = [5*x for x in range(0,12)]
  return bins

###############################################
# Get an empty histogram with the binning for the standard dijet mass plot
def getMassHist( name, opt = "13TeV" ):
  bins = getMassBins( opt )
  hist = ROOT.TH1D( name, name, len(bins)-1, array('f', bins) )
  if "m12" in name: xlabel = "m_{12}"
  elif "m13" in name: xlabel = "m_{13}"
  elif "m23" in name: xlabel = "m_{23}"
  else: xlabel = "m_{jj}"
  hist.GetXaxis().SetTitle(xlabel + " [GeV]")
  hist.Sumw2()
  return hist

###############################################
# Get an empty histogram with the binning for the chi plot
def getChiHist( name ) :
  bins = getChiBins()
  hist = ROOT.TH1D( name, name, len(bins)-1, array('f', bins) )
  return binLowE

###############################################
# Get an array which defines the eta bin boundaries for high pT jet checks
def getJetPhiBinsFine():
  binLowE = [-3.2 + (6.4/120)*x for x in range(0,121)]
  return binLowE

###############################################
# Get an array which defines some jet mass bins
def getJetMassBins():
  binLowE = [3*x for x in range(0,120)]
  return binLowE

###############################################
# Get an array of edges which divide run number range into
# bins of roughly equivalent luminosity
def getRunBins( opt = "2015" ):
  # no other bins defined
  if opt!="2015": print "warning: using 2015 run bins\n"
  # no data yet, so one bin for every five runs or something
  # starting from may 23
  bins = [265500+5*x for x in range(0,200)]
  return bins

def getNPVBins( opt = "2015" ):
  # no other bins defined
  if opt!="2015": print "warning: using 2015 NPV bins\n"
  bins = [5*x for x in range(0,12)]
  return bins

def getMuBins( opt = "2015" ):
  # no other bins defined
  if opt!="2015": print "warning: using 2015 mu bins\n"
  bins = [5*x for x in range(0,12)]
  return bins

###############################################
# Get an empty histogram with the binning for the standard dijet mass plot
def getMassHist( name, opt = "13TeV" ):
  bins = getMassBins( opt )
  hist = ROOT.TH1D( name, name, len(bins)-1, array('f', bins) )
  if "m12" in name: xlabel = "m_{12}"
  elif "m13" in name: xlabel = "m_{13}"
  elif "m23" in name: xlabel = "m_{23}"
  else: xlabel = "m_{jj}"
  hist.GetXaxis().SetTitle(xlabel + " [GeV]")
  hist.Sumw2()
  return hist

###############################################
# Get an empty histogram with the binning for the chi plot
def getChiHist( name ) :
  bins = getChiBins()
  hist = ROOT.TH1D( name, name, len(bins)-1, array('f', bins) )
  hist.GetXaxis().SetTitle("#chi")
  hist.Sumw2()
  return hist

###############################################
# Get an empty histogram with the binning for the jet pT plot
def getJetPtHist( name, opt = "13TeV" ):
  bins = getJetPtBins( )
  hist = ROOT.TH1D( name, name, len(bins)-1, array('f', bins) )
  hist.GetXaxis().SetTitle("jet p_{T} [GeV]")
  hist.Sumw2()
  return hist

def getJetEnHist( name, opt = "13TeV" ):
  bins = getJetPtBins( )
  hist = ROOT.TH1D( name, name, len(bins)-1, array('f', bins) )
  hist.GetXaxis().SetTitle("jet E [GeV]")
  hist.Sumw2()
  return hist

# Get an empty histogram with the binning for the high pT JES check plots
def getCoarseJetPtHist( name, opt = "13TeV" ):
  bins = getCoarseJetPtBins()
  hist = ROOT.TH1D( name, name, len(bins)-1, array('f', bins) )
  hist.GetXaxis().SetTitle("jet p_{T} [GeV]")
  hist.Sumw2()
  return hist

# Get an empty histogram with the binning for the jet eta plot
def getJetEtaHist( name ):
  #bins = getJetEtaBins()
  hist = ROOT.TH1D( name, name, 120, -4.8, 4.8)
  hist.GetXaxis().SetTitle("jet #eta")
  hist.Sumw2()
  return hist

# Get an empty histogram with the binning for the jet phi plot
def getJetPhiHist( name ):
  bins = getJetPhiBins()
  hist = ROOT.TH1D( name, name, len(bins)-1, array('f', bins) )
  hist.GetXaxis().SetTitle("jet #phi")
  hist.Sumw2()
  return hist

# Get an empty histogram with the binning for the jet phi plot
def getJetEtaPhiHist( name ):
  binsX = getJetEtaBinsFine()
  binsY = getJetPhiBinsFine()
  hist = ROOT.TH2D( name, name, len(binsX)-1, array('f', binsX), len(binsY)-1, array('f', binsY) )
  hist.GetXaxis().SetTitle("jet #eta")
  hist.GetYaxis().SetTitle("jet #phi")
  hist.Sumw2()
  return hist

# Get an empty histogram with the binning for the jet phi plot
def getJetMassHist( name ):
  bins = getJetMassBins()
  hist = ROOT.TH1D( name, name, len(bins)-1, array('f', bins) )
  hist.GetXaxis().SetTitle("jet M [GeV]")
  hist.Sumw2()
  return hist

###############################################
#Get empty punchThrough studies histograms from Lydia's studies

def getNSegments(name, opt = "13TeV"):
    bins = getNSegmentBins()
    hist = ROOT.TH1D( name, name, len(bins)-1, array('f', bins) )
    hist.GetXaxis().SetTitle("N muon segs behind jet")
    hist.Sumw2()
    return hist

def getJetPt_nSegments(name, opt = "13TeV"):
    binsX = getCoarseJetPtBins()
    binsY = getNSegmentBins()
    hist = ROOT.TH2D( name, name, len(binsX)-1, array('f', binsX), len(binsY)-1, array('f', binsY) )
    hist.GetXaxis().SetTitle("jet p_{T} [GeV]")
    hist.GetYaxis().SetTitle("N muon segs behind jet")
    hist.Sumw2()
    return hist

def getJetEta_nSegments(name, opt = "13TeV"):
    binsX = getShaunEtaBins()
    binsY = getNSegmentBins()
    hist = ROOT.TH2D( name, name, len(binsX)-1, array('f', binsX), len(binsY)-1, array('f', binsY) )
    hist.GetXaxis().SetTitle("jet #eta")
    hist.GetYaxis().SetTitle("N muon segs behind jet")
    hist.Sumw2()
    return hist

def getJetPhi_nSegments(name, opt = "13TeV"):
    binsX = getShaunPhiBins()
    binsY = getNSegmentBins()
    hist = ROOT.TH2D( name, name, len(binsX)-1, array('f', binsX), len(binsY)-1, array('f', binsY) )
    hist.GetXaxis().SetTitle("jet #phi")
    hist.GetYaxis().SetTitle("N muon segs behind jet")
    hist.Sumw2()
    return hist

def getJetEMScaleEta_nSegments_TruthEg1(name, opt = "13TeV"):
    binsX = getShaunEtaBins()
    binsY = getNSegmentBins()
    hist = ROOT.TH2D( name, name, len(binsX)-1, array('f', binsX), len(binsY)-1, array('f', binsY) )
    hist.GetXaxis().SetTitle("  ")
    hist.GetYaxis().SetTitle("N muon segs behind jet")
    hist.Sumw2()
    return hist

def getShaunEtaBins():
#    nEtaBins=60
#    etaRange=3.
#    etaBins = numpy.array([])
#    for i in range (nEtaBins+1):
#        etaBins = numpy.append(etaBins, etaRange*(2.*i/nEtaBins-1.))
#    binLowE = etaBins.tolist()
    binLowE = [-4.,-3.,-2.,-1.,0,1.,2.,3.,4.]
    return binLowE

def getShaunPhiBins():
#    nPhiBins=100
#    phiRange= math.pi
#    phiBins = numpy.array([])
#    for i in range (nPhiBins+1):
#        phiBins = numpy.append(phiBins, phiRange*(2.*i/nPhiBins-1.))
#    binLowE = phiBins.tolist()
    binLowE = [-4.,-3.,-2.,-1.,0,1.,2.,3.,4.]
    return binLowE

###############################################
# Get an empty histogram with simple binning using input nbins and preset max and min based on variable
def getHistExtrema(tree,branch,type):
  boundaries = [-1000,1000]

  if branch=="dummy": [tree.GetMinimum(branch),tree.GetMaximum(branch)]
#  elif branch=="runNumber": ends = []
#  elif branch=="eventNumber": ends = []
#  elif branch=="mcEventNumber": ends = []
#  elif branch=="mcChannelNumber": ends = []
#  elif branch=="mcEventWeight": ends = []
  elif branch=="NPV": ends = [0.,60.]
  elif branch=="actualInteractionsPerCrossing": ends = [0.,50.]
  elif branch=="averageInteractionsPerCrossing": ends = [0.,50.]
  elif branch=="pdgId1" : ends = [-10.,25.]
  elif branch=="pdgId2" : ends = [-10.,25.]
  elif branch=="pdfId1" : ends = [-10.,10.]
  elif branch=="pdfId2" : ends = [-10.,10.]
  elif branch=="x1": ends = [0.,1.]
  elif branch=="x2": ends = [0.,1.]
  elif branch=="xf1": ends = [0.,30.]
  elif branch=="xf2": ends = [0.,30.]
  elif branch=="yStar": ends = [-3.,3.]
  elif branch=="yBoost": ends = [-3.,3.]
  elif branch=="mjj": ends = [0.,13000.]
  elif branch=="pTjj": ends = [0.,2500.]
  elif branch=="m3j": ends = [0.,13000.]
  elif branch=="deltaPhi": ends = [0.,3.2]
#  elif branch=="weight": ends = []
#  elif branch=="weight_xs": ends = []
#  elif branch=="weight_prescale": ends = []
  elif branch=="njets": ends = [0,16]
  elif branch=="jet_E": ends = [0,7000]
  elif branch=="jet_pt": ends = [0,6500]
  elif branch=="jet_phi": ends = [-3.2,3.2]
  elif branch=="jet_eta": ends = [-4,4]
  elif branch=="jet_Timing": ends = [-11,11]
  elif branch=="jet_LArQuality": ends = [-0.2,1.2]
  elif branch=="jet_HECQuality": ends = [-1.1,1.1]
  elif branch=="jet_NegativeE": ends = [-65,5]
  elif branch=="jet_AverageLArQF": ends = [0,60]
  elif branch=="jet_BchCorrCell": ends = [-0.1,0.5]
  elif branch=="jet_N90Constituents": ends = [0,46]
#  elif branch=="jet_LArBadHVEnergy": ends = []
#  elif branch=="jet_LArBadHVRatio": ends = []
  elif branch=="jet_HECFrac": ends = [-0.1,1.1]
  elif branch=="jet_EMFrac": ends = [-0.1,1.5]
  elif branch=="jet_CentroidR": ends = [0,6500]
  elif branch=="jet_FracSamplingMax": ends = [0,1.1]
  elif branch=="jet_FracSamplingMaxIndex": ends = [-1,25]
#  elif branch=="jet_LowEtConstituentsFrac": ends = []
  elif branch=="jet_GhostMuonSegmentCount": ends = [0,200]
  elif branch=="jet_SVO": ends = [-200,800]
  elif branch=="jet_SV1": ends = [-8,12]
  elif branch=="jet_IP3D": ends = [-100,150]
  elif branch=="jet_SV1IP3D": ends = [-100,150]
#  elif branch=="jet_MV1": ends = []
  elif branch=="jet_MV2c00": ends = [-1.1,1.1]
  elif branch=="jet_MV2c20": ends = [-1.1,1.1]
  elif branch=="jet_ConeTruthLabelID": ends = [-1,20]
#  elif branch=="jet_TruthCount": ends = []
  elif branch=="jet_TruthLabelDeltaR_B": ends = [0,0.6]
  elif branch=="jet_TruthLabelDeltaR_C": ends = [0,0.6]
  elif branch=="jet_TruthLabelDeltaR_T": ends = [0,0.6]
  elif branch=="jet_PartonTruthLabelID": ends = [-10,25]
  elif branch=="jet_GhostTruthAssociationFraction": ends = [-0.1,1.1]
  elif branch=="jet_truth_E": ends = [0,7000]
  elif branch=="jet_truth_pt": ends = [0,6500]
  elif branch=="jet_truth_phi": ends = [-3.2,3.2]
  elif branch=="jet_truth_eta": ends = [-5,5]
  elif branch=="jet_detEta": ends = [-5,5]
  elif branch=="jet_emScaleEta": ends = [-4,4]

  else: ends = [tree.GetMinimum(branch),tree.GetMaximum(branch)]


  if type=="min":
      value = ends[0]
  elif type=="max":
    value = ends[1]
  return value

###############################################



########## From input string, get name of sample ###############
def getName(f, splitSlices = False):
  type = ""
#    user.jdandoy.data15_comm.00265545.physics_MinBias.None.JetInputs_DataMay23_v0_20150527_tree.root
#  type = f.split('.')
#  if len(type) < 6:
#    print "Error, we expect input files to have more than 6 fields of information, where a field is speerated by '.'"
#    print "For example: user.jdandoy.data15_comm.00265545.physics_MinBias.None.JetInputs_DataMay23_v0_20150527_tree.root"
#    return "None"
#  return '.'.join( type[2:5] )

  if f.find("jetjet") > 0 or f.find("QCDDiJet") >0:
    type="QCDDiJet"
    if splitSlices:
      for i in range(15):
        if "JZ"+str(i) in f:
          type = type + "_JZ"+str(i)
          break
        elif "JZW"+str(i) in f:
          type = type + "_JZ" + str(i) + "W"
          break

  elif f.find("ExcitedQ")>0:
    masses = [ "2000", "2500", "3000", "3500", "4000", "4500", "5000", "5500", "6000", "6500", "7000" ]
    type = "ExcitedQ"
    for mass in masses:
      if f.find(mass)>0:
        type += "_"+mass
        break

  elif f.find("data15")>0:
    type = "data15"

  else:
    print("plotUtils::getName - no names are found in this string")
    print(f)

  #print(f)
  #print(type)
  return type

###############################################

## a standarized set of colors for each dijet slice
def getDijetColor( name ):

  if "JZ" in name:
    sliceNum = name[name.find("JZ")+2][0]
    sliceNum = float( sliceNum )
  else:
    return ROOT.kBlack


  #### Color Palette ####
  colorMax = 240.
  colorMin = 20.
  numSlices = 8.
  colorNum = int(colorMin+(colorMax-colorMin)*sliceNum/numSlices)
  return ROOT.gStyle.GetColorPalette(colorNum)

  #### Color Wheel ####
#  nColors = 12
#  stops = array('d', [0., 0.35, 0.65, 1.] )
#  red =   array('d', [1., 0., 0., 1.] )
#  green = array('d', [0., 0., 1., 0.] )
#  blue =  array('d', [0., 1., 0., 1.] )
#
#  colorStart = ROOT.TColor.CreateGradientColorTable(len(stops), stops, red, green, blue, nColors)
#  return int(colorStart+sliceNum)

  #### Manual Setting ####
#  if "JZ9" in name: return ROOT.kGreen - 3
#  if "JZ8" in name: return ROOT.kRed - 3
#  if "JZ7" in name: return ROOT.kMagenta - 3
#  if "JZ6" in name: return ROOT.kBlue - 3
#  if "JZ5" in name: return ROOT.kCyan - 3
#  if "JZ4" in name: return ROOT.kGreen + 3
#  if "JZ3" in name: return ROOT.kRed + 3
#  if "JZ2" in name: return ROOT.kMagenta + 3
#  if "JZ1" in name: return ROOT.kBlue + 3
#  if "JZ0" in name: return ROOT.kCyan + 3

## a standarized set of colors for each dijet mass parton plot
def getMassPartonColor( name ):
    if "qqToqq" in name: return ROOT.kGreen - 3
    elif "qqTogq" in name: return ROOT.kCyan - 3
    elif "ggToqq" in name: return ROOT.kBlue - 3
    elif "gqToqg" in name: return ROOT.kMagenta - 3
    elif "ggTogg" in name: return ROOT.kRed - 3
    elif "qgToqg" in name: return ROOT.kOrange - 3
    elif "ggToqg" in name: return ROOT.kGreen + 3
    elif "ggTogq" in name: return ROOT.kCyan + 3
    elif "qqTogg" in name: return ROOT.kBlue + 3
    elif "qqToqg" in name: return ROOT.kMagenta + 3
    elif "qgTogg" in name: return ROOT.kRed + 3
    elif "qgToqq" in name: return ROOT.kOrange + 3
    elif "gqTogg" in name: return ROOT.kYellow + 3
    elif "qgTogq" in name: return ROOT.kYellow - 3
    elif "gqTogq" in name: return ROOT.kBlue + 1
    elif "gqToqq" in name: return ROOT.kMagenta + 1

## a standarized set of colors for each dijet mass parton plot
def getMassPartonColorOneSide( name ):
    if "qq" in name: return ROOT.kGreen - 3
    elif "gq" in name: return ROOT.kCyan - 3
    elif "qg" in name: return ROOT.kCyan - 3
    elif "gg" in name: return ROOT.kBlue - 3
#    elif "gqToqg" in name: return ROOT.kMagenta - 3
#    elif "ggTogg" in name: return ROOT.kRed - 3
#    elif "qgToqg" in name: return ROOT.kOrange - 3
#    elif "ggToqg" in name: return ROOT.kGreen + 3
#    elif "ggTogq" in name: return ROOT.kCyan + 3
#    elif "qqTogg" in name: return ROOT.kBlue + 3
#    elif "qqToqg" in name: return ROOT.kMagenta + 3
#    elif "qgTogg" in name: return ROOT.kRed + 3
#    elif "qgToqq" in name: return ROOT.kOrange + 3
#    elif "gqTogg" in name: return ROOT.kGreen + 1
#    elif "qgTogq" in name: return ROOT.kCyan + 1
#    elif "gqTogq" in name: return ROOT.kBlue + 1
#    elif "gqToqq" in name: return ROOT.kMagenta + 1



## a standarized set of colors for each dijet mass parton plot
def getSignalColor( name ):
    if "ExcitedQ_2000" in name: return ROOT.kGreen - 3
    elif "ExcitedQ_2500" in name: return ROOT.kCyan - 3
    elif "ExcitedQ_3000" in name: return ROOT.kBlue - 3
    elif "ExcitedQ_3500" in name: return ROOT.kMagenta - 3
    elif "ExcitedQ_4000" in name: return ROOT.kRed - 3
    elif "ExcitedQ_4500" in name: return ROOT.kYellow - 3
    elif "ExcitedQ_5000" in name: return ROOT.kGreen + 3
    elif "ExcitedQ_5500" in name: return ROOT.kCyan + 3
    elif "ExcitedQ_6000" in name: return ROOT.kBlue + 3
    elif "ExcitedQ_6500" in name: return ROOT.kMagenta + 3
    elif "ExcitedQ_7000" in name: return ROOT.kRed + 3

    else: return ROOT.kBlack


#******************************************
def printHist (hist):
    """print histogram content
    """
    for bin in xrange(1,hist.GetNbinsX()+1):
        print "bin %5s = %10.4f +/- %10.4f"%(bin, hist.GetBinContent(bin), hist.GetBinError(bin))

#******************************************
def checkHistPoissonianErrors (hist):
    """check if the errors of the histogram are Poissonian
    """
    for bin in xrange(1,hist.GetNbinsX()+1):
        if hist.GetBinContent(bin) != 0:
            if hist.GetBinError(bin) != math.sqrt(hist.GetBinContent(bin)):
                print "bin %5s = %10.4f +/- %10.4f\t->\t%10.4f"%(bin, hist.GetBinContent(bin), hist.GetBinError(bin), math.sqrt(hist.GetBinContent(bin)))
            else:
                print "bin %5s is ok"%bin
        else:
            print "bin %5s is empty"%bin

#******************************************
def setHistPoissonianErrors (hist, debug=False):
    """set Poissonian errors
    """
    for bin in xrange(1,hist.GetNbinsX()+1):
        hist.SetBinError(bin, math.sqrt(hist.GetBinContent(bin)))
        if debug:
            print "bin %5s = %10.4f +/- %10.4f"%(ii, hist.GetBinContent(bin), hist.GetBinError(bin))
    return hist

#******************************************
def roundHistogram (hist):
    """round the histogram bin content to integer numbers; NOTE fill histogram one entry at a time
    """
    newHist = ROOT.TH1D("newHist","newHist",hist.GetXaxis().GetNbins(),hist.GetXaxis().GetXbins().GetArray())
    newHist.SetDefaultSumw2(ROOT.kTRUE)
    for bin in xrange(1,hist.GetNbinsX()+1):
        bincontent = int(round(hist.GetBinContent(bin)))
        for iBinCont in xrange(bincontent):
            newHist.Fill(newHist.GetBinCenter(bin))
    return newHist

#******************************************
#def getSignalMass(name):
#    if "ExcitedQ" in name:
#        regEx = re.compile("ExcitedQ(.*)Lambda")
#    elif "BlackMax" in name:
#        regEx = re.compile("MthMD(.*)\.e2303")
#    else:
#        regEx = re.compile("_14TeV(.*)_AU2")
#
#    match = regEx.search(name)
#    sample = match.group(1)
#    return sample
#
##******************************************
#def getQStarXSec(mass):
#    #cross sections are in nb
#    sampleDict = {}
#    sampleDict["2000"]  = 3.680e-02
#    sampleDict["3000"]  = 2.985e-03
#    sampleDict["4000"]  = 3.534e-04
#    sampleDict["5000"]  = 4.833e-05
#    sampleDict["6000"]  = 7.047e-06
#    sampleDict["7000"]  = 1.039e-06
#    sampleDict["8000"]  = 1.626e-07
#    sampleDict["9000"]  = 3.186e-08
#    sampleDict["10000"] = 9.205e-09
#    sampleDict["11000"] = 3.653e-09
#    sampleDict["12000"] = 1.684e-09
#    sampleDict["13000"] = 8.456e-10
#
#    #return cross section in nb
#    #print 'QStar [%s GeV] cross section: %s nb'%(mass, str(sampleDict[mass]/1e3))
#    return sampleDict[mass]
#
##******************************************
##function taken from CommonFunctions.py
#def getQBHXSec(mass):
#	#cross sections are in pb
#    sampleDict = {}
#    sampleDict["2000"] = 2.570e+03
#    sampleDict["3000"] = 2.194e+02
#    sampleDict["4000"] = 2.742e+01
#    sampleDict["5000"] = 3.850e+00
#    sampleDict["6000"] = 5.507e-01
#    sampleDict["7000"] = 7.374e-02
#    sampleDict["8000"] = 8.615e-03
#    sampleDict["9000"] = 8.318e-04
#    sampleDict["10000"] = 5.754e-05
#    sampleDict["11000"] = 2.431e-06
#    sampleDict["12000"] = 4.606e-08
#
#    #return cross section in nb
#    #print 'QBH [%s GeV] cross section: %s nb'%(mass, str(sampleDict[mass]/1e3))
#    return sampleDict[mass]/1e3
#
##******************************************
#def getScaleFactor(model, mass, lumi, nEvents):
#    #print "lumi = %s nb^-1"%lumi
#    if model == "QStar":
#        return (getQStarXSec(mass) * lumi) / nEvents
#    elif model == "QBH":
#        return (getQBHXSec(mass) * lumi) / nEvents
#    else:
#        raise SystemExit("\n***ERROR*** unknown signal sample: %s"%name)

#******************************************
def getHistogramContainingPercentage(hist, percentage, lowBin=-999, highBin=-999):

    if lowBin == -999 : lowBin = 1
    if highBin == -999 : highBin = hist.GetNbinsX()+1

    nbins = hist.GetNbinsX()
    if (nbins==0) : return None

    integral = hist.Integral()
    if (integral==0) : return None

    firstBin = 1
    while (hist.GetBinContent(firstBin)==0) : firstBin = firstBin+1

    lastBin = nbins
    while (hist.GetBinContent(lastBin)==0) : lastBin = lastBin-1

    binsToScan = lastBin - firstBin
    if (binsToScan==0) : return None

    scanStep = binsToScan/100
    if (scanStep<1) : scanStep=1

    thisPercentage=0
    thisInterval=0

    remember1=1
    remember2=1

    #a really big interval to start with.
    smallestInterval= hist.GetBinLowEdge(lastBin) + hist.GetBinWidth(lastBin) - hist.GetBinLowEdge(firstBin) + 1e12

    rememberThisPercentage=0

    for bin1 in xrange(firstBin, lastBin+1, scanStep) :
        for bin2 in xrange(bin1, lastBin+1, scanStep) :

            #print "bins ", bin1, " to ", bin2
            thisPercentage = (hist.Integral(bin1,bin2))/integral
            thisInterval = hist.GetBinLowEdge(bin2) +  hist.GetBinWidth(bin2) - hist.GetBinLowEdge(bin1)
            #print " -. contain ", thisPercentage

            if thisPercentage >= percentage :
                if thisInterval < smallestInterval :
                    remember1=bin1
                    remember2=bin2
                    smallestInterval=thisInterval
                    rememberThisPercentage=thisPercentage
                break

    #print "best interval are bins : ", remember1, " , ", remember2
    #print " which span ", smallestInterval, "GeV"
    lowBin=remember1
    highBin=remember2

    #now make the histogram
    choppedHist = hist.Clone()
    choppedHist.Reset("ICE")
    for iBin in xrange(1, hist.GetNbinsX()+1) :
        if iBin < lowBin : continue
        if iBin > highBin : continue
        choppedHist.SetBinContent(iBin, hist.GetBinContent(iBin))
        choppedHist.SetBinError(iBin, hist.GetBinError(iBin))

    #print "bins [" , lowBin, "," , highBin , "] contain " , rememberThisPercentage*100, "percent of the signal"
    return choppedHist

#******************************************
def getEffectiveEntriesHistogram(hist, name = "hee"):
    hee = ROOT.TH1D(name,name,hist.GetXaxis().GetNbins(),hist.GetXaxis().GetXbins().GetArray())
    for bin in xrange(1,hist.GetNbinsX()+1):
        if hist.GetBinError(bin) != 0.:
            nee = pow(hist.GetBinContent(bin), 2) /  pow(hist.GetBinError(bin), 2)
        else:
            nee = 0.
        hee.SetBinContent(bin, nee)
        hee.SetBinError(bin, math.sqrt(nee))
    return hee

#******************************************
def createPseudoDataHist(inHist):

    #nEvents = inHist.GetSumOfWeights()
    nEvents = inHist.Integral()
    #nEvents = inHist.GetEntries() * lumi

    print "number of events: %s"%nEvents
    random = ROOT.TRandom3(1986)
    gRandom = random

    normalizedMassDist = inHist.Clone("normalized_mjj")
    normalizedMassDist.Scale(1./normalizedMassDist.Integral())
    nEventsFluctuated = random.Poisson(floor(nEvents))
    pseudoData = inHist.Clone("pseudo_data")
    pseudoData.Reset()
    pseudoData.FillRandom(normalizedMassDist, int(nEventsFluctuated))

    return pseudoData

#******************************************
def getDataLikeHists( effectiveHist, scaledHists, names, jobSeed = 10 ):
  dataLikeHists = []
  for iHist, scaledHist in enumerate(scaledHists):
    dataLikeHists.append( ROOT.TH1D(names[iHist], names[iHist], effectiveHist.GetXaxis().GetNbins(), effectiveHist.GetXaxis().GetXbins().GetArray()) )
    dataLikeHists[-1].SetDirectory(0)

  rand3 = ROOT.TRandom3(1986) #1986 #ORIGINAL

  #Bin upper edge must be above this limit
  massLimit = 1000.

  ## If not a single bin has enough effective entries, we will return None
  hasAcceptableBin = [False for i in range(len(scaledHists))]
  scaledHistThreshold = [0. for i in range(len(scaledHists))]

  #Loop over effective histogram bins
  for bin in xrange(1, effectiveHist.GetNbinsX()+1):
    #enough effective entries?

    #NOTE the seed for each bin must be always the same
    binSeed = int( round( effectiveHist.GetBinCenter(bin) + jobSeed*1e5 ))
    rand3.SetSeed(binSeed)

    effectiveEntries = effectiveHist.GetBinContent(bin)
    ## Don't do low mass bins, too many effective entries... ##
    if effectiveHist.GetXaxis().GetBinUpEdge(bin) < massLimit:
      continue
    fillValue = effectiveHist.GetBinCenter(bin)

    print "effective entries", effectiveEntries

    ## check that histograms can be made datalike 
    for iHist, scaledHist in enumerate(scaledHists):
      print scaledHist.GetBinContent(bin)
      if scaledHist.GetBinContent(bin) > 0 and effectiveEntries >= scaledHist.GetBinContent(bin):
        hasAcceptableBin[iHist] = True
        scaledHistThreshold[iHist] = scaledHist.GetBinContent(bin) / effectiveEntries
      elif effectiveEntries < scaledHist.GetBinContent(bin) and effectiveHist.GetXaxis().GetBinUpEdge(bin) > massLimit:
        print "***Warning***  Not enough effective entries for bin", bin, "(", scaledHist.GetXaxis().GetBinLowEdge(bin), "to", scaledHist.GetXaxis().GetBinUpEdge(bin), "GeV) in histogram, ", scaledHist.GetName()
        scaledHistThreshold[iHist] = 0. #Don't fill this one
      else:
        scaledHistThreshold[iHist] = 0. #Don't fill this one

    #get data-like bin content by picking entries
    #NOTE weights are poissonian by construction
    for jj in xrange( int( round( effectiveEntries ) ) ):
      eventThreshold = rand3.Uniform()

      for iHist, scaledHist in enumerate(scaledHists):
        if eventThreshold < scaledHistThreshold[iHist] :
          dataLikeHists[iHist].Fill( fillValue )


  ## Check if not a single bin has enough effective entries
  for iHist, binDecision in enumerate(hasAcceptableBin):
    if not binDecision:
      dataLikeHists[iHist] = None

  return dataLikeHists

def getDataLikeHist( eff, scaled, name, jobSeed = 10 ):
  dataLike = ROOT.TH1D(name, name, eff.GetXaxis().GetNbins(),eff.GetXaxis().GetXbins().GetArray())
  dataLike.SetDirectory(0)
  #random number generator
  rand3 = ROOT.TRandom3(1986) #1986 #ORIGINAL

  #Bin upper edge must be above this limit
  massLimit = 1000.

  hasAcceptableBin = False

  #loop over bins
  for bin in xrange(1,eff.GetNbinsX()+1):
    #enough effective entries?
    nee = eff.GetBinContent(bin)
    if scaled.GetBinContent(bin) > 0 and nee >= scaled.GetBinContent(bin) and scaled.GetXaxis().GetBinUpEdge(bin) > massLimit:
      hasAcceptableBin = True

      #set seed
      #NOTE the seed for each bin must be always the same
      binSeed = int( round( eff.GetBinCenter(bin) + jobSeed*1e5 ))
      #print '  bin %s\t seed = %i'%(bin, binSeed)
      rand3.SetSeed(binSeed)

      #get data-like bin content by drawing entries
      #NOTE weights are poissonian by construction
      for jj in xrange( int( round( nee ) ) ):
        if rand3.Uniform() < scaled.GetBinContent(bin) / nee :
          dataLike.Fill(dataLike.GetBinCenter(bin))

    elif nee < scaled.GetBinContent(bin) and scaled.GetXaxis().GetBinUpEdge(bin) > massLimit:
      print "***Warning***  Not enough effective entries for bin", bin, "(", scaled.GetXaxis().GetBinLowEdge(bin), "to", scaled.GetXaxis().GetBinUpEdge(bin), "GeV) in histogram, ", dataLike.GetName()

  ## If not a single bin has enough effective entries
  if not hasAcceptableBin:
    return None

  return dataLike

#******************************************
def getLumiFromFileName(fileName):
    #get luminosity value from file name
    keys = fileName.split('.')
    for ii in xrange(len(keys)):
        if keys[ii] == 'ifb':
            return keys[ii-1]
    raise SystemExit('\n***ERROR*** couldn\'t find luminosity for file: %s'%fileName)

#******************************************
def getSignalMassFromFileName(fileName):
    #get luminosity value from file name
    keys = fileName.split('.')
    for ii in xrange(len(keys)):
        if keys[ii] == 'GeV':
            return keys[ii-1]
    raise SystemExit('\n***ERROR*** couldn\'t find signal mass for file: %s'%fileName)

#******************************************
def getSignalModelFromFileName(fileName):
    #get luminosity value from file name
    keys = fileName.split('.')
    for ii in xrange(len(keys)):
        if keys[ii] == 'GeV':
            return keys[ii-2]
    raise SystemExit('\n***ERROR*** couldn\'t find signal model for file: %s'%fileName)

#******************************************
def getSampleInfo(path, dsid, i):
    #given a DSID, get the number of generated events from a table
    #table is samples.info
    #'i' is the i-th entry in the sample info table
    dsid = str(dsid)
    f = open(os.environ['ROOTCOREBIN']+'/../DijetResonanceAlgo/data/XsAcc_13TeV.txt', 'r')
    lines = f.read().splitlines()
    for line in lines:
        if line.startswith('#'): line = line[1:]
        info = line.split()
        if len(info) == 0: continue
        if info[0] == dsid:
            return info[i]
    print '\n***WARNING*** DSID %s not found in the library\n'%dsid
    return 0

#******************************************
def getSampleCrossSection(path, dsid):
    #given a DSID, get the cross-section
    return getSampleInfo(path, dsid, 1)

#******************************************
def getSampleAcceptance(path, dsid):
    #given a DSID, get the acceptance
    return getSampleInfo(path, dsid, 2)

#******************************************
def getSampleNEntries(path, dsid):
    #given a DSID, get the number of generated events from a table
    return getSampleInfo(path, dsid, 3)

#******************************************
#def getRawTreeFileList(path, tag1, tag2):
#    #NOTE given a path and two tags (to identify the right dataset),
#    #return the list of all the 'tree' files
#    #NOTE 'path' should be the path to the gridOutput/ directory
#
#    path+='/rawDownload/'
#    fileList = []
#
#    for d in os.listdir(path):
#        if not os.path.isdir( os.path.join(path,d) ): continue
#        if not '_tree.root' in d: continue
#        if not tag1 in d: continue
#        if not tag2 in d: continue
#        #print '  %s'%d
#
#        for f in os.listdir( os.path.join(path,d) ):
#            if not '.tree.root' in f: continue
#            #print '    %s'%f
#            fileList.append(path+'/'+d+'/'+f)
#
#    fileList.sort()
#    return fileList

#******************************************
def getFileList(path, tags):
    return getMergedTreeFileList(path, tags)

def getMergedTreeFileList(path, tags):
    #NOTE given a path and tags (to identify the right dataset),
    #return the list of all the merged 'tree' files
    #NOTE 'path' should be the path to the gridOutput directory
    tags.append(".root")


    path+='/'
    fileList = []
    for f in os.listdir(path):
      if not os.path.isfile( os.path.join(path,f) ): continue

      passed = True
      for tag in tags:
        if '=' in tag:
          if not any(splitTag in f for splitTag in list(tag.split('='))):
            passed = False
        else:
          if not tag in f:
            passed = False

      if passed:
        fileList.append( os.path.join(path,f) )

    fileList.sort()
    return fileList

#******************************************
def getCutflowEntries(path, tags, dsid):
    #NOTe given a path, tags and the DSID
    #get the number of events in the first bin of the cutflow
    #NOTE this is a backup solution, the cutflow histogram should be in the tree file

    path += '/cutflow/'
    events = 0
    fileList = []

    for f in os.listdir(path):
        if not os.path.isfile( os.path.join(path,f) ): continue
        if not 'user.' in f: continue
        if not '.root' in f: continue
        if not str(dsid) in f: continue
        if all(tag in f for tag in tags):
          fileList.append( os.path.join(path,f) )

    if len(fileList) < 1:
        raise SystemExit('\n***EXIT*** no cutflow file found')

    elif len(fileList) > 1:
        raise SystemExit('\n***EXIT*** too many cutflow files found')

    else:
        #print '  cutflow file: %s'%fileList[0]
        c = ROOT.TFile.Open(fileList[0],'READ')
        keys = c.GetListOfKeys()
        for key in keys:
            if key.ReadObj().GetTitle() == 'cutflow':
                events = key.ReadObj().GetBinContent(1)
                break

    return events





def getNSegmentBins():
    binLowE = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0, 20.0, 21.0, 22.0, 23.0, 24.0, 25.0, 26.0, 27.0, 28.0, 29.0, 30.0, 31.0, 32.0, 33.0, 34.0, 35.0, 36.0, 37.0, 38.0, 39.0, 40.0, 41.0, 42.0, 43.0, 44.0, 45.0, 46.0, 47.0, 48.0, 49.0, 50.0, 51.0, 52.0, 53.0, 54.0, 55.0, 56.0, 57.0, 58.0, 59.0, 60.0, 61.0, 62.0, 63.0, 64.0, 65.0, 66.0, 67.0, 68.0, 69.0, 70.0, 71.0, 72.0, 73.0, 74.0, 75.0, 76.0, 77.0, 78.0, 79.0, 80.0, 81.0, 82.0, 83.0, 84.0, 85.0, 86.0, 87.0, 88.0, 89.0, 90.0, 91.0, 92.0, 93.0, 94.0, 95.0, 96.0, 97.0, 98.0, 99.0, 100.0, 101.0, 102.0, 103.0, 104.0, 105.0, 106.0, 107.0, 108.0, 109.0, 110.0, 111.0, 112.0, 113.0, 114.0, 115.0, 116.0, 117.0, 118.0, 119.0, 120.0, 121.0, 122.0, 123.0, 124.0, 125.0, 126.0, 127.0, 128.0, 129.0, 130.0, 131.0, 132.0, 133.0, 134.0, 135.0, 136.0, 137.0, 138.0, 139.0, 140.0, 141.0, 142.0, 143.0, 144.0, 145.0, 146.0, 147.0, 148.0, 149.0, 150.0, 151.0, 152.0, 153.0, 154.0, 155.0, 156.0, 157.0, 158.0, 159.0, 160.0, 161.0, 162.0, 163.0, 164.0, 165.0, 166.0, 167.0, 168.0, 169.0, 170.0, 171.0, 172.0, 173.0, 174.0, 175.0, 176.0, 177.0, 178.0, 179.0, 180.0, 181.0, 182.0, 183.0, 184.0, 185.0, 186.0, 187.0, 188.0, 189.0, 190.0, 191.0, 192.0, 193.0, 194.0, 195.0, 196.0, 197.0, 198.0, 199.0, 200.0, 201.0, 202.0, 203.0, 204.0, 205.0, 206.0, 207.0, 208.0, 209.0, 210.0, 211.0, 212.0, 213.0, 214.0, 215.0, 216.0, 217.0, 218.0, 219.0, 220.0, 221.0, 222.0, 223.0, 224.0, 225.0, 226.0, 227.0, 228.0, 229.0, 230.0, 231.0, 232.0, 233.0, 234.0, 235.0, 236.0, 237.0, 238.0, 239.0, 240.0, 241.0, 242.0, 243.0, 244.0, 245.0, 246.0, 247.0, 248.0, 249.0, 250.0, 251.0, 252.0, 253.0, 254.0, 255.0, 256.0, 257.0, 258.0, 259.0, 260.0, 261.0, 262.0, 263.0, 264.0, 265.0, 266.0, 267.0, 268.0, 269.0, 270.0, 271.0, 272.0, 273.0, 274.0, 275.0, 276.0, 277.0, 278.0, 279.0, 280.0, 281.0, 282.0, 283.0, 284.0, 285.0, 286.0, 287.0, 288.0, 289.0, 290.0, 291.0, 292.0, 293.0, 294.0, 295.0, 296.0, 297.0, 298.0, 299.0, 300.0, 301.0, 302.0, 303.0, 304.0, 305.0, 306.0, 307.0, 308.0, 309.0, 310.0, 311.0, 312.0, 313.0, 314.0, 315.0, 316.0, 317.0, 318.0, 319.0, 320.0, 321.0, 322.0, 323.0, 324.0, 325.0, 326.0, 327.0, 328.0, 329.0, 330.0, 331.0, 332.0, 333.0, 334.0, 335.0, 336.0, 337.0, 338.0, 339.0, 340.0, 341.0, 342.0, 343.0, 344.0, 345.0, 346.0, 347.0, 348.0, 349.0, 350.0, 351.0, 352.0, 353.0, 354.0, 355.0, 356.0, 357.0, 358.0, 359.0, 360.0, 361.0, 362.0, 363.0, 364.0, 365.0, 366.0, 367.0, 368.0, 369.0, 370.0, 371.0, 372.0, 373.0, 374.0, 375.0, 376.0, 377.0, 378.0, 379.0, 380.0, 381.0, 382.0, 383.0, 384.0, 385.0, 386.0, 387.0, 388.0, 389.0, 390.0, 391.0, 392.0, 393.0, 394.0, 395.0, 396.0, 397.0, 398.0, 399.0, 400.0, 401.0, 402.0, 403.0, 404.0, 405.0, 406.0, 407.0, 408.0, 409.0, 410.0, 411.0, 412.0, 413.0, 414.0, 415.0, 416.0, 417.0, 418.0, 419.0, 420.0, 421.0, 422.0, 423.0, 424.0, 425.0, 426.0, 427.0, 428.0, 429.0, 430.0, 431.0, 432.0, 433.0, 434.0, 435.0, 436.0, 437.0, 438.0, 439.0, 440.0, 441.0, 442.0, 443.0, 444.0, 445.0, 446.0, 447.0, 448.0, 449.0, 450.0, 451.0, 452.0, 453.0, 454.0, 455.0, 456.0, 457.0, 458.0, 459.0, 460.0, 461.0, 462.0, 463.0, 464.0, 465.0, 466.0, 467.0, 468.0, 469.0, 470.0, 471.0, 472.0, 473.0, 474.0, 475.0, 476.0, 477.0, 478.0, 479.0, 480.0, 481.0, 482.0, 483.0, 484.0, 485.0, 486.0, 487.0, 488.0, 489.0, 490.0, 491.0, 492.0, 493.0, 494.0, 495.0, 496.0, 497.0, 498.0, 499.0, 500.0, 501.0, 502.0, 503.0, 504.0, 505.0, 506.0, 507.0, 508.0, 509.0, 510.0, 511.0, 512.0, 513.0, 514.0, 515.0, 516.0, 517.0, 518.0, 519.0, 520.0, 521.0, 522.0, 523.0, 524.0, 525.0, 526.0, 527.0, 528.0, 529.0, 530.0, 531.0, 532.0, 533.0, 534.0, 535.0, 536.0, 537.0, 538.0, 539.0, 540.0, 541.0, 542.0, 543.0, 544.0, 545.0, 546.0, 547.0, 548.0, 549.0, 550.0, 551.0, 552.0, 553.0, 554.0, 555.0, 556.0, 557.0, 558.0, 559.0, 560.0, 561.0, 562.0, 563.0, 564.0, 565.0, 566.0, 567.0, 568.0, 569.0, 570.0, 571.0, 572.0, 573.0, 574.0, 575.0, 576.0, 577.0, 578.0, 579.0, 580.0, 581.0, 582.0, 583.0, 584.0, 585.0, 586.0, 587.0, 588.0, 589.0, 590.0, 591.0, 592.0, 593.0, 594.0, 595.0, 596.0, 597.0, 598.0, 599.0, 600.0, 601.0, 602.0, 603.0, 604.0, 605.0, 606.0, 607.0, 608.0, 609.0, 610.0, 611.0, 612.0, 613.0, 614.0, 615.0, 616.0, 617.0, 618.0, 619.0, 620.0, 621.0, 622.0, 623.0, 624.0, 625.0, 626.0, 627.0, 628.0, 629.0, 630.0, 631.0, 632.0, 633.0, 634.0, 635.0, 636.0, 637.0, 638.0, 639.0, 640.0, 641.0, 642.0, 643.0, 644.0, 645.0, 646.0, 647.0, 648.0, 649.0, 650.0, 651.0, 652.0, 653.0, 654.0, 655.0, 656.0, 657.0, 658.0, 659.0, 660.0, 661.0, 662.0, 663.0, 664.0, 665.0, 666.0, 667.0, 668.0, 669.0, 670.0, 671.0, 672.0, 673.0, 674.0, 675.0, 676.0, 677.0, 678.0, 679.0, 680.0, 681.0, 682.0, 683.0, 684.0, 685.0, 686.0, 687.0, 688.0, 689.0, 690.0, 691.0, 692.0, 693.0, 694.0, 695.0, 696.0, 697.0, 698.0, 699.0, 700.0, 701.0, 702.0, 703.0, 704.0, 705.0, 706.0, 707.0, 708.0, 709.0, 710.0, 711.0, 712.0, 713.0, 714.0, 715.0, 716.0, 717.0, 718.0, 719.0, 720.0, 721.0, 722.0, 723.0, 724.0, 725.0, 726.0, 727.0, 728.0, 729.0, 730.0, 731.0, 732.0, 733.0, 734.0, 735.0, 736.0, 737.0, 738.0, 739.0, 740.0, 741.0, 742.0, 743.0, 744.0, 745.0, 746.0, 747.0, 748.0, 749.0, 750.0, 751.0, 752.0, 753.0, 754.0, 755.0, 756.0, 757.0, 758.0, 759.0, 760.0, 761.0, 762.0, 763.0, 764.0, 765.0, 766.0, 767.0, 768.0, 769.0, 770.0, 771.0, 772.0, 773.0, 774.0, 775.0, 776.0, 777.0, 778.0, 779.0, 780.0, 781.0, 782.0, 783.0, 784.0, 785.0, 786.0, 787.0, 788.0, 789.0, 790.0, 791.0, 792.0, 793.0, 794.0, 795.0, 796.0, 797.0, 798.0, 799.0, 800.0, 801.0, 802.0, 803.0, 804.0, 805.0, 806.0, 807.0, 808.0, 809.0, 810.0, 811.0, 812.0, 813.0, 814.0, 815.0, 816.0, 817.0, 818.0, 819.0, 820.0, 821.0, 822.0, 823.0, 824.0, 825.0, 826.0, 827.0, 828.0, 829.0, 830.0, 831.0, 832.0, 833.0, 834.0, 835.0, 836.0, 837.0, 838.0, 839.0, 840.0, 841.0, 842.0, 843.0, 844.0, 845.0, 846.0, 847.0, 848.0, 849.0, 850.0, 851.0, 852.0, 853.0, 854.0, 855.0, 856.0, 857.0, 858.0, 859.0, 860.0, 861.0, 862.0, 863.0, 864.0, 865.0, 866.0, 867.0, 868.0, 869.0, 870.0, 871.0, 872.0, 873.0, 874.0, 875.0, 876.0, 877.0, 878.0, 879.0, 880.0, 881.0, 882.0, 883.0, 884.0, 885.0, 886.0, 887.0, 888.0, 889.0, 890.0, 891.0, 892.0, 893.0, 894.0, 895.0, 896.0, 897.0, 898.0, 899.0, 900.0, 901.0, 902.0, 903.0, 904.0, 905.0, 906.0, 907.0, 908.0, 909.0, 910.0, 911.0, 912.0, 913.0, 914.0, 915.0, 916.0, 917.0, 918.0, 919.0, 920.0, 921.0, 922.0, 923.0, 924.0, 925.0, 926.0, 927.0, 928.0, 929.0, 930.0, 931.0, 932.0, 933.0, 934.0, 935.0, 936.0, 937.0, 938.0, 939.0, 940.0, 941.0, 942.0, 943.0, 944.0, 945.0, 946.0, 947.0, 948.0, 949.0, 950.0, 951.0, 952.0, 953.0, 954.0, 955.0, 956.0, 957.0, 958.0, 959.0, 960.0, 961.0, 962.0, 963.0, 964.0, 965.0, 966.0, 967.0, 968.0, 969.0, 970.0, 971.0, 972.0, 973.0, 974.0, 975.0, 976.0, 977.0, 978.0, 979.0, 980.0, 981.0, 982.0, 983.0, 984.0, 985.0, 986.0, 987.0, 988.0, 989.0, 990.0, 991.0, 992.0, 993.0, 994.0, 995.0, 996.0, 997.0, 998.0, 999.0, 1000.0]
    binLowE = numpy.arrange(0.,1001.,1.)
    return binLowE


def LogSpace(Min, Max, N):
  spacing = (float(Max) - float(Min))/float(N-1)
  bins = [10.**(spacing*i+float(Min)) for i in range(0,N-1)]
  bins.append(10**Max)
  return bins
