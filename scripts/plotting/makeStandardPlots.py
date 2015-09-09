#!/usr/bin/env python
import os, sys, glob, copy, subprocess
import time
import argparse
import plotUtils
import AtlasStyle
from collections import defaultdict
from math import sqrt, log, isnan, isinf, fabs, exp
import ROOT


#
#put argparse before ROOT call.  This allows for argparse help options to be printed properly (otherwise pyroot hijacks --help) and allows -b option to be forwarded to pyroot
parser = argparse.ArgumentParser(description="%prog [options]", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-b", dest='b', action='store_true', default=False, help="Batch mode for PyRoot")
parser.add_argument("-v", dest='v', action='store_true', default=False, help="Verbose mode for debugging")
parser.add_argument("--plotDir", dest='plotDir', default="sel_mu_4j_2b", help="TDirectory to search for plots in ROOT file.  By default no directory")


parser.add_argument("--plotPartial", dest='plotPartial', action='store_true', default=False, help="Plot all histograms, even if some sample types do not contain the histogram (i.e. truth for data)")
parser.add_argument("--plotRatio", dest='plotRatio', action='store_true', default=False, help="Add ratio plot below 1D plots")
parser.add_argument("--ratioWRT", dest='ratioWRT', default='data', help="Do ratio wrt data, bkg, or signal")
parser.add_argument("--allRebin", dest='allRebin', action='store_true', default=False, help="Rebin every histogram that does not have a rebin1D applied")
parser.add_argument("--allRebinFactor", dest='allRebinFactor', default='2', help="Value to rebin by if using allRebin")
parser.add_argument("--unitNormalize", dest='unitNormalize', action='store_true', default=False, help="Draw unit normalization")
parser.add_argument("--normToData", dest='normToData', action='store_true', default=False, help="normalize all files to the first data file")
parser.add_argument("--normToBkg", dest='normToBkg', action='store_true', default=False, help="Normalize all files to the first background File")
parser.add_argument("--differential", dest='differential', action='store_true', default=False, help="Draw differential")
parser.add_argument("--plotDijetSlices", dest='plotDijetSlices', action='store_true', default=False, help="Plot dijet only with each slice a different color")
parser.add_argument("--stackBkg", dest='stackBkg', action='store_true', default=False, help="Stack the backgrounds together")
parser.add_argument("--noStackSignal", dest='noStackSignal', action='store_true', default=False, help="When signal and background are both present, do not stack them")
parser.add_argument("--inDir", dest='inDir', default="./", help="Default directory to find all histograms")
parser.add_argument("--dataDir", dest='dataDir', default=None, help="Directory to find data histograms")
parser.add_argument("--bkgDir", dest='bkgDir', default=None, help="Directory to find bkg histograms")
parser.add_argument("--signalDir", dest='signalDir', default=None, help="Directory to find signal histograms")
parser.add_argument("--outDir", dest='outDir', default="./plots",
                    help="Name directory to store plots")
parser.add_argument("--outputTag", dest='outputTag', default="newStudy", help="Output Tag Name for plots")
parser.add_argument("--outputVersion", dest='outputVersion', default="", help="Add a version number to the end of the plots.")
parser.add_argument("--plotText", dest='plotText', default="", help="Additional text to be written to the plots")
parser.add_argument("--dataType", dest='dataType', default='', help="Name of data type to be used in plotting. Seperate inputs by a comma, tags by a +")
parser.add_argument("--bkgType", dest='bkgType', default='', help="Name of mc type to be used in plotting.  Seperate inputs by a comma, tags by a +")
parser.add_argument("--signalType", dest='signalType', default="", help="Name of signal type to be used in plotting.  Seperate inputs by a comma, tags by a +")
parser.add_argument("--scaleBinWidth", dest='scaleBinWidth', action='store_true', default=False, help="scale bins by bin widthn")

parser.add_argument("--noRecommendedRebin", dest='noRecommendedRebin', action='store_true', default=False, help=" DO NOT use the recommended rebins")
parser.add_argument("--noRecommendedRerange", dest='noRecommendedRerange', action='store_true', default=False, help=" DO NOT use the recommended rerange of x-axis")
parser.add_argument('--rebin1D', dest='rebin1D', nargs='+', help='Variable then rebin value, i.e. "mjj,2 m3j,4"')
parser.add_argument('--rebin2D', dest='rebin2D', nargs='+', help='Variable then rebin value, i.e. "mjj,2 m3j,4"')
parser.add_argument('--range1D', dest='range1D', nargs='+', help='Variable followed by min and max value, i.e. "mjj,10,400 eta,-1,1"')
parser.add_argument('--range1Dy', dest='range1Dy', nargs='+', help='Variable followed by min and max value, i.e. "jet_dRtrk__NPixelHits,3.6,4.3 jet_dRtrk__NSCTHits,7.7,9.0"')
parser.add_argument('--range2D', dest='range2D', nargs='+', help='Variable followed by min and max value"')
parser.add_argument('--range2Dy', dest='range2Dy', nargs='+', help='Variable followed by min and max value"')
parser.add_argument('--ratioRange', dest='ratioRange', nargs='+', help='Variable followed by min and max value, i.e. "mjj,10,400 eta,-0.5,0.5"')
parser.add_argument('--ratioRangeMax', dest='ratioRangeMax', default=1.0, help='Max value of ratio plot range.  If this and ratioRangeMin is 0, it uses ROOT defaults')
parser.add_argument('--ratioRangeMin', dest='ratioRangeMin', default=-1., help='Min value of ratio plot range.  If this and ratioRangeMax is 0, it uses ROOT defaults')
parser.add_argument('--ratioRange2DMax', dest='ratioRange2DMax', default=1.1999, help='Max value of ratio plot range.  If this and ratioRange2DMin is 0, it uses ROOT defaults')
parser.add_argument('--ratioRange2DMin', dest='ratioRange2DMin', default=0.8, help='Min value of ratio plot range.  If this and ratioRange2DMax is 0, it uses ROOT defaults')
parser.add_argument("--lumi", dest='lumi', type=float, default=0, help="Scale by Luminosity")

parser.add_argument("--writeMerged", dest='writeMerged', action='store_true', default=False)
parser.add_argument('--extraText', dest='extraText', nargs='+', help='add an extra line of text to the canvas, i.e. "NumTrkPt500PV,p_{T}^{trk}>500MeV"')


#------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------


args = parser.parse_args()
if len(args.outputVersion) > 0:
  args.outputVersion = "_" + args.outputVersion
if not os.path.exists(args.outDir):
  os.mkdir(args.outDir)

AtlasStyle.SetAtlasStyle()


#### TODO Rebinning and reranging stuff####
## Rebinning and ranges, make global for now
rebin1D, rebin2D, range1D, range2D, ratioRange, range2Dy, range1Dy, extraText = [], [], [], [], [], [], [], []

## Add user ranges first as the first gets chosen in case of conflict
if (args.rebin1D):
  rebin1D += args.rebin1D
if (args.rebin2D):
  rebin2D += args.rebin2D
if (args.range1D):
  range1D += args.range1D
if (args.range1Dy):
  range1Dy += args.range1Dy
if (args.range2D):
  range2D += args.range2D
if (args.range2Dy):
  range2Dy += args.range2Dy
if (args.ratioRange):
  ratioRange += args.ratioRange
if (args.extraText):
  extraText += args.extraText

#Add recommended rebins if not explicitely removed ##
if not args.noRecommendedRebin:
  rebin1D += [ "first_jet_eta,2", "second_jet_eta,2", "jet_eta,2","first_jet_phi,2", "second_jet_phi,2", "jet_phi,2" ]
##if not args.noRecommendedRebin:
##  rebin1D += [ "deltaPhi,4", "AverageLAr,4", "EMB2,4", "FracSamplingMax,4", "Jvt_,4", "phi,4", "minDeltaR,4"]
#  rebin1D += [ "EMB2,4", "minDeltaR,4"]
if not args.noRecommendedRerange:
  # if jet in name - exact match, otherwise look for in name
  if "angular" in args.outDir: range1D += [ "mjj,2000,10000"]
  if "resonance" in args.outDir: range1D += [ "mjj,1000,10000"]
  else: range1D += [ "mjj,1000,10000"]
  range1D += ["first_jet_pt,350,6000","second_jet_pt,200,6000" ]
  range1D += [ "m3j,800,7000","m12,800,7000","m13,400,7000","m23,400,7000" ]
  range2D += [ "mjj,800,7000","m3j,800,7000","m12,800,7000","m13,800,7000","m23,800,7000","jet_E,0,2000" ]
  range1D += ["HT2,600,3200","pTjj,0,2000"]
#  range1D += ["pt,0,1000"]

#  ratioRange += []
extraText += ["TrackWidthPt500PV,p_{T}^{trk} > 500 MeV", "TrackWidthPt1000PV,p_{T}^{trk} > 1000 MeV", "NumTrkPt500PV,p_{T}^{trk} > 500 MeV", "NumTrkPt1000PV,p_{T}^{trk} > 1000 MeV", "SumPtTrkPt500PVoverPt,p_{T}^{trk} > 500 MeV","SumPtTrkPt1000PVoverPt,p_{T}^{trk} > 1000 MeV"]


########################## Histogram Retrieval Code #########################################
def getPlotList():
  print("getPlotList")

  if not args.dataDir:  args.dataDir = args.inDir
  if not args.bkgDir:  args.bkgDir = args.inDir
  if not args.signalDir:  args.signalDir = args.inDir

  ########## Get all fileNames to use ##########
  SampleNames, SampleTypes, SampleFiles = [], [], []
  ## Get All Background Files ##
  if len(args.bkgType) > 0:
    args.bkgType = args.bkgType.split(',')
    for thisBkgType in args.bkgType:
      if ':' in thisBkgType:
        thisBkgName = thisBkgType.split(':')[0]
        thisBkgType = thisBkgType.split(':')[1]
      else:
        thisBkgName = thisBkgType
      SampleNames.append( thisBkgName )
      SampleTypes.append( "bkg" )
      SampleFiles.append( getFileNames( args.bkgDir, thisBkgType.split('+') ) )

  ## Get All Signal Files ##
  if len(args.signalType) > 0:
    args.signalType = args.signalType.split(',')
    for thisSigType in args.signalType:
      if ':' in thisSigType:
        thisSigName = thisSigType.split(':')[0]
        thisSigType = thisSigType.split(':')[1]
      else:
        thisSigName = thisSigType
      SampleNames.append( thisSigName)
      SampleTypes.append( "signal" )
      SampleFiles.append( getFileNames( args.signalDir, thisSigType.split('+') ) )

  #TODO#### Keep Data Last!! ####
  if len(args.dataType) > 0:
    args.dataType = list(args.dataType.split(','))
    if args.v: print args.dataType
    for thisDataType in args.dataType:
      if ':' in thisDataType:
        thisDataName = thisDataType.split(':')[0]
        thisDataType = thisDataType.split(':')[1]
      else:
        thisDataName = thisDataType
      SampleNames.append( thisDataName )
      SampleTypes.append( "data" )
      SampleFiles.append( getFileNames( args.dataDir, thisDataType.split('+') ) )

  ##### Get histogram list from first file #####
  HistNames = getHistNames( SampleFiles )

  ##### Get all histograms #####
  Hists = []
  for iS, fileList in enumerate(SampleFiles):
    Hists.append( getHists(SampleNames[iS], fileList, HistNames) )

  ## TODO ## Properly create stacked histograms

  return SampleNames, SampleTypes, HistNames, Hists



############## Get File List #############################
def getFileNames( histDir, histFileTags ):

###
  #histFileNames = plotUtils.getFileList( histDir, histFileTags )
  thisHistDir = histDir
  thisHistFileTags = histFileTags
  thisHistFileTags.append(".root") #must be root files
  thisHistDir += '/'

  ## Get List of Files that match the tag ##
  histFileNames = []
  for f in os.listdir(histDir):
    if not os.path.isfile( os.path.join(histDir,f) ): continue

    passed = True
    for tag in histFileTags:
      if '=' in tag:
        if not any(splitTag in f for splitTag in list(tag.split('='))):
          passed = False
      else:
        if not tag in f:
          passed = False

    if passed:
      histFileNames.append( os.path.join(histDir,f) )

  histFileNames.sort()
  if len(histFileNames)<1:
    print "ERROR:  There are no histogram files of requested type", histFileTags
    exit(1)

  elif args.v: print histFileNames

  return histFileNames

################# Get Histogram List ################################
def getHistNames( inFileNames ):
#TODO need to check that they're actually histograms!!

  ## Get names of all histograms in all files ##
  ## Histogram list will be all those common to all files ##

  allFileNames = sum( inFileNames, [])
  allHistNames = []
  for inFileName in allFileNames:
    allHistNames.append([])
    inFile = ROOT.TFile(inFileName, 'READ')
    if len(args.plotDir) > 0:
      plotDir = inFile.Get(args.plotDir)
      if not plotDir:
        print "ERROR, Couldn't find TDirectory", args.plotDir, "in", inFileName
        exit(1)
    else:
      plotDir = inFile
    keys = plotDir.GetListOfKeys()
    for key in keys:
      allHistNames[-1].append(args.plotDir+'/'+key.GetName())

    inFile.Close()

  ## Hist Names must be common to all files ##
  histNames = []
  for histName in allHistNames[0]:
    if all( histName in histNameList for histNameList in allHistNames):
      histNames.append(histName)

  return histNames

################# Combine all samples ##############################
def getHists( sampleName, fileList, histNames ):

  CombinedHists = []

  for iF, fileName in enumerate(fileList):
    file = ROOT.TFile.Open(fileName, "READ")

    for iH, histName in enumerate(histNames):
      thisHist = file.Get(histName)
      if iF == 0:
        CombinedHists.append( thisHist.Clone( sampleName+'_'+thisHist.GetName() ) ) #Unique name for each type
        CombinedHists[-1].SetDirectory( 0 ) # just in case...
      else:
        CombinedHists[iH].Add( thisHist )

    file.Close()

#??    ##Need to add clone now else get's rebinned ##
#??    CombinedHists.append(copy.copy(total))
#??    CombinedHists[-1].SetName( total.GetName()+"_final")

  return CombinedHists

## Ideas to Add From before ###

##  if lumi > 0: hist.Scale( lumi )

  ### bring in overflow
  ##nbinX = hist.GetNbinsX()
  ##if hist.GetBinContent( nbinX + 1 ) > 0:
  ##  hist.SetBinContent( nbinX, hist.GetBinContent( nbinX ) + hist.GetBinContent( nbinX + 1 ) )
  ##  newError = sqrt( hist.GetBinError( nbinX )*hist.GetBinError( nbinX ) + hist.GetBinError( nbinX + 1 )*hist.GetBinError( nbinX + 1) )
  ##  hist.SetBinError( nbinX, newError )


##  if args.writeMerged:
##    f = ROOT.TFile(args.histDirData+"/"+mergeFileTag+"_mergedFiles.root","recreate")
##    for hist in CombinedHists:
##      hist.Write()
##    f.Close()




##################################### Plotting Code ###########################################
def plotAll( SampleNames, SampleTypes, HistNames, Hists):
  print "plotAll"

  ### Align histograms and reorder so histName is first dimension ###
  #Hists are [fileType][histName]
  newHistList = []  #Will be [histName][fileType]
  for iHist, thisHistName in enumerate(HistNames):
    newHistList.append([])

    for iSample, thisSample in enumerate(SampleTypes):
      newHistList[-1].append( Hists[iSample][iHist] )

  Hists = newHistList

#  for iHist, histName in enumerate(newHistNames):
#    print  "-----------------------------"
#    for iBkg, thisHistName in enumerate(histName):
#      print thisHistName, newHistList[iHist][iBkg]




  for iHist, histName in enumerate(HistNames):
    theseHists = Hists[iHist]
    theseTypes = SampleTypes
    theseNames = SampleNames
    formatHists(theseTypes, theseHists)
    lumiScale = getLumiDifference(theseTypes, theseHists)
    if(args.stackBkg):
      theseTypes, theseHists, theseNames = stackBkg(theseTypes, theseHists, theseNames)
    scaleHists(theseTypes, theseHists, lumiScale)
    if ( type(theseHists[0]) == ROOT.TH1D or type(theseHists[0]) == ROOT.TH1F or type(theseHists[0]) == ROOT.THStack ):
      plot1D( theseHists, theseTypes, theseNames )

#    plotHists( SampleNames, histsToPlot, histName[0], HistTypes, args.outputTag, args.outputVersion )

def stackBkg(SampleTypes, Hists, Names):

  newSampleTypes = []
  newHists = []
  newNames = []

  newSampleTypes.append( "stack" )
  newHists.append( ROOT.THStack() )
  newNames.append( [] )
  newHists[-1].SetName( Hists[SampleTypes.index("bkg")].GetName() )
  for iHist, hist in enumerate(Hists):
    if SampleTypes[iHist] != 'bkg':
      newSampleTypes.append( SampleTypes[iHist] )
      newHists.append( hist )
      newNames.append( Names[iHist] )
    else:
      newHists[-1].Add( hist )
      newNames[0].append( Names[iHist] )

  return newSampleTypes, newHists, newNames

######### Rescale the histograms ###########
def scaleHists( histTypes, hists, lumiScale ):

  ## The following can handle :
  ## Normalizing any number of seperate data and bkg samples to either data or bkg
  ## If normalizing signals to one another, just treat them as bkg!
  ## Normalizing 1 bkg to data, and scaling all signal histograms by the same fraction


# For now if there is a stack - then no normalize?
#In the future maybe normalize each histogram by some sort of sum equation ?!

##  if lumi > 0: hist.Scale( lumi )
  if args.lumi > 0 :
    for iHist, hist in enumerate(hists):
      if histTypes[iHist] == 'bkg':
        hist.Scale( args.lumi )
      elif histTypes[iHist] == 'stack':
        for iStack, stackHist in enumerate(hist.GetHists()):
          stackHist.Scale( args.lumi )

  elif args.normToBkg or args.normToData:
    if not "stack" in histTypes:
      if args.normToBkg:
        iScale = histTypes.index("bkg")
      elif args.normToData:
        iScale = histTypes.index("data")
      scaleNorm = hists[iScale].Integral()

      ## If only 1 bkg and there are signals, then scale signals by the same as the bkg ##
      if args.normToData and (histTypes.count('bkg') == 1) and ('signal' in histTypes) :
        bkgScaleFactor = 1.
        for iHist, hist in enumerate(hists):
          if iHist != iData and hist.Integral() > 0 :
            if histTypes[iHist] == 'bkg':
              bkgScaleFactor = scaleNorm / hist.Integral()
              hist.Scale(bkgScaleFactor)
            elif histTypes[iHist] == 'data':
              hist.Scale( scaleNorm / hist.Integral() )
        for iHist, hist in enumerate(hists):
          if histTypes[iHist] == 'signal':
            hist.Scale(bkgScaleFactor)

      else: ## Just scale the rest
        for iHist, hist in enumerate(hists):
          if iHist != iScale and histTypes[iHist] != "signal" and hist.Integral() > 0:
            hist.Scale( scaleNorm / hist.Integral() )

    else: ## If a stack, treat like 1 bkg + signal case, but 1 bkg = stack
      bkgScaleFactor = 0.
      for iStack, stackHist in enumerate(hists[0].GetHists()):
        bkgScaleFactor += stackHist.Integral()
      if bkgScaleFactor <= 0 :
        return
      if args.normToData:
        iScale = histTypes.index("data")
        scaleNorm = hists[iScale].Integral()
        for iHist, hist in enumerate(hists):
          if iHist == 0:
            for iStack, stackHist in enumerate(hists[iHist].GetHists()):
              stackHist.Scale( scaleNorm / bkgScaleFactor )
          elif histTypes[iHist] == 'data' and hist.Integral() > 0:
            hist.Scale( scaleNorm / hist.Integral() )
          elif histTypes[iHist] == 'signal':
            hist.Scale( scaleNorm / bkgScaleFactor )
      elif args.normToBkg:
        for iHist, hist in enumerate(hists):
          if iHist != 0 and hist.Integral() > 0:
            hist.Scale( bkgScaleFactor / hist.Integral() )

  elif args.unitNormalize or args.differential:
    if "stack" in histTypes:
      print "Error, cannot do unitNormalize or differential with Stacked histograms"
      exit(1)
    for iHist, hist in enumerate(hists):
      if hist.Integral() > 0:
        if args.unitNormalize:
          hist.Scale(1.0/hist.Integral())
        elif args.differential:
          hist.Scale(1.0/hist.Integral(),"width")

  return


#### Plot 1D Histograms ####
def plot1D( Hists, SampleTypes, SampleNames ):

  histName = '_'.join(Hists[0].GetName().split('_')[1:] )
  plotRatio = args.plotRatio

  ## Setup Canvas ##
  c0 = ROOT.TCanvas(histName)
  logx = False
  logy = False
# TODO need a logXList of variables for choosing this.  Get from a config file?
##    #extraText=[]
##    #logXList = [ "mjj", "m3j", "chi", "m12", "m13", "m23" ]   # madd all two-jet mass plots have logX
##    logXList = [ "chi" ]   # madd all two-jet mass plots have logX
##    for v in logXList:
##      if v == hName: logx = True
###      elif v in hName and "for_mjj" in hName : logx = True
##      elif v in hName and not "__" in hName: logx = True
##    if logx: hists[i].GetYaxis().SetMoreLogLabels(1)
##
##    if logx:
##      c0.SetLogx()
##      if (plotRatio):
##        pad1.SetLogx()
##        pad2.SetLogx()
##    else:
##      c0.SetLogx(0)
##      if (plotRatio):
##        pad1.SetLogx(0)
##        pad2.SetLogx(0)

  setMaximum(Hists)

  if plotRatio:
    pad1, pad2, zeroLine, oneLine = getRatioObjects(c0, logx, logy)
    pad1.cd()

  leg = configureLegend(SampleTypes, Hists, SampleNames)
  ### Configure draw string ###
  for iH, hist in enumerate(Hists):
    drawString = ""
    if iH != 0:
      drawString += 'same'
    drawString += 'histe'
    if not "data" == SampleTypes[iH]:
      drawString += 'fe'
    else:
      drawString += 'ep'

    Hists[iH].Draw( drawString )

  if plotRatio:
    pad2.cd()

    ratioHists = [] #Ratio histograms
    iRatioHist = SampleTypes.index(args.ratioWRT)
    for iHist, hist in enumerate(Hists):
      if iHist == iRatioHist: continue

      ## get relevant hists ##
      tmpRatioHist = Hists[iRatioHist].Clone( hist.GetName()+'_ratio' )
      tmpHist = hist.Clone( 'tmp' )

      ## create ratio ##
      if type(tmpHist) == ROOT.THStack:
        tmpStackHist = getCombinedStack( tmpHist )
        for iStack, stackHist in enumerate(tmpHist.GetHists() ):
          if iStack == 0:
            tmpStackHist = stackHist.Clone('tmp2')
          else:
            tmpStackHist.Add( stackHist )
        tmpRatioHist.Add( tmpStackHist, -1. )
        tmpRatioHist.Divide( tmpStackHist )
      else:
        tmpRatioHist.Add( tmpHist, -1. )
        tmpRatioHist.Divide( tmpHist )

      # flip it so excess is still positive on ratio
      if args.ratioWRT == 'bkg' or args.ratioWRT == 'stack':
        tmpRatioHist.Scale( -1.0 )

      ## If ratio value is 0 then there should be no ratio drawn
      for iBin in range(1, tmpRatioHist.GetNbinsX()+1):
        if Hists[iRatioHist].GetBinContent(iBin) == 0:
          tmpRatioHist.SetBinContent(iBin, 0)
          tmpRatioHist.SetBinError(iBin, 0)

      configureRatioHist(tmpHist, tmpRatioHist)
      ratioHists.append( tmpRatioHist )

    for iHist, ratioHist in enumerate(ratioHists):
      ratioHists[iHist].SetStats(0)
      if iHist == 0:
        ratioHists[iHist].DrawCopy("p")
        ratioHists[iHist].SetMarkerSize(0)
        ratioHists[iHist].DrawCopy("same e0")
      else:
        ratioHists[iHist].Draw( "same fhist" )
    zeroLine.Draw("same")

    c0.cd()

  leg.Draw("same")
  AtlasStyle.ATLAS_LABEL(0.20,0.88)
  sqrtSLumiText = getSqrtSLumiText( args.lumi )
  AtlasStyle.myText(0.20,0.82,1, sqrtSLumiText)
  if len(args.plotText)>0:
    AtlasStyle.myText(0.20,0.76,1, args.plotText)

  if any( extraTextString.split(',')[0] in histName for extraTextString in extraText ):
    extraTextString = [extraTextString for extraTextString in extraText if extraTextString.split(',')[0] in histName][0]
    if len(args.plotText)>0:
      AtlasStyle.myText(0.20,0.64, 1,extraTextString.split(',')[1])
    else:
      AtlasStyle.myText(0.20,0.75, 1,extraTextString.split(',')[1])

  c0.Print( args.outDir + "/" + args.outputTag + "_" + histName + args.outputVersion + ".png","png") #,"png")

## TODO Draw log versions?

  if plotRatio:
    pad1.Delete()
    pad2.Delete()
#  c0.Delete()

  return

def configureRatioHist(originalHist, ratioHist):
  if type(originalHist) == ROOT.THStack:
    #originalHist = originalHist.GetHists()[-1]
    ratioHist.SetMarkerColor( ROOT.kBlack )
    ratioHist.SetLineColor( ROOT.kBlack )
    ratioHist.SetFillColor( ROOT.kBlack )
  else:
    ratioHist.SetMarkerColor( originalHist.GetMarkerColor() )
    ratioHist.SetLineColor( originalHist.GetLineColor() )
    ratioHist.SetFillColor( originalHist.GetFillColor() )

  ratioHist.GetYaxis().SetTitleSize( 0.17 )
  ratioHist.GetYaxis().SetLabelSize( 0.17 )
  ratioHist.GetYaxis().SetTitleOffset( 0.4 )
  ratioHist.GetXaxis().SetLabelSize( 0.2 )
  ratioHist.GetXaxis().SetTitleSize( 0.2 )
  ratioHist.GetXaxis().SetTitleOffset( 1 )
  ratioHist.GetYaxis().SetNdivisions(5)
  ratioHist.GetYaxis().SetTitle("#splitline{Relative}{Difference}")
  #ratioHist.GetYaxis().SetTitle("Significance")
  ratioHist.SetMinimum(-1.0)
  ratioHist.SetMaximum(1.0)
  return
def configureLegend(SampleTypes, Hists, SampleNames):
  leg = ROOT.TLegend(0.70,0.7, 0.86, 0.92,"")
  leg.SetTextFont(62)
  leg.SetFillStyle(0)
  leg.SetEntrySeparation(0.0001)

  ## Draw all input histograms ##
  for iHist, hist in enumerate(Hists):
    legendString = ""
    if "data" == SampleTypes[iHist]:
      legendString += 'p'
    else:
      legendString += 'f'

    if "stack" == SampleTypes[iHist]:
      for iStack, stackHist in enumerate(hist.GetHists()):
        leg.AddEntry( stackHist, '{0: <12} {1:.2f}'.format(SampleNames[iHist][iStack],stackHist.Integral()), legendString)
    else:
      leg.AddEntry( hist, '{0: <12} {1:.2f}'.format(SampleNames[iHist],hist.Integral()), legendString)

  return leg


############ Format the histograms ##################
def formatHists( SampleTypes, Hists ):

  #TODO more automatic color selection
  MCColors = [ROOT.kBlue, ROOT.kRed, ROOT.kGreen, ROOT.kOrange, ROOT.kCyan, ROOT.kViolet, ROOT.kYellow, ROOT.kBlack, ROOT.kPink]

  iMC, iData = 0, 0
  for iS, sampleType in enumerate(SampleTypes):
    if "data" in sampleType:
      #print "nothing yet..."
      iData += 1
    else:
      Hists[iS].SetMarkerSize(0.0)
      Hists[iS].SetMarkerColor(MCColors[iMC])
      Hists[iS].SetLineColor(ROOT.kBlack)
      Hists[iS].SetLineWidth(1)
      Hists[iS].SetFillColor(MCColors[iMC])
      #Hists[iS].SetFillColorAlpha(MCColors[iMC], 0)
      #Hists[iS].SetFillStyle(1001)
      iMC += 1

  ### TODO Redo axes here!
##    ## check if the range needs to be changed for this variable
##    ## rangeStrings are like "jet_E,35,150"
##    xmax = xmin = 0
### exact match if jet in name
##
##    if any( rangeString.split(',')[0] in hName and not "jet_" in rangeString.split(',')[0] for rangeString in range1D ):
##      rangeString = [rangeString for rangeString in range1D if rangeString.split(',')[0] in hName][0]
##      xmin = float(rangeString.split(',')[1])
##      xmax = float(rangeString.split(',')[2])
### not exact match if jet not in name
##    if any( rangeString.split(',')[0] == hName and "jet_" in rangeString.split(',')[0] for rangeString in range1D ):
##      rangeString = [rangeString for rangeString in range1D if rangeString.split(',')[0] in hName][0]
##      xmin = float(rangeString.split(',')[1])
##      xmax = float(rangeString.split(',')[2])
##
##
##    ## Rebin before getting y maximum ##
##    rebin = 0
##    if any( rebinString.split(',')[0] in hName for rebinString in rebin1D ):
##      if args.v: print("REBIN " + hName)
##      rebinString = [rebinString for rebinString in rebin1D if rebinString.split(',')[0] in hName][0]
##      rebin = int(rebinString.split(',')[1])
##      for i in range(0,len(hists)):
##        hists[i].Rebin(rebin)
##    elif args.allRebin:
##      for i in range(0,len(hists)):
##        hists[i].Rebin( args.allRebinFactor )
##
##    for i in range(0,len(hists)):
##      scaleBinWidthHere = False
##      if args.scaleBinWidth:
##        for v in ["first_jet_pt","second_jet_pt","mjj"]:
##          if v in hName:
##            hists[i].Scale(1,"width")
##            scaleBinWidthHere = True
##
##
##
##    ## Get Y-axis maximum after rebinning ##
##    ymax = 0
##    ymin = 0
##    #yMinNotZero = 1e8
##    yMinNotZero = 0.00011
#### if no data, use a default
##    if 'data' in histTypes:
##      yMinNotZero = 0.00011
##
##    for i, hist in enumerate(hists):
##      if hist.GetMaximum() > ymax: ymax = hist.GetMaximum()
##      if hist.GetMaximum() < ymin: ymin = hist.GetMinimum()
##      if histTypes[i] == "data":
##        for ibin in range(1, hist.GetNbinsX()+1):
##          content = hist.GetBinContent(ibin)
##          if content > 0:
##            if content < yMinNotZero: yMinNotZero = content
##    ymax *= 1.3
##    if "eta" in hName or "Eta" in hName:
##      ymax *= 1.1



##      hists[i].GetYaxis().SetRangeUser( ymin, ymax )
##      if xmax != 0 or xmin != 0:
##        hists[i].GetXaxis().SetRangeUser( xmin, xmax )
##
##      hists[i].GetYaxis().SetTitle("Events")
##      if scaleBinWidthHere:  hists[i].GetYaxis().SetTitle("Events / GeV")
##      if "deltaPhi" in hName:
##        hists[i].GetXaxis().SetTitle("#Delta#phi(jet_{1},jet_{2})")
##      if "lumiBlock" in hName:
##        hists[i].GetXaxis().SetTitle("Lumi Block")
##      if "jet_" in hName:
##        hists[i].GetXaxis().SetTitle(hists[i].GetXaxis().GetTitle().replace("jet_",""))
##        if not "__" in hName: # 1D
##          if scaleBinWidthHere:  hists[i].GetYaxis().SetTitle("Jets / GeV")
##          else: hists[i].GetYaxis().SetTitle("Jets")
##      if "Number" in hName:
##        hists[i].GetXaxis().SetTitle(hists[i].GetXaxis().GetTitle().replace("Number", " Number"))
##      if "mc" in hName:
##        hists[i].GetXaxis().SetTitle(hists[i].GetXaxis().GetTitle().replace("mc", "MC "))
##      if "EventWeight" in hName:
##        hists[i].GetXaxis().SetTitle(hists[i].GetXaxis().GetTitle().replace("Event", "Event "))
##      if args.unitNormalize and not "__" in hName:
##        hists[i].GetYaxis().SetTitle("Arbitrary Units")
##      if args.differential and not "__" in hName:
##        xaxisName = hists[i].GetXaxis().GetTitle()
##        hists[i].GetYaxis().SetTitle("(1/N)dN/d"+xaxisName)
##
##      # eta ranges
##      xaxisTitle = hists[i].GetTitle()
##      cutoff = xaxisTitle.find("eta")
##      exText = ""
##      if "eta_0_0p8" in xaxisTitle: exText = xaxisTitle[cutoff:].replace("eta_0_0p8","0<|#eta|#leq0.8")
##      if "eta_0p8_1p2" in xaxisTitle: exText = xaxisTitle[cutoff:].replace("eta_0p8_1p2","0.8<|#eta|#leq1.2")
##      if "eta_1p2_1p8" in xaxisTitle: exText = xaxisTitle[cutoff:].replace("eta_1p2_1p8","1.2<|#eta|#leq1.8")
##      if "eta_1p8_2p1" in xaxisTitle: exText = xaxisTitle[cutoff:].replace("eta_1p8_2p1","1.8<|#eta|#leq2.1")
##      if "eta_2p1_2p8" in xaxisTitle: exText = xaxisTitle[cutoff:].replace("eta_2p1_2p8","2.1<|#eta|#leq2.8")
##      if "eta_2p8_3p1" in xaxisTitle: exText = xaxisTitle[cutoff:].replace("eta_2p8_3p1","2.8<|#eta|#leq3.1")
##      if "eta_3p1_4p9" in xaxisTitle: exText = xaxisTitle[cutoff:].replace("eta_3p1_4p9","3.1<|#eta|#leq4.9")
##      if exText: extraText.append(hists[i].GetTitle()+","+exText)


########## Get Lumi Difference ##########
def getLumiDifference( SampleTypes, hists ):
  dataInteg = 0.
  bkgInteg = 0.
  for iHist, hist in enumerate(hists):
    if SampleTypes[iHist] == "data":
      dataInteg += hist.Integral()
    elif SampleTypes[iHist] == 'bkg':
      bkgInteg += hist.Integral()
  if bkgInteg > 0:
    lumiRatio = dataInteg/bkgInteg
  else:
    lumiRatio = None

  return lumiRatio

#### Set Maximum of all hists ####
def setMaximum(Hists):
  for iHist, hist in enumerate(Hists):
    if iHist == 0:
      yMax = hist.GetMaximum()
    else:
      yMax = max(yMax, hist.GetMaximum() )
  yMax *= 1.3
  for iHist, hist in enumerate(Hists):
    hist.SetMaximum( yMax )
  return


#### Get Ratio Objects ####
def getRatioObjects(c0, logX, logY):
  pad1 = ROOT.TPad("pad1","pad1",0,0.3,1,1)
  pad2 = ROOT.TPad("pad2","pad2",0,0.01,1,0.3)
  pad1.Draw()
  pad2.Draw()
  pad1.SetBottomMargin(0)
  pad2.SetTopMargin(0)
  pad1.SetRightMargin(0.05)
  pad2.SetRightMargin(0.05)
  pad2.SetBottomMargin(.5)
  zeroLine = ROOT.TF1("zl0", "0", -50000, 50000 )
  zeroLine.SetTitle("")
  zeroLine.SetLineWidth(1)
  zeroLine.SetLineStyle(7)
  zeroLine.SetLineColor(ROOT.kBlack)
  oneLine = ROOT.TF1("ol0", "1", -50000, 50000 )
  oneLine.SetTitle("")
  oneLine.SetLineWidth(1)
  oneLine.SetLineStyle(7)
  oneLine.SetLineColor(ROOT.kBlack)

  if logX:
    pad1.SetLogx()
    pad2.SetLogx()
  if logY:
    pad1.SetLogy()

  return pad1, pad2, zeroLine, oneLine

#####################################################

##  END      FUNCTIONS TO CALL PLOTNTUPLE.PY      ##
####################################################

def getSqrtSLumiText( lumi ):
  sqrtSLumiText = "#sqrt{s}=13 TeV"
  #sqrtSLumiText = "#sqrt{s}=13 TeV, 6.7 pb^{-1}"
  return sqrtSLumiText

def getCombinedStack( stackHist ):
  for iStack, thisHist in enumerate(stackHist.GetHists() ):
    if iStack == 0:
      combinedHist = thisHist.Clone('tmp2')
    else:
      combinedHist.Add( thisHist )
  return combinedHist

if __name__ == "__main__":
  args.outputTag = args.outputTag+'_'+args.plotDir
  SampleNames, SampleTypes, HistNames, Hists = getPlotList()
  plotAll( SampleNames, SampleTypes, HistNames, Hists )

