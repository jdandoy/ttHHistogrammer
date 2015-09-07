python makeStandardPlots.py -b --inDir gridOutput/output.root/ --bkgType 410000,aMc --dataType physics_Main --stackBkg

python makeStandardPlots.py -b --inDir gridOutput/output.root/ --bkgType SingleTop:Wt,W+jets:Wplus=Wminus,Z+jets:Zee=Zmumu=Ztautau,Diboson:ZZ=WpZ=WmZ=WpWm,ttbar,ttH --dataType Data:physics_Main --stackBkg --plotRatio --normToData


WpZ check:
python makeStandardPlots.py -b --inDir gridOutput/output.root/ --bkgType WpZ_3e,WpZ_e2mu,WpZ_e2tau,WpZ_mu2e,WpZ_3mu,WpZ_mu2tau,WpZ_tau2e,WpZ_tau2mu,WpZ_3tau


New:

python makeStandardPlots.py -b --inDir gridOutput/histOutput/ --bkgType SingleTop:Wt,W+jets:Wplus=Wminus,Z+jets:Zee=Zmumu=Ztautau,Diboson:ZZ=WpZ=WmZ=WpWm,ttbar,ttH --dataType Data:physics_Main --stackBkg --plotRatio --normToData
