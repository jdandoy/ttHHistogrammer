##############################################################
# commandPlot.sh                                             #
##############################################################
# A dump of different commands for running plotHistograms.py #
##############################################################
# Jeff.Dandoy and Nedaa.Asbah                                #
##############################################################

python plotHistograms.py -b --inDir gridOutput/output.root/ --bkgType 410000,aMc --dataType physics_Main --stackBkg

python plotHistograms.py -b --inDir gridOutput/output.root/ --bkgType SingleTop:Wt,W+jets:Wplus=Wminus,Z+jets:Zee=Zmumu=Ztautau,Diboson:ZZ=WpZ=WmZ=WpWm,ttbar,ttH --dataType Data:physics_Main --stackBkg --plotRatio --normToData


WpZ check:
python plotHistograms.py -b --inDir gridOutput/output.root/ --bkgType WpZ_3e,WpZ_e2mu,WpZ_e2tau,WpZ_mu2e,WpZ_3mu,WpZ_mu2tau,WpZ_tau2e,WpZ_tau2mu,WpZ_3tau


New:
python ttHPlotter/scripts/plotting/plotHistograms.py -b --inDir gridOutput/histOutput/ --bkgType WpZ_3e,WpZ_e2mu,WpZ_e2tau,WpZ_mu2e,WpZ_3mu,WpZ_mu2tau,WpZ_tau2e,WpZ_tau2mu,WpZ_3tau

python ttHPlotter/scripts/plotting/plotHistograms.py -b --plotDir sel_mu_4j_2b --inDir gridOutput/histOutput/ --bkgType SingleTop:Wt,W+jets:Wplus=Wminus,Z+jets:Zee=Zmumu=Ztautau,Diboson:ZZ=WpZ=WmZ=WpWm,ttbar,ttH --dataType Data:physics_Main --stackBkg --plotRatio --normToData
