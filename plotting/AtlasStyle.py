#!/usr/bin/env python
#
# Python ATLAS Style: Based on ATLAS Style

import ROOT
import array

def ATLAS_LABEL(x, y, color=1, label = "Internal"):
    l = ROOT.TLatex()  #l.SetTextAlign(12); l.SetTextSize(tsize);
    l.SetNDC()
    l.SetTextFont(72)
    l.SetTextColor(color)
    l.DrawLatex(x,y,"ATLAS Internal")
    l2 = ROOT.TLatex()  #l.SetTextAlign(12); l.SetTextSize(tsize);
    l2.SetNDC()
    l2.SetTextColor(color)
    l2.DrawLatex(x+8,y,"Internal")


def myText(x, y, color, text):
  #tsize=0.05
    l = ROOT.TLatex()  #l.SetTextAlign(12); l.SetTextSize(tsize);
    l.SetNDC()
    l.SetTextColor(color)
    l.DrawLatex(x,y,text)


def SetAtlasStyle():
    print "Applying ATLAS style settings..."
    atlasStyle = AtlasStyle()
    ROOT.gStyle = atlasStyle
    ROOT.gROOT.SetStyle("ATLAS")
    ROOT.gROOT.ForceStyle()
#def SetAtlasStyle

def AtlasStyle():
    print "Create ATLAS Style"
    atlasStyle = ROOT.TStyle("ATLAS","Atlas style")

    #Use black and white
    icol=0; #WHITE
    atlasStyle.SetFrameBorderMode(icol);
    atlasStyle.SetFrameFillColor(icol);
    atlasStyle.SetCanvasBorderMode(icol);
    atlasStyle.SetCanvasColor(icol);
    atlasStyle.SetPadBorderMode(icol);
    atlasStyle.SetPadColor(icol);
    atlasStyle.SetStatColor(icol);

    # set the paper & margin sizes
    atlasStyle.SetPaperSize(20,26);

    # set margin sizes
    atlasStyle.SetPadTopMargin(0.05);
    atlasStyle.SetPadRightMargin(0.10);
    atlasStyle.SetPadBottomMargin(0.16);
    atlasStyle.SetPadLeftMargin(0.16);

    # set title offsets (for axis label)
    atlasStyle.SetTitleXOffset(1.4);
    atlasStyle.SetTitleYOffset(1.4);

    # use large fonts
    font=42; # Helvetica
    size=0.05;
    atlasStyle.SetTextFont(font);
    atlasStyle.SetTextSize(size);
    atlasStyle.SetTitleFont(font,"t");
    atlasStyle.SetLabelFont(font,"x");
    atlasStyle.SetTitleFont(font,"x");
    atlasStyle.SetLabelFont(font,"y");
    atlasStyle.SetTitleFont(font,"y");
    atlasStyle.SetLabelFont(font,"z");
    atlasStyle.SetTitleFont(font,"z");
    atlasStyle.SetLabelSize(size,"x");
    atlasStyle.SetTitleSize(size,"x");
    atlasStyle.SetLabelSize(size,"y");
    atlasStyle.SetTitleSize(size,"y");
    atlasStyle.SetLabelSize(size,"z");
    atlasStyle.SetTitleSize(size,"z");

    # use bold lines and markers
    atlasStyle.SetMarkerStyle(20);
    atlasStyle.SetMarkerSize(1.2);
    atlasStyle.SetHistLineWidth(2);
    atlasStyle.SetLineStyleString(2,"[12 12]"); # postscript dashes
    atlasStyle.SetFuncColor(ROOT.kRed);
    atlasStyle.SetLineColor(ROOT.kRed);
    #atlasStyle.SetHistLineColor(ROOT.kRed);

    # get rid of X error bars and y error bar caps
    atlasStyle.SetEndErrorSize(0.);

    # do not display any of the standard histogram decorations
    atlasStyle.SetLegendFillColor(0);
    atlasStyle.SetLegendBorderSize(0);
    atlasStyle.SetOptTitle(0);
    atlasStyle.SetOptStat(0);
    atlasStyle.SetOptFit(0);

    # put tick marks on top and RHS of plots
    atlasStyle.SetPadTickX(1);
    atlasStyle.SetPadTickY(1);

    #Define colours for COLZ option

    nrgbs = 5
    ncont = 250
    stops = array.array('d',[ 0.00, 0.34, 0.61, 0.84, 1.00 ])
    red   = array.array('d',[ 0.00, 0.00, 0.87, 1.00, 0.51 ])
    green = array.array('d',[ 0.00, 0.81, 1.00, 0.20, 0.00 ])
    blue  = array.array('d',[ 0.51, 1.00, 0.12, 0.00, 0.00 ])
    ROOT.TColor.CreateGradientColorTable(nrgbs, stops, red, green, blue, ncont)
    atlasStyle.SetNumberContours(ncont);

    return atlasStyle;

#def AtlasStyle
