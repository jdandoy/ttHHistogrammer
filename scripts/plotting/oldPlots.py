#!/usr/bin/env python
import os, sys, glob, copy, subprocess
import time
import argparse
import plotUtils
import AtlasStyle
import ROOT
from collections import defaultdict
from math import sqrt, log, isnan, isinf, fabs, exp

##################################################
##################################################
# THIS script is used to loop over a set of files
# and call the standard histogram filling script
# after all the files are done, plots can be made
# creating and filling the  histograms is optional
##################################################
##################################################

#
#put argparse before ROOT call.  This allows for argparse help options to be printed properly (otherwise pyroot hijacks --help) and allows -b option to be forwarded to pyroot
parser = argparse.ArgumentParser(description="%prog [options]", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-b", dest='b', action='store_true', default=False, help="Batch mode for PyRoot")
parser.add_argument("-v", dest='v', action='store_true', default=False, help="Verbose mode for debugging")
parser.add_argument("--plotPartial", dest='plotPartial', action='store_true', default=False, help="Plot all histograms, even if some sample types do not contain the histogram (i.e. truth for data)")
parser.add_argument("--plotRatio", dest='plotRatio', action='store_true', default=False, help="Add ratio plot below 1D plots")
parser.add_argument("--ratioWRT", dest='ratioWRT', default='data', help="Do ratio wrt data, bkg, or signal")
parser.add_argument("--allRebin", dest='allRebin', action='store_true', default=False, help="Rebin every histogram that does not have a rebin1D applied")
parser.add_argument("--allRebinFactor", dest='allRebinFactor', default='2', help="Value to rebin by if using allRebin")
parser.add_argument("--unitNormalize", dest='unitNormalize', action='store_true', default=False, help="Draw unit normalization")
parser.add_argument("--normToData", dest='normToData', action='store_true', default=False, help="normalize all background files to the single data file")
parser.add_argument("--normToMC", dest='normToMC', action='store_true', default=False, help="Normalize to first bkgd")
parser.add_argument("--differential", dest='differential', action='store_true', default=False, help="Draw differential")
parser.add_argument("--plotDijetSlices", dest='plotDijetSlices', action='store_true', default=False, help="Plot dijet only with each slice a different color")
parser.add_argument("--noStackSignal", dest='noStackSignal', action='store_true', default=False, help="When signal and background are both present, do not stack them")
parser.add_argument("--histDir", dest='histDir', default="./histograms",
                    help="Name directory to store/find histograms")
parser.add_argument("--histDirData", dest='histDirData', default="none",
                    help="Name directory to store/find histograms")
parser.add_argument("--histDirMC", dest='histDirMC', default="none",
                    help="Name directory to store/find histograms")
parser.add_argument("--plotDir", dest='plotDir', default="./plots",
                    help="Name directory to store plots")
parser.add_argument("--outputTag", dest='outputTag', default="newStudy", help="Output Tag Name for plots")
parser.add_argument("--outputVersion", dest='outputVersion', default="", help="Add a version number to the end of the plots.")
parser.add_argument("--plotText", dest='plotText', default="", help="Additional text to be written to the plots")
parser.add_argument("--dataType", dest='dataType', default='', help="Name of data type to be used in plotting. Seperate inputs by a comma, tags by a +")
parser.add_argument("--bkgType", dest='bkgType', default='', help="Name of mc type to be used in plotting.  Seperate inputs by a comma, tags by a +")
parser.add_argument("--signalType", dest='signalType', default="", help="Name of signal type to be used in plotting.  Seperate inputs by a comma, tags by a +")
parser.add_argument("--bkgJESType", dest='bkgJESType', default='', help="Name of mc JES type to be used in plotting.  Seperate inputs by a comma, tags by a +")

parser.add_argument("--include_JES_bands", dest='include_JES_bands', action='store_true', default=False, help="")

parser.add_argument("--deriveRW", dest='deriveRW', default="", help="Derive rewighting for the given variable") # Choose variable

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
parser.add_argument("--lumi", dest='lumi', type=float, default=0.072, help="Desired Luminosity")

parser.add_argument("--writeMerged", dest='writeMerged', action='store_true', default=False)
parser.add_argument('--extraText', dest='extraText', nargs='+', help='add an extra line of text to the canvas, i.e. "NumTrkPt500PV,p_{T}^{trk}>500MeV"')
#parser.add_argument("--plotAll", dest='plotAll', action='store_true', default=False, help="Plot all tree entries.  This will not plot vector branches")
#parser.add_argument("--plotAllVector", dest='plotAllVector', action='store_true', default=False, help="Plot all tree entries for branches of vectors")
#parser.add_argument("--fillJetPlots", dest='fillJetPlots', action='store_true', default=False, help="Fill plots for individual jets (slow!)")
#parser.add_argument("--nJetToPlot", dest='nJetToPlot', default=2, type=int, help="Number of jets to put in jet plots (-1 is all)")
#parser.add_argument("--nBins", dest='nBins', default=100, type=int, help="Default number of bins to be used for 1D histograms added on the fly")
parser.add_argument("--do_massPartonPlots", dest='do_massPartonPlots', action='store_true', default=False, help="Include plots of mjj split by incoming and outgoing parton")


#------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------


args = parser.parse_args()
if len(args.outputVersion) > 0:
  args.outputVersion = "_" + args.outputVersion

AtlasStyle.SetAtlasStyle()

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
  if "angular" in args.plotDir: range1D += [ "mjj,2000,10000"]
  if "resonance" in args.plotDir: range1D += [ "mjj,1000,10000"]
  else: range1D += [ "mjj,1000,10000"]
  range1D += ["first_jet_pt,350,6000","second_jet_pt,200,6000" ]
  range1D += [ "m3j,800,7000","m12,800,7000","m13,400,7000","m23,400,7000" ]
  range2D += [ "mjj,800,7000","m3j,800,7000","m12,800,7000","m13,800,7000","m23,800,7000","jet_E,0,2000" ]
  range1D += ["HT2,600,3200","pTjj,0,2000"]
#  range1D += ["pt,0,1000"]

#  ratioRange += []
extraText += ["TrackWidthPt500PV,p_{T}^{trk} > 500 MeV", "TrackWidthPt1000PV,p_{T}^{trk} > 1000 MeV", "NumTrkPt500PV,p_{T}^{trk} > 500 MeV", "NumTrkPt1000PV,p_{T}^{trk} > 1000 MeV", "SumPtTrkPt500PVoverPt,p_{T}^{trk} > 500 MeV","SumPtTrkPt1000PVoverPt,p_{T}^{trk} > 1000 MeV"]


#####################################################
#  Begin Plotting Code                              #
#####################################################
def getPlotLists():
    print("getPlotLists")

    #set MC and Data histogram directories to generaral args.histDir in case the user is still placing all file in one directory as was the only option pre-June 22
    if args.histDirMC == "none": args.histDirMC = args.histDir
    if args.histDirData == "none": args.histDirData = args.histDir

    Names, Hists, HistNames, HistTypes = [], [], [], []


    ## Get All Background Files ##
    if len(args.bkgType) > 0:
      args.bkgType = args.bkgType.split(',')
      for thisBkgType in args.bkgType:
        theseTags = thisBkgType.split('+')
        if args.include_JES_bands: theseTags.append("nominal")
        (theseFiles, theseHistNames) = getRelevantHistFiles( args.histDirMC, theseTags )

        Names.append( thisBkgType)
        Hists.append( mergeFiles( theseFiles, theseHistNames, thisBkgType, args.plotDijetSlices, args.lumi,thisBkgType.replace('+','_') ) )
        HistNames.append( theseHistNames )
        HistTypes.append( "bkg" )



    ## Get All Background JES Files ##
    if len(args.bkgJESType) > 0:
      args.bkgJESType = args.bkgJESType.split(',')
      for thisBkgJESType in args.bkgJESType:
        theseTags = thisBkgJESType.split('+')
        (theseFiles, theseHistNames) = getRelevantHistFiles( args.histDirMC, theseTags )

        Names.append( thisBkgJESType)
        Hists.append( mergeFiles( theseFiles, theseHistNames, thisBkgJESType, args.plotDijetSlices, args.lumi,thisBkgJESType.replace('+','_') ) )
        HistNames.append( theseHistNames )
        HistTypes.append( "bkgJES" )

    ## Get All Signal Files ##
    if len(args.signalType) > 0:
      args.signalType = args.signalType.split(',')
      for thisSigType in args.signalType:
        theseTags = thisSigType.split('+')
        (theseFiles, theseHistNames) = getRelevantHistFiles( args.histDirMC, theseTags )

        Names.append( thisSigType)
        Hists.append( mergeFiles( theseFiles, theseHistNames, thisSigType, False, args.lumi,thisSigType.replace('+','_') ) )
        HistNames.append( theseHistNames )
        HistTypes.append( "signal" )

    ##### Keep Data Last!! ####
    if len(args.dataType) > 0:
      args.dataType = list(args.dataType.split(','))
      if args.v: print args.dataType
      for thisDataType in args.dataType:
        theseTags = thisDataType.split('+')
        (theseFiles, theseHistNames) = getRelevantHistFiles( args.histDirData, theseTags )
        Names.append( thisDataType )
        Hists.append( mergeFiles( theseFiles, theseHistNames, thisDataType, False, -1.0, thisDataType.replace('+','_') ) )
        HistNames.append( theseHistNames )
        HistTypes.append( "data" )

    do_Plotting( Names, Hists, HistNames, HistTypes)

#----------------------------------------------------

def do_Plotting( Names, Hists, HistNames, HistTypes):

  print "HISTS", Hists
  ############# Reformat and match histogram names ###########

  ## collect all potential histogram names ##
  allHistNames = []
  for iBkg, Name in enumerate(HistNames):
    allHistNames += HistNames[iBkg]

  ## Choose only unique histogram names ##
  allHistNames = list(set(allHistNames))


  ### Align histograms and reorder so histName is first dimension ###
  #HistNames, Hists are [fileType][histName]
  newHistNames, newHistList = [], []  #[histName][fileType]
  for thisAllHistName in allHistNames:
    newHistNames.append([])
    newHistList.append([])

    for iBkg, thisHistNames in enumerate(HistNames):
      if thisAllHistName in thisHistNames:
        iHist = thisHistNames.index( thisAllHistName )
        newHistNames[-1].append( HistNames[iBkg][iHist] )
        newHistList[-1].append( Hists[iBkg][iHist] )
      else:
        newHistNames[-1].append( thisAllHistName )
        newHistList[-1].append( None )

#  for iHist, histName in enumerate(newHistNames):
#    print  "-----------------------------"
#    for iBkg, thisHistName in enumerate(histName):
#      print thisHistName, newHistList[iHist][iBkg]


  totalBkgColors = [ROOT.kBlue, ROOT.kRed, ROOT.kGreen, ROOT.kOrange, ROOT.kCyan, ROOT.kViolet, ROOT.kYellow]

  if args.include_JES_bands:  totalBkgColors = [ROOT.kBlue, ROOT.kRed, ROOT.kGreen, ROOT.kOrange, ROOT.kCyan, ROOT.kViolet, ROOT.kYellow]

  for iHist, histName in enumerate(newHistNames):
    #rwVar = "averageInteractionsPerCrossing"
    if not args.deriveRW in histName[0]: continue


    histsToPlot = []
    for iType, thisType in enumerate(HistTypes):
      if ( newHistList[iHist][iType] ): #if it exists
        if len(args.dataType) != 1 or not "data" in thisType:
          newHistList[iHist][iType].SetMarkerColor(totalBkgColors[iType])
          newHistList[iHist][iType].SetLineColor(totalBkgColors[iType])
          newHistList[iHist][iType].SetFillColorAlpha(totalBkgColors[iType],0)
#          newHistList[iHist][iType].SetFillStyle(3004)
          newHistList[iHist][iType].SetFillStyle(1001)
        histsToPlot.append( newHistList[iHist][iType] )

    if len(args.deriveRW) > 0:
      rwHist = deriveReweight( histsToPlot, HistTypes, args.outputTag, args.outputVersion, args.deriveRW )
      iBkg = HistTypes.index("bkg")
      for ibin in range(1, rwHist.GetNbinsX()+1):
        histsToPlot[iBkg].SetBinContent( ibin, histsToPlot[iBkg].GetBinContent(ibin) * rwHist.GetBinContent(ibin) )



    # Don't plot if some samples are missing the histogram and plotPartial is not requested
    if len(histsToPlot) == len(newHistList[iHist]) or args.plotPartial:
      plotHists( Names, histsToPlot, histName[0], HistTypes, args.outputTag, args.outputVersion )


#----------------------------------------
#Combine all samples in histFiles
#plot individual JZ slices if plotSlices is requsted

def mergeFiles( histFiles, histNames , sampleName, plotSlices, lumi,mergeFileTag ):
  histsTotal = []

  if args.do_massPartonPlots == True:
    hists_partons = defaultdict(list)
    plotNames_partons = defaultdict(list)


#  if args.include_JES_bands == True:
#    hists_JES = defaultdict(list)
#    plotNames_JES = defaultdict(list)

  outputName = "Slices_"+sampleName
  for hName in histNames:
#    if not "first_jet_pt" in hName: continue
    if "cutflow" in hName: continue
    hists = []
    plotNames = []
    for hFile in histFiles:
      if "merged" in hFile.GetName(): continue
      if args.v: print sampleName, hName
      sampleNameInitial = os.path.basename(hFile.GetName()).split('.')
#      sampleName = '.'.join(sampleName[1:-1]) #Remove first and last fields (studyName and .root)
      sampleName = '_'.join(sampleNameInitial[1:-1]) #Remove first and last fields (studyName and .root)
      #hist = hFile.Get("Scaled_" + hName)
      if args.v: print "getting histogram named Scaled_" + hName + "_" + sampleName
      hist = hFile.Get("Scaled_" + hName + "_" + sampleName)
      if lumi > 0: hist.Scale( lumi )

      if args.v: print hist


      if len(sampleNameInitial)==6:  #---MERGE CHANGE
        sampleName = '_'.join(sampleNameInitial[1:-2]) #Remove last fields (remove jSlice sub file index)  #---MERGE CHANGE
      nbinX = hist.GetNbinsX()
      # bring in overflow
      if hist.GetBinContent( nbinX + 1 ) > 0:
        hist.SetBinContent( nbinX, hist.GetBinContent( nbinX ) + hist.GetBinContent( nbinX + 1 ) )
        newError = sqrt( hist.GetBinError( nbinX )*hist.GetBinError( nbinX ) + hist.GetBinError( nbinX + 1 )*hist.GetBinError( nbinX + 1) )
        hist.SetBinError( nbinX, newError )

      ## if first file ##
      if len(hists) == 0:
        total =  hist.Clone( hist.GetTitle() + '_'+sampleName+"_total" )
        total.SetDirectory(0)
        if type(hist) == ROOT.TH1D:
          total.SetMarkerColor(ROOT.kBlack)
        hists.append( total )
        plotNames.append( "total" )

      ## else add to previous entry ##
      else:
        total.Add( hist )

      ## configure individual JZX or JZXW slices if requested ##
      if plotSlices == True:
#       if type(hist) == ROOT.TH1D:
        hist.SetMarkerColor( plotUtils.getDijetColor( sampleName ) )
        hist.SetLineColor( plotUtils.getDijetColor( sampleName ) )

        index_sliceName = sampleName.find('JZ')
        if sampleName.find('.',index_sliceName) != -1:
          index_end = sampleName.find('.',index_sliceName)
        else:
          index_end = len(sampleName)
        if sampleName[index_sliceName:index_end] in plotNames:    #--MERGE CHANGE
          for hist_num in range(0,len(hists)):                  #--MERGE CHANGE
            if hist.GetName == hists[hist_num].GetName():       #--MERGE CHANGE
              hists[hist_num].Add(hist)                             #--MERGE CHANGE
        else:                                                          #--MERGE CHANGE
          hists.append( hist )                                            #--MERGE CHANGE
          plotNames.append( sampleName[index_sliceName:index_end] )    #--MERGE CHANGE
#        print hist.GetName()                                           #---MERGE CHANGE  commented
#        plotNames.append( sampleName[index_sliceName:index_end] )      #---MERGE CHANGE  commented





    ##Need to add clone now else get's rebinned ##
    histsTotal.append(copy.copy(total))
    histsTotal[-1].SetName( total.GetName()+"_final")
    #histsTotal.append(total.Clone(total.GetName()+"_final"))

    ## Plot individual JZX or JZXW slices if requested ##
    if plotSlices == True:
#      HistTypes = ["bkg"]*len(histsToPlot)
      HistTypes = ["bkg"]*len(hists)
      if args.v: print plotNames
      if args.v: print hName
      plotHists( plotNames, hists, hName, HistTypes, outputName, args.outputVersion )



#    print hist.GetTitle()
    if args.do_massPartonPlots == True:
      if "CutFlow" in hName: continue
      if not "incoming" in hName and not "outgoing" in hName:
        total.SetMarkerColor( plotUtils.getMassPartonColor( hName ) )
        total.SetLineColor( plotUtils.getMassPartonColor( hName  ) )
      else:
        total.SetMarkerColor( plotUtils.getMassPartonColorOneSide( hName ) )
        total.SetLineColor( plotUtils.getMassPartonColorOneSide( hName  ) )

      typeName = total.GetTitle().split('_of_')[1]
      varName = total.GetTitle().split('_of_')[0]

      if not varName in plotNames_partons.keys():
        hists_partons[varName].append(total.Clone( total.GetTitle() + "_total_partons" ))
        hists_partons[varName][0].SetMarkerColor(ROOT.kBlack)
#        print total.GetTitle() + "_total_partons"
        plotNames_partons[varName].append("total")
      else:
        hists_partons[varName][0].Add(total)
      hists_partons[varName].append(total)
      plotNames_partons[varName].append(typeName)


  if args.do_massPartonPlots == True:
    for varName in hists_partons:
      print plotNames_partons[varName]
      HistTypes = ["bkg"]*len(hists_partons[varName])
      plotNames = plotNames_partons[varName]
      hists = hists_partons[varName]
      outputName = "Partons"
      hName = varName
      plotHists( plotNames, hists, hName, HistTypes, outputName, args.outputVersion )

  if args.writeMerged:
    f = ROOT.TFile(args.histDirData+"/"+mergeFileTag+"_mergedFiles.root","recreate")
    for hist in histsTotal:
      hist.Write()
    f.Close()


   #ADD JES BANDS HERE!!!

  return histsTotal


#---------------------------------------------------------
#get files containing the input tags
def getRelevantHistFiles( histDir, histFileTags ):

  histFiles = []
  histNames = []

  histFileNames = plotUtils.getFileList( histDir, histFileTags )

  if len(histFileNames)<1: print "ERROR:  There are no histogram files of requested type", histFileTags
  elif args.v: print histFileNames

  for fName in histFileNames:
    print("Including : " + fName)
    histFiles.append( ROOT.TFile(fName, 'READ') )

  ## Get names of all included histograms ##
  keys = histFiles[0].GetListOfKeys()
  for key in keys:
#    print key
    if "cutflow" in key.GetTitle(): continue
    histNames.append(key.GetTitle())

  if len(histFileNames)<1: print "ERROR:  No histogram matching the given name."

  return histFiles, histNames


#--------------------------------------------------------
#--------------------------------------------------------
## Plot the histograms given ##
def plotHists( h_names, h_hists, hName, h_histTypes, outputTag, outputVersion ):

  ## copy these as they can be changed ##
  names = copy.copy(h_names)
  hists = copy.copy(h_hists)
  histTypes = copy.copy(h_histTypes)

  if(args.v):
    print("Plot " + hName)
    for h in hists:
      print( "\t" + str(h.Integral()) )

  if len(hists)<0:
    print "ERROR, no hists passed... not plotting"
    return

  if not os.path.exists(args.plotDir):
    os.mkdir(args.plotDir)

  plotRatio = args.plotRatio
  # Only run plotRatio if there is 1 data file
#  if not "data" in histTypes:
#    plotRatio = False
  # Only run for TH1F and TH1D
  #if not ( type(hists[0]) == ROOT.TH1D or type(hists[0]) == ROOT.TH1F ):
  #  plotRatio = False

  c0 = ROOT.TCanvas(hName)
  if plotRatio:
    pad1 = ROOT.TPad("pad1","pad1",0,0.3,1,1)
    pad2 = ROOT.TPad("pad2","pad2",0,0.01,1,0.3)
    pad1.Draw()
    pad2.Draw()
    pad1.cd()
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



  logx=False

  ## calculate bkg vs data lumi difference ##
  dataInteg = 0.
  bkgInteg = 0.
  for iHist, hist in enumerate(hists):
    if histTypes[iHist] == "data":
      dataInteg += hist.Integral()
    elif histTypes[iHist] == 'bkg':
      bkgInteg += hist.Integral()
  if bkgInteg > 0:
    lumiRatio = dataInteg/bkgInteg
  else:
    lumiRatio = -1.

  # differential - then scale to same integral as data or not...
  if args.differential:  #MAKE THIS INCLUDE AN "OR CONTAINS CHI" CLAUSE   **********
    for iHist, hist in enumerate(hists):
      if hist.Integral() > 0:
        hist.Scale(1.0/hist.Integral(),"width")

  elif args.unitNormalize:
    print "NORMALIZE"
    for iHist, hist in enumerate(hists):
      if hist.Integral() > 0:
        hist.Scale(1.0/hist.Integral())


  elif args.normToMC:
    iBkg = histTypes.index("bkg")
    scaleFactor = 1.
    for iHist, hist in enumerate(hists):
      if histTypes[iHist] == 'data':
        if hist.Integral() > 0:
          scaleFactor = hists[iBkg].Integral() / hist.Integral()
          hist.Scale(scaleFactor)
    for iHist, hist in enumerate(hists):
      if histTypes[iHist] == 'signal':
        hist.Scale(scaleFactor)


  elif args.normToData:

    ## If not exactly one data sample ##
    if not len( [x for x in histTypes if x == "data"]) == 1:
      print "Don't normalize this as there is no data file.  Likely a slices plotting or not exactly 1 data file."
      #args.noNormalize = True

    else:

      iData = histTypes.index("data")
      scaleFactor = 1.
      for iHist, hist in enumerate(hists):
        if histTypes[iHist] == 'bkg':
          if hist.Integral() > 0:
            scaleFactor = hists[iData].Integral() / hist.Integral()
            hist.Scale(scaleFactor)
      for iHist, hist in enumerate(hists):
        if histTypes[iHist] == 'signal':
          hist.Scale(scaleFactor)
      for iHist, hist in enumerate(hists):
        if histTypes[iHist] == 'bkgJES':
          hist.Scale(scaleFactor)

  ## THStack does not work! So just add background to signals, and make sure signal drawn first ##
  ##Stack Signal on MC if requested
  if not args.noStackSignal and len(args.bkgType) > 0 and len(args.bkgJESType) > 0 :   #( len(args.signalType) > 0 or ):

    ## Find signal files ##
    signalIndicies = []
    for iHistType, histType in enumerate(histTypes):
      if histType == "signal":
        signalIndicies.append(iHistType)

    ## Find JES files ##
    countHere = 0
    jesIndicies = []
    for iHistType, histType in enumerate(histTypes):
      if histType == "bkgJES":
        countHere += 1
        jesIndicies.append(iHistType)

    print countHere

    newHists = []
    newNames = []
    newHistTypes = []
    ## Edit background into signal + bkg
    for iHistType, histType in enumerate(histTypes):
      ## just add back nominal if data and don't add if signal ##
      if histType == "data":
        newHists.append( hists[iHistType] )
        newNames.append( names[iHistType] )
        newHistTypes.append( histTypes[iHistType] )
      elif histType == 'bkg':
        if type(hists[iHistType]) == ROOT.TH1D or type(hists[iHistType]) == ROOT.TH1F:

          if len(args.bkgJESType) > 0:
            ii = 0;
            for i, iJES in enumerate(jesIndicies):
              if ii == 0:
                ii+=1
                jesUp = hists[iHistType].Clone(hists[iHistType].GetName()+"_jesUp")
                jesUp.SetDirectory(0)
                jesDown = hists[iHistType].Clone(hists[iHistType].GetName()+"_jesDown")
                jesDown.SetDirectory(0)
                nBins = hists[iHistType].GetNbinsX()
                for j in range(1,nBins+1):
                  jesUp.SetBinContent( j , 0 )
                  jesDown.SetBinContent( j , 0 )
              for j in range(1,nBins+1):
                variation = hists[iJES].GetBinContent(j) - hists[iHistType].GetBinContent(j)
                if variation >= 0:
                  jesUp.SetBinContent( j , jesUp.GetBinContent(j) + variation*variation )
                if variation < 0:
                  jesDown.SetBinContent( j , jesDown.GetBinContent(j) + variation*variation )

            for j in range(1,nBins+1):
              jesUp.SetBinContent( j , sqrt(jesUp.GetBinContent(j)) )
              jesDown.SetBinContent( j , sqrt(jesDown.GetBinContent(j)) )

            jesUptemp = hists[iHistType].Clone(hists[iHistType].GetName()+"_UP")
            jesUp.Scale(1)
            jesUptemp.Add(jesUp,1)
            jesDowntemp = hists[iHistType].Clone(hists[iHistType].GetName()+"_DOWN")
            jesDowntemp.Add(jesDown,-1)

            jesUptemp.SetMarkerColorAlpha( ROOT.kBlue,0.15)
            jesUptemp.SetLineColorAlpha( ROOT.kBlue,0.15)
            jesUptemp.SetFillColorAlpha( ROOT.kBlue, 0.15)
            jesUptemp.SetFillStyle(1001)
            jesDowntemp.SetFillStyle(1001)
            jesDowntemp.SetMarkerColorAlpha( ROOT.kBlue,0.15)
            jesDowntemp.SetLineColorAlpha( ROOT.kBlue,0.15)
            jesDowntemp.SetFillColorAlpha(ROOT.kWhite,1)


          if len(args.signalType) > 0:
            for i, iSignal in enumerate(signalIndicies):
              newBkgHist = hists[iHistType].Clone(hists[iHistType].GetName()+"_signal")
              newBkgHist.Add( hists[iSignal] )
              newBkgHist.SetMarkerColor( hists[iSignal].GetMarkerColor())
              newBkgHist.SetLineColor( hists[iSignal].GetLineColor())
              newBkgHist.SetFillColor( hists[iSignal].GetFillColor())
              for j in range(i+1, len(signalIndicies)):
                newBkgHist.Add( hists[ signalIndicies[ j ] ] )
              newHists.append( newBkgHist)
              #newNames.append( names[iHistType]+'_'+names[iSignal])
              newNames.append( names[iHistType]+'_'+names[iSignal])
              newHistTypes.append( "bkg")
#


          ## make sure original background comes afterwards ##
          newHists.append( hists[iHistType] )
          newNames.append( names[iHistType] )
          newHistTypes.append( histTypes[iHistType] )

          newHists.append( jesUptemp )
          newNames.append( names[iHistType]+"_jesUp" )
          newHistTypes.append( "bkgJESup" )

          newHists.append( jesDowntemp )
          newNames.append( names[iHistType]+"_jesDown" )
          newHistTypes.append( "bkgJESdown" )

        ## if 2D plots, just remove the regular backgrounds ##
        else:
          for i, iSignal in enumerate(signalIndicies):
            hists[iHistType].Add( hists[iSignal] )

          newHists.append( hists[iHistType] )
          newNames.append( names[iHistType] )
          newHistTypes.append( histTypes[iHistType] )


    hists = newHists
    names = newNames
    histTypes = newHistTypes

  #------------------------------------------
#  leg = ROOT.TLegend(0.70,0.67, 0.88, 0.94,"")
#  leg = ROOT.TLegend(0.75,0.75, 0.9, 0.94,"")

  leg = ROOT.TLegend(0.70,0.7, 0.86, 0.92,"")
  leg.SetTextFont(62)
#  leg.SetTextSize(0.1)
  leg.SetFillStyle(0)
  leg.SetEntrySeparation(0.0001)
  if args.v: print("N hists : " + str(len(hists)) )

  ## Handle 1D plots all on the same TCanvas ##
  if type(hists[0]) == ROOT.TH1D or type(hists[0]) == ROOT.TH1F:
    #extraText=[]
    #logXList = [ "mjj", "m3j", "chi", "m12", "m13", "m23" ]   # madd all two-jet mass plots have logX
    logXList = [ "chi" ]   # madd all two-jet mass plots have logX

    for v in logXList:
      if v == hName: logx = True
#      elif v in hName and "for_mjj" in hName : logx = True
      elif v in hName and not "__" in hName: logx = True

    ## check if the range needs to be changed for this variable
    ## rangeStrings are like "jet_E,35,150"
    xmax = xmin = 0
# exact match if jet in name

    if any( rangeString.split(',')[0] in hName and not "jet_" in rangeString.split(',')[0] for rangeString in range1D ):
      rangeString = [rangeString for rangeString in range1D if rangeString.split(',')[0] in hName][0]
      xmin = float(rangeString.split(',')[1])
      xmax = float(rangeString.split(',')[2])
# not exact match if jet not in name
    if any( rangeString.split(',')[0] == hName and "jet_" in rangeString.split(',')[0] for rangeString in range1D ):
      rangeString = [rangeString for rangeString in range1D if rangeString.split(',')[0] in hName][0]
      xmin = float(rangeString.split(',')[1])
      xmax = float(rangeString.split(',')[2])


    ## Rebin before getting y maximum ##
    rebin = 0
    if any( rebinString.split(',')[0] in hName for rebinString in rebin1D ):
      if args.v: print("REBIN " + hName)
      rebinString = [rebinString for rebinString in rebin1D if rebinString.split(',')[0] in hName][0]
      rebin = int(rebinString.split(',')[1])
      for i in range(0,len(hists)):
        hists[i].Rebin(rebin)
    elif args.allRebin:
      for i in range(0,len(hists)):
        hists[i].Rebin( args.allRebinFactor )

    for i in range(0,len(hists)):
      scaleBinWidthHere = False
      if args.scaleBinWidth:
        for v in ["first_jet_pt","second_jet_pt","mjj"]:
          if v in hName:
            hists[i].Scale(1,"width")
            scaleBinWidthHere = True



    ## Get Y-axis maximum after rebinning ##
    ymax = 0
    ymin = 0
    #yMinNotZero = 1e8
    yMinNotZero = 0.00011
## if no data, use a default
    if 'data' in histTypes:
      yMinNotZero = 0.00011

    for i, hist in enumerate(hists):
      if hist.GetMaximum() > ymax: ymax = hist.GetMaximum()
      if hist.GetMaximum() < ymin: ymin = hist.GetMinimum()
      if histTypes[i] == "data":
        for ibin in range(1, hist.GetNbinsX()+1):
          content = hist.GetBinContent(ibin)
          if content > 0:
            if content < yMinNotZero: yMinNotZero = content
    ymax *= 1.3
    if "eta" in hName or "Eta" in hName:
      ymax *= 1.1

    ## Draw all input histograms ##
    drawString, legendString = [], []
    for i in range(0,len(hists)):
      ## Configure ##
#      hists[i].SetMaximum( ymax )
      hists[i].GetYaxis().SetRangeUser( ymin, ymax )
      if xmax != 0 or xmin != 0:
        hists[i].GetXaxis().SetRangeUser( xmin, xmax )

      hists[i].GetYaxis().SetTitle("Events")
      if scaleBinWidthHere:  hists[i].GetYaxis().SetTitle("Events / GeV")
      if "deltaPhi" in hName:
        hists[i].GetXaxis().SetTitle("#Delta#phi(jet_{1},jet_{2})")
      if "lumiBlock" in hName:
        hists[i].GetXaxis().SetTitle("Lumi Block")
      if "jet_" in hName:
        hists[i].GetXaxis().SetTitle(hists[i].GetXaxis().GetTitle().replace("jet_",""))
        if not "__" in hName: # 1D
          if scaleBinWidthHere:  hists[i].GetYaxis().SetTitle("Jets / GeV")
          else: hists[i].GetYaxis().SetTitle("Jets")
      if "Number" in hName:
        hists[i].GetXaxis().SetTitle(hists[i].GetXaxis().GetTitle().replace("Number", " Number"))
      if "mc" in hName:
        hists[i].GetXaxis().SetTitle(hists[i].GetXaxis().GetTitle().replace("mc", "MC "))
      if "EventWeight" in hName:
        hists[i].GetXaxis().SetTitle(hists[i].GetXaxis().GetTitle().replace("Event", "Event "))
      if args.unitNormalize and not "__" in hName:
        hists[i].GetYaxis().SetTitle("Arbitrary Units")
      if args.differential and not "__" in hName:
        xaxisName = hists[i].GetXaxis().GetTitle()
        hists[i].GetYaxis().SetTitle("(1/N)dN/d"+xaxisName)

      # eta ranges
      xaxisTitle = hists[i].GetTitle()
      cutoff = xaxisTitle.find("eta")
      exText = ""
      if "eta_0_0p8" in xaxisTitle: exText = xaxisTitle[cutoff:].replace("eta_0_0p8","0<|#eta|#leq0.8")
      if "eta_0p8_1p2" in xaxisTitle: exText = xaxisTitle[cutoff:].replace("eta_0p8_1p2","0.8<|#eta|#leq1.2")
      if "eta_1p2_1p8" in xaxisTitle: exText = xaxisTitle[cutoff:].replace("eta_1p2_1p8","1.2<|#eta|#leq1.8")
      if "eta_1p8_2p1" in xaxisTitle: exText = xaxisTitle[cutoff:].replace("eta_1p8_2p1","1.8<|#eta|#leq2.1")
      if "eta_2p1_2p8" in xaxisTitle: exText = xaxisTitle[cutoff:].replace("eta_2p1_2p8","2.1<|#eta|#leq2.8")
      if "eta_2p8_3p1" in xaxisTitle: exText = xaxisTitle[cutoff:].replace("eta_2p8_3p1","2.8<|#eta|#leq3.1")
      if "eta_3p1_4p9" in xaxisTitle: exText = xaxisTitle[cutoff:].replace("eta_3p1_4p9","3.1<|#eta|#leq4.9")
      if exText: extraText.append(hists[i].GetTitle()+","+exText)

   #if "NPV" in hName:
      #  hists[i].GetYaxis().SetTitle("Events")
      #else:
      #  hists[i].GetYaxis().SetTitle("Jets")

      drawString.append('')
      legendString.append('')
      if i != 0:
        drawString[-1] += 'same'
      drawString[-1] += 'histe'
      if len(args.dataType) > 0 and not "data" == histTypes[i]:
        # not data so can make sure markers are not seen - see error bars
        hists[i].SetMarkerSize( 0.0 )
        if not "bkg" == histTypes[i]:
          drawString[-1] += 'fe'
          legendString[-1] += 'f'
#        drawString[-1] += 'e'
        else: #why is this here?
          drawString[-1] += 'fe'
          legendString[-1] += 'f'
            #        drawString[-1] += 'e'
      else:
        drawString[-1] += 'ep'
        legendString[-1] += 'p'

    ## Get ratio ##
    if (plotRatio):
      print "a!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
      ratioHists = []
      # Get first data point
      iDataHist = histTypes.index(args.ratioWRT)
      iJESHistup    = -1
      iJESHistdown  = -1
      if len(args.bkgJESType) > 0:
        iJESHistup = histTypes.index('bkgJESup')
        iJESHistdown = histTypes.index('bkgJESdown')

      for i in range(0,len(hists)):
        if i == iDataHist: continue
        if iJESHistup != -1 and i == iJESHistup:    continue
        if iJESHistup != -1 and i == iJESHistdown:  continue
        tmpRatioHist = hists[iDataHist].Clone( hists[iDataHist].GetName()+"_ratio" )
        tmpMCHist = hists[i].Clone( "tmp" )
        tmpRatioHist.SetMarkerColor( tmpMCHist.GetMarkerColor() )
        tmpRatioHist.SetLineColor( tmpMCHist.GetLineColor() )


        print "b!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
        if iJESHistup >= 0:
          tmpJESRatioHistup = hists[iJESHistup].Clone( hists[iJESHistup].GetName()+"_ratioJESup" )
          tmpJESRatioHistup.Add( tmpMCHist, -1. )
          tmpJESRatioHistup.Divide( tmpMCHist )
#          for i in range(0, hists[iDataHist].GetNbinsX()+1):
#            if hists[iDataHist].GetBinContent(i) == 0:
#              tmpJESRatioHistdown.SetBinContent(i,0)
#              tmpJESRatioHistdown.SetBinError(i,0)
#              continue
#            tmpJESRatioHistdown.SetBinContent( i, tmpJESRatioHistdown.GetBinContent(i) / hists[iDataHist].GetBinError(i) )
#            tmpJESRatioHistdown.SetBinError(i, 0)
          tmpJESRatioHistup.SetMarkerColorAlpha( ROOT.kBlue,0.15)
          tmpJESRatioHistup.SetLineColorAlpha( ROOT.kBlue,0.15)
          tmpJESRatioHistup.SetFillColorAlpha( ROOT.kBlue, 0.15)
          tmpJESRatioHistup.SetFillStyle(1001)
          if args.ratioWRT == 'bkg':
            tmpJESRatioHistup.Scale( -1.0 )

        if iJESHistdown >= 0:
          tmpJESRatioHistdown = hists[iJESHistdown].Clone( hists[iJESHistdown].GetName()+"_ratioJESdown" )
          tmpJESRatioHistdown.Add( tmpMCHist, -1. )
          tmpJESRatioHistdown.Divide( tmpMCHist )
#          for i in range(0, hists[iDataHist].GetNbinsX()+1):
#            if hists[iDataHist].GetBinContent(i) == 0:
#              tmpJESRatioHistdown.SetBinContent(i,0)
#              tmpJESRatioHistdown.SetBinError(i,0)
#              continue
#            tmpJESRatioHistdown.SetBinContent( i, tmpJESRatioHistdown.GetBinContent(i) / hists[iDataHist].GetBinError(i) )
#            tmpJESRatioHistdown.SetBinError(i, 0)
          tmpJESRatioHistdown.SetMarkerColorAlpha( ROOT.kBlue,0.15)
          tmpJESRatioHistdown.SetLineColorAlpha( ROOT.kBlue,0.15)
          tmpJESRatioHistdown.SetFillColorAlpha( ROOT.kBlue, 0.15)
          tmpJESRatioHistdown.SetFillStyle(1001)
          if args.ratioWRT == 'bkg':
            tmpJESRatioHistdown.Scale( -1.0 )

        print "c!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
        tmpRatioHist.Add( tmpMCHist, -1. )
        tmpRatioHist.Divide( tmpMCHist )
#        for i in range(0, hists[iDataHist].GetNbinsX()+1):
#          if hists[iDataHist].GetBinContent(i) == 0:
#            tmpRatioHist.SetBinContent(i,0)
#            tmpRatioHist.SetBinError(i,0)
#            continue
#          tmpRatioHist.SetBinContent( i, tmpRatioHist.GetBinContent(i) / hists[iDataHist].GetBinError(i) )
#          tmpRatioHist.SetBinError(i, 0)

# flip it so excess is still positive on ratio
        if args.ratioWRT == 'bkg':
          tmpRatioHist.Scale( -1.0 )

        ## If data is 0 then there should be no ratio drawn
        for iBin in range(1, tmpRatioHist.GetNbinsX()+1):
          if hists[iDataHist].GetBinContent(iBin) == 0:
            tmpRatioHist.SetBinContent(iBin, 0)
            tmpRatioHist.SetBinError(iBin, 0)


        print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
        tmpRatioHist.GetYaxis().SetTitleSize( 0.17 )
        tmpRatioHist.GetYaxis().SetLabelSize( 0.17 )
        tmpRatioHist.GetYaxis().SetTitleOffset( 0.4 )
        tmpRatioHist.GetXaxis().SetLabelSize( 0.2 )
        tmpRatioHist.GetXaxis().SetTitleSize( 0.2 )
        tmpRatioHist.GetXaxis().SetTitleOffset( 1 )
        tmpRatioHist.GetYaxis().SetNdivisions(5)
        tmpRatioHist.GetYaxis().SetTitle("#splitline{Relative}{Difference}")
        #tmpRatioHist.GetYaxis().SetTitle("Significance")
        ratioHists.append( tmpRatioHist )

        if iJESHistup >= 0:
          ratioHists.append( tmpJESRatioHistup )
        if iJESHistdown >= 0:
          ratioHists.append( tmpJESRatioHistdown )

      ############################### Being Ratio y-axis ###############################
      ## Fix ratio Y-axis ##
      yMaxRatio = args.ratioRangeMax
      yMinRatio = args.ratioRangeMin
      # exact match if jet in name
      if any( ratioRangeString.split(',')[0] in hName and not "jet_" in ratioRangeString.split(',')[0] for ratioRangeString in ratioRange ):
        ratioRangeString = [ratioRangeString for ratioRangeString in ratioRange if ratioRangeString.split(',')[0] in hName][0]
        yMinRatio = float(ratioRangeString.split(',')[1])
        yMaxRatio = float(ratioRangeString.split(',')[2])
      # not exact match if jet not in name
      if any( ratioRangeString.split(',')[0] == hName and "jet_" in ratioRangeString.split(',')[0] for ratioRangeString in ratioRange ):
        ratioRangeString = [ratioRangeString for ratioRangeString in ratioRange if ratioRangeString.split(',')[0] in hName][0]
        yMinRatio = float(ratioRangeString.split(',')[1])
        yMaxRatio = float(ratioRangeString.split(',')[2])

      ## If yMaxRatio and yMinRatio are 0, then use range determined by ROOT ##
      if yMaxRatio !=0 and yMinRatio != 0:
        for i in range(0, len(ratioHists)):
          ratioHists[i].SetMaximum(yMaxRatio)
          ratioHists[i].SetMinimum(yMinRatio)

    #%%%%%%%%%%%%%%%%%%%% End ratio hists ymax code %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

    if logx: hists[i].GetYaxis().SetMoreLogLabels(1)

    if logx:
      c0.SetLogx()
      if (plotRatio):
        pad1.SetLogx()
        pad2.SetLogx()
    else:
      c0.SetLogx(0)
      if (plotRatio):
        pad1.SetLogx(0)
        pad2.SetLogx(0)

    if plotRatio:
      for i in range(0, len(hists)):
        if hists[i].GetMinimum() < 0.0001:
          hists[i].SetMinimum(0.0001)

    ## Draw non logY ##
#super ugly differential chi patch
    for i in range(0,len(hists)):
      if hists[i].GetMaximum() < 0.00000001:
        if args.differential :
          hists[i].SetMaximum(0.1)
#        else :
#          hists[i].SetMaximum(1.)
#        hists[i].GetYaxis().SetRangeUser(0.0001, 1.)
      if ymax/10. > 1 and ymax/10. < 10: hists[i].GetYaxis().SetTitleOffset(0.7)
      elif ymax/100. > 1 and ymax/100. < 10: hists[i].GetYaxis().SetTitleOffset(0.8)
      elif ymax/1000. > 1 and ymax/1000. < 10: hists[i].GetYaxis().SetTitleOffset(0.9)
      else:
        hists[i].GetYaxis().SetTitleOffset(1.)
#      hists[i].GetYaxis().SetLabelSize(0.08)
#      hists[i].GetXaxis().SetLabelSize(0.06)
#      hists[i].GetYaxis().SetTitleSize(0.08)
#      hists[i].GetXaxis().SetTitleSize(0.06)
      hists[i].Draw( drawString[i] )
      entryName = list(names[i].split('+'))[0]
      if entryName == "26763": entryName = "Period A4"
      if entryName == "270"  : entryName = "Period C2"
      if entryName == "27"   : entryName = "Period C2+partial 3"
      if "_jesUp" in entryName:  entryName = "Pythia +/- JES"
      #if "somthing" in entryName: entryName = something else
      if "jesDown" not in entryName: leg.AddEntry( hists[i], entryName, legendString[i])

    leg.Draw("same")
    '''
    AtlasStyle.ATLAS_LABEL(0.20,0.88, 0.07)
    sqrtSLumiText = getSqrtSLumiText( args.lumi )
    AtlasStyle.myText(0.20,0.82,sqrtSLumiText,0.07)
    if len(args.plotText)>0:
      AtlasStyle.myText(0.20,0.75,args.plotText, 0.07)


    if any( extraTextString.split(',')[0] in hName for extraTextString in extraText ):
      extraTextString = [extraTextString for extraTextString in extraText if extraTextString.split(',')[0] in hName][0]
      if len(args.plotText)>0:
        AtlasStyle.myText(0.20,0.64, extraTextString.split(',')[1],0.07)
      else:
        AtlasStyle.myText(0.20,0.75, extraTextString.split(',')[1],0.07)

    if any( extraTextString.split(',')[0] in hName for extraTextString in extraText ):
      extraTextString = [extraTextString for extraTextString in extraText if extraTextString.split(',')[0] in hName][0]
      if len(args.plotText)>0:
        AtlasStyle.myText(0.20,0.64, extraTextString.split(',')[1],0.07)
      else:
        AtlasStyle.myText(0.20,0.75, extraTextString.split(',')[1],0.07)
    '''
    AtlasStyle.ATLAS_LABEL(0.20,0.88)
    sqrtSLumiText = getSqrtSLumiText( args.lumi )
    AtlasStyle.myText(0.20,0.82,1, sqrtSLumiText)
    if len(args.plotText)>0:
      AtlasStyle.myText(0.20,0.76,1, args.plotText)
#    AtlasStyle.myText(0.20,0.71,1, "Lumi:"'%s' % float('%.2g' % lumiRatio) )


    if any( extraTextString.split(',')[0] in hName for extraTextString in extraText ):
      extraTextString = [extraTextString for extraTextString in extraText if extraTextString.split(',')[0] in hName][0]
      if len(args.plotText)>0:
        AtlasStyle.myText(0.20,0.64, 1,extraTextString.split(',')[1])
      else:
        AtlasStyle.myText(0.20,0.75, 1,extraTextString.split(',')[1])

    if (plotRatio):
      pad2.cd()
#      for i in range(0,len(ratioHists)):
#        ratioHists[i].Draw( "p" )
      if len(ratioHists) == 1:
        ratioHists[0].SetLineColor(ROOT.kBlack)
        ratioHists[0].SetMarkerColor(ROOT.kBlack)
      for i in range(0,len(ratioHists)):
        ratioHists[i].SetStats(0)
        if i == 0: ratioHists[i].DrawCopy("p") #e0
        if i == 0: ratioHists[i].SetMarkerSize(0) #e0
        if i == 0: ratioHists[i].DrawCopy("same e0") #e0
        else: ratioHists[i].Draw( "fhistsame" )
        ratioHists[i].GetYaxis().SetRangeUser(-0.5, 0.5)
      pad2.Update()
      zeroLine.Draw("same")

    c0.Print( args.plotDir + "/" + outputTag + "_" + hName + outputVersion + ".png","png") #,"png")
#    c0.Print( args.plotDir + "/" + outputTag + "_" + hName + outputVersion + ".pdf","pdf") #,"pdf")
#!!    c0.Clear()

    if plotRatio:
      pad1.cd()

    if not args.differential or args.differential: # why not do log fo differential?

    ## Draw logY ##
      c0.SetLogy()
      if (plotRatio):
        pad1.SetLogy()

      for i in range(0,len(hists)):
#        hists[i].SetMaximum( ymax*50. )
        hists[i].SetMinimum( 0.1001 )
        if ymax > 0:
          hists[i].GetYaxis().SetRangeUser( yMinNotZero,  exp(log(ymax)*1.8))
        else:
          hists[i].GetYaxis().SetRangeUser( yMinNotZero,  ymax*50)
        if hists[i].GetMaximum() > 0 and log(hists[i].GetMaximum())/10. > 1.: hists[i].GetYaxis().SetTitleOffset(0.8)
        else: hists[i].GetYaxis().SetTitleOffset(0.7)
#        if ymax > 0:
#          hists[i].SetMaximum( exp(log(ymax)*1.8) )
        hists[i].Draw( drawString[i] )


      leg.Draw("same")
      AtlasStyle.ATLAS_LABEL(0.20,0.88)
      sqrtSLumiText = getSqrtSLumiText( args.lumi )
      AtlasStyle.myText(0.20,0.82,1, sqrtSLumiText)
      if len(args.plotText)>0:
        AtlasStyle.myText(0.20,0.76,1, args.plotText)
#     AtlasStyle.myText(0.20,0.71,1, "Lumi:"'%s' % float('%.2g' % lumiRatio) )

      if any( extraTextString.split(',')[0] in hName for extraTextString in extraText ):
        extraTextString = [extraTextString for extraTextString in extraText if extraTextString.split(',')[0] in hName][0]
        if len(args.plotText)>0:
          AtlasStyle.myText(0.20,0.64, 1,extraTextString.split(',')[1])
        else:
          AtlasStyle.myText(0.20,0.75, 1,extraTextString.split(',')[1])
      c0.Print( args.plotDir + "/" + outputTag + "_" + hName + "_logY" + outputVersion + ".png","png") #,"png")
#      c0.Print( args.plotDir + "/" + outputTag + "_" + hName + "_logY" + outputVersion + ".pdf","pdf") #,"pdf")
      c0.SetLogy(0)
      if (plotRatio):
        pad1.SetLogy(0)


  ## Draw seperate 2D plots for each input ##
  elif type(hists[0]) == ROOT.TH2D or type(hists[0]) == ROOT.TProfile2D:
    ## check if the range needs to be changed for this variable
    ## rangeStrings are like "jet_E,35,150"

    print "printing 2D plot or Profile2D", hName
    xmax = xmin = 0
    if any( rangeString.split(',')[0] in hName for rangeString in range2D ):
      rangeString = [rangeString for rangeString in range2D if rangeString.split(',')[0] in hName][0]
      xmin = float(rangeString.split(',')[1])
      xmax = float(rangeString.split(',')[2])
      #print xmin, xmax

    rebin = 0
    if any( rebinString.split(',')[0] in hName for rebinString in rebin2D ):
      if args.v: print("REBIN 2D" + hName)
      rebinString = [rebinString for rebinString in rebin2D if rebinString.split(',')[0] in hName][0]
      rebin = int(rebinString.split(',')[1])
      for i in range(0,len(hists)):
        hists[i].Rebin2D(rebin,rebin)

    ## Draw the profile of all of them together
    print("Make profiles")
    profs = []
    ymax = 0
    ymin = hists[0].GetMinimum() - hists[0].GetBinError(hists[0].GetMinimumBin())/2.
    for iHist, thisHist in enumerate(hists):
      prof = thisHist.ProfileX( thisHist.GetName() + "_ProfileX_" + str(iHist) )
      prof.SetMarkerColor( thisHist.GetMarkerColor() )
      prof.SetLineColor(   thisHist.GetMarkerColor() )
      if "#splitline" in thisHist.GetYaxis().GetTitle():
        prof.GetYaxis().SetTitle(thisHist.GetYaxis().GetTitle().replace("splitline{", "splitline{<").replace("}{", ">}{"))
      else:
        prof.GetYaxis().SetTitle("<" + thisHist.GetYaxis().GetTitle() + ">")
      if xmin != 0 or xmax != 0:
        prof.GetXaxis().SetRangeUser(xmin, xmax)
      if prof.GetMaximum() > ymax: ymax = prof.GetMaximum()
      if prof.GetMinimum < ymin: ymin = prof.GetMinimum()
      profs.append( prof )
      entryName = list(names[iHist].split('+'))[0]
      #if "somthing" in entryName: entryName = something else
      if entryName == "26763": entryName = "Period A4"
      if entryName == "271"  : entryName = "Period C2"
      if entryName == "27"   : entryName = "Period C2+partial 3"
      leg.AddEntry( prof, entryName, "p")

    ## Get ratio ##
    if (plotRatio):
      ratioHists = []
      # Get first data point
      iDataHist = histTypes.index(args.ratioWRT)

      if histTypes.count("data") == histTypes.count("bkg"):
        tmpRatioHistList=[]
        #tmpErrorHistList=[]
        tmpMCHistList=[]
        for i in range(0,len(profs)):
          #if histTypes[i] == "data": tmpRatioHistList.append( profs[i].Clone(hists[i].GetName()+"_ratio"))
          #if histTypes[i] == "bkg": tmpMCHistList.append( profs[i].Clone( hists[i].GetName()+"_tmp" ))
          if histTypes[i] == "data":
            tmpRatioHistList.append( profs[i].ProjectionX(hists[i].GetName()+"_ratio", "E") )
            #tmpErrorHistList.append( profs[i].ProjectionX(hists[i].GetName()+"_ratio", "C=E") ) # content = error
          if histTypes[i] == "bkg": tmpMCHistList.append( profs[i].ProjectionX( hists[i].GetName()+"_tmp", "e") )
        for i in range(histTypes.count("data")):
          tmpRatioHist = tmpRatioHistList[i]
          #tmpErrorHist = tmpErrorHistList[i]
          tmpMCHist = tmpMCHistList[i]

          #tmpRatioHist.Add(tmpMCHist,-1.)
          #tmpRatioHist.Divide(tmpErrorHist)
          tmpRatioHist.Divide(tmpMCHist)
#          for i in range(0,tmpRatioHist.GetNbinsX()+1):
#            content = tmpRatioHist.GetBinContent(i) - tmpMCHist.GetBinContent(i)

          print profs[iDataHist].GetXaxis().GetTitle()
          tmpRatioHist.GetXaxis().SetTitle(profs[iDataHist].GetXaxis().GetTitle())
          if xmin != 0 or xmax != 0:
            tmpRatioHist.GetXaxis().SetRangeUser(xmin, xmax)

#          tmpRatioHist.GetYaxis().SetTitleSize( 0.15 )
#          tmpRatioHist.GetYaxis().SetLabelSize( 0.14 )
#          tmpRatioHist.GetYaxis().SetTitleOffset( 0.4 )
#          tmpRatioHist.GetXaxis().SetLabelSize( 0.17 )
#          tmpRatioHist.GetXaxis().SetTitleSize( 0.17 )
#          tmpRatioHist.GetXaxis().SetTitleOffset( 1 )
          tmpRatioHist.GetYaxis().SetNdivisions(7)
          tmpMin=tmpRatioHist.GetMinimum()+tmpRatioHist.GetMinimum()/100000.
          tmpRatioHist.GetYaxis().SetRangeUser(tmpMin, tmpRatioHist.GetMaximum())
          #tmpRatioHist.GetYaxis().SetTitle("#splitline{Relative}{Difference}")
          tmpRatioHist.GetYaxis().SetTitle("Data/MC")
        #if maxbin != 0:
        #  tmpRatioHist.GetXaxis().SetRange(0,maxbin+5)

          ratioHists.append( tmpRatioHist )

      ############################## Being Ratio y-axis ###############################
      ## Fix ratio Y-axis ##
      yMax = args.ratioRange2DMax
      yMin = args.ratioRange2DMin
      # exact match if jet in name
      if any( ratioRangeString.split(',')[0] in hName and not "jet_" in ratioRangeString.split(',')[0] for ratioRangeString in ratioRange ):
        ratioRangeString = [ratioRangeString for ratioRangeString in ratioRange if ratioRangeString.split(',')[0] in hName][0]
        yMin = float(ratioRangeString.split(',')[1])
        yMax = float(ratioRangeString.split(',')[2])
      # not exact match if jet not in name
      if any( ratioRangeString.split(',')[0] == hName and "jet_" in ratioRangeString.split(',')[0] for ratioRangeString in ratioRange ):
        ratioRangeString = [ratioRangeString for ratioRangeString in ratioRange if ratioRangeString.split(',')[0] in hName][0]
        yMin = float(ratioRangeString.split(',')[1])
        yMax = float(ratioRangeString.split(',')[2])

      ## If yMax and yMin are 0, then use range determined by ROOT ##
      if yMax !=0 and yMin != 0:
        for i in range(0, len(ratioHists)):
          ratioHists[i].SetMaximum(yMax)
          ratioHists[i].SetMinimum(yMin)

    if (plotRatio):
      for i in range(0, len(profs)):
        if profs[i].GetMinimum() < 0.0001:
          profs[i].SetMinimum(0.0001)

    #%%%%%%%%%%%%%%%%%%%% End ratio hists ymax code %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

    profs[0].SetMaximum( 1.8*ymax )
    profs[0].SetMinimum(ymin+0.0001)
#    profs[0].GetYaxis().SetTitleOffset(1)
#    profs[0].GetXaxis().SetTitleSize(0.08)
#    profs[0].GetYaxis().SetTitleSize(0.08)
#    profs[0].GetXaxis().SetLabelSize(0.08)
#    profs[0].GetYaxis().SetLabelSize(0.08)
    profs[0].Draw('p')
    for i in range(1,len(profs)):
      profs[i].Draw("psame")
    leg.Draw("same")
    AtlasStyle.ATLAS_LABEL(0.20,0.88)
    sqrtSLumiText = getSqrtSLumiText( args.lumi )
    AtlasStyle.myText(0.20,0.82,1, sqrtSLumiText)
    if len(args.plotText)>0:
      AtlasStyle.myText(0.20,0.76,1, args.plotText)

   #############################################################
    if (plotRatio):
      pad2.cd()
#      for i in range(0,len(ratioHists)):
#        ratioHists[i].Draw( "p" )
      if len(ratioHists) > 0:
        #ratioHists[0].SetMarkerColor( ROOT.kBlack )
        #ratioHists[0].SetLineColor( ROOT.kBlack )
        ratioHists[0].Draw( "p" )
      for rat in ratioHists:
        rat.Draw("psame")

      #zeroLine.Draw("same")
      oneLine.Draw("same")


    c0.Print(args.plotDir + "/" + outputTag + '_' + hName + '_allProfiled'+outputVersion+'.png',"png") #,"png")
#    c0.Print(args.plotDir + "/" + outputTag + '_' + hName + '_allProfiled'+outputVersion+'.pdf',"pdf") #,"pdf")
    if plotRatio:
      pad1.cd()

    c0.Clear()

    ## for 2D hists with data draw relative difference of (data-MC)/MC
    #if len(args.dataType) == 1:
    #  iData = histTypes.index("data")
    #  for iHist, thisHist in enumerate(hists):
    #    if iHist != iData:
    #      tmpHist = hists[iData].Clone("tmp")
    #      tmpHist.Add( thisHist, -1.)
    #      tmpHist.Divide( thisHist )
    #      hists[iHist] = tmpHist

    ymin2d, ymax2d = 0,0
    for iHist, thisHist in enumerate(hists):
      if xmin != 0 or xmax != 0:
        thisHist.GetXaxis().SetRangeUser(xmin, xmax)
      if any( "__"+range2DyString.split(',')[0] in hName for range2DyString in range2Dy):
        range2DyString = [range2DyString for range2DyString in range2Dy if range2DyString.split(',')[0] in hName][0]
        ymin2d = float(range2DyString.split(',')[1])
        ymax2d = float(range2DyString.split(',')[2])
      if ymin2d != 0 and ymax2d != 0:
        thisHist.GetYaxis().SetRangeUser(ymin2d, ymax2d)

#      c0.SetRightMargin(0.15)
#      thisHist.GetYaxis().SetTitleOffset(0.9)
#      thisHist.GetYaxis().SetTitleSize(0.08)
#      thisHist.GetXaxis().SetTitleSize(0.08)
#      thisHist.GetYaxis().SetLabelSize(0.08)
#      thisHist.GetXaxis().SetLabelSize(0.08)

      thisHist.DrawCopy("colz")
      prof = thisHist.ProfileX( thisHist.GetName() + "_ProfileX" )
      if xmin != 0 or xmax != 0:
        thisHist.GetXaxis().SetRangeUser(xmin, xmax)
        prof.GetXaxis().SetRangeUser(xmin, xmax)
      #  draw the X profile on the plot
      prof.SetMarkerColor(ROOT.kBlack)
      prof.SetLineColor(ROOT.kWhite)
      prof.SetMarkerStyle(24)
      prof.Draw("same")

      AtlasStyle.ATLAS_LABEL(0.20,0.88)
      sqrtSLumiText = getSqrtSLumiText( args.lumi )
      AtlasStyle.myText(0.20,0.82,1, sqrtSLumiText)
      if len(args.plotText)>0:
        AtlasStyle.myText(0.20,0.76,1, args.plotText)
      c0.Print(args.plotDir + "/" + outputTag + "_" + hName + '_' + names[iHist] + outputVersion + ".png","png") #,"png")
#      c0.Print(args.plotDir + "/" + outputTag + "_" + hName + '_' + names[iHist] + outputVersion + ".pdf","pdf") #,"pdf")


  return

#####################################################

##  END      FUNCTIONS TO CALL PLOTNTUPLE.PY      ##
####################################################



####################################################
##  START    FUNCTIONS TO CALL PLOTNTUPLE.PY      ##
####################################################
# derive a weight to have the same NPV
def deriveReweight( h_hists, h_histTypes, outputTag, outputVersion, var ):
  ## copy these as they can be changed ##
  #names = copy.copy(h_names)
  hists = copy.copy(h_hists)
  histTypes = copy.copy(h_histTypes)

  iData = histTypes.index("data")
  integralData = hists[iData].Integral()
  iBkg = histTypes.index("bkg")
  integralBkg = hists[iBkg].Integral()
  hists[iBkg].Draw()
  time.sleep(2)
  normScale = integralData / integralBkg


  rwHist = hists[iData].Clone( "rewight_" + var )
  rwHist.Reset()
  for ibin in range(1, rwHist.GetNbinsX()+1):
    if hists[iBkg].GetBinContent(ibin) == 0: continue
    rwValue = hists[iData].GetBinContent(ibin) / hists[iBkg].GetBinContent(ibin)
    rwHist.SetBinContent( ibin, rwValue )

# don't change the mc integral
  #rwHist.Scale(1. / normScale)


  npvReweightFile = ROOT.TFile(args.plotDir + "/" + outputTag + "_reweight" + outputVersion + "_" + var + ".root", 'RECREATE')
  rwHist.Write()
  npvReweightFile.Close()

  return rwHist

def getSqrtSLumiText( lumi ):
  sqrtSLumiText = "#sqrt{s}=13 TeV"
  sqrtSLumiText += ", 80.4 pb^{-1}"
#  Periods 12 = 13 / pb
#  Periods 3 = 20 / pb
  #if lumi > 0:
  #  if lumi > 1:
  #    sqrtSLumiText += ", " + str(lumi) + " fb^{-1}"
  #  else: # make 1/pb
  #    lumi *= 1e3
  #    lumiStr = str(lumi)
  #    lumiStr = lumiStr.rstrip("0").rstrip(".")
  #    sqrtSLumiText += ", " + lumiStr + " pb^{-1}"
  return sqrtSLumiText


####################################################
##  END      FUNCTIONS TO CALL PLOTNTUPLE.PY      ##
####################################################

####################################################
##               Control parallel jobs            ##
##       taken from bkgFit/runSingleFit.py        ##
####################################################
def submit_local_job(exec_sequence, logfilename):
  #os.system("rm -f "+logfilename)
  output_f=open(logfilename, 'w')
  pid = subprocess.Popen(exec_sequence, shell=True, stderr=output_f, stdout=output_f)
  time.sleep(0.5)  #Wait to prevent opening / closing of several files

  return pid, output_f

def wait_completion(pids, logFiles):
  print """Wait until the completion of all of the launched jobs"""
  while True:
    for pid in pids:
      if pid.poll() is not None:
        print "\nProcess", pid.pid, "has completed"
        logFiles.pop(pids.index(pid)).close()  #remove logfile from list and close it
        pids.remove(pid)

        return
    print ".",
    sys.stdout.flush()
    time.sleep(3) # wait before retrying

def wait_all(pids, logFiles):
  print """Wait until the completion of all launched jobs"""
  while len(pids)>0:
    wait_completion(pids, logFiles)
  print "All jobs finished!"
####################################################
##    END        Control parallel jobs            ##
####################################################

if __name__ == "__main__":
    getPlotLists()









