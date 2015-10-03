#!/usr/bin/python

##############################################################
# runLocalPlotter.py                                         #
##############################################################
# Submit PlotMinitree jobs locally on a folder of TTrees     #
##############################################################
# Jeff.Dandoy and Nedaa.Asbah                                #
##############################################################

import os, subprocess, time, sys

def main():
  test = False # does not run the job

  inDir = "gridOutput/histOutput/"
  plotDirs = ["sel_el_4j_2b"]
  dataType = "D3:276262=276329=276330=276336,D4:276416=276511=276689,D5:276731,D6:276778=276790=276952=276954,E2:278748=278880=278912,E3:278968=278970=279169=279259=279279=279284,E4:279345=279515=279598=279685"
  bkgType=""

  #plotDirs = ["sel_mu_4j","sel_mu_4j_2b","sel_mu_4j_3b","sel_mu_4j_4b"]
  #plotDirs += ["sel_el_4j","sel_el_4j_2b","sel_el_4j_3b","sel_el_4j_4b"]
  #bkgType = "SingleTop:Wt,W+jets:Wplus=Wminus,Z+jets:Zee=Zmumu=Ztautau,Diboson:ZZ=WpZ=WmZ=WpWm,ttbar,ttH"
  #dataType = "Data:physics_Main"
  stackBkg = False
  plotRatio = False

  normToData = False
  lumi = 232
  #Luminosities: PeriodC 85, PeriodD 80, PeriodE


  if not os.path.exists('logs/plotting/'):
    os.makedirs('logs/plotting/')

  ncores = 4
  pids, logFiles = [], []
  ## Submit histogramming jobs ##
  for plotDir in plotDirs:
    if len(pids) >= ncores:
      wait_completion(pids, logFiles)

    logFile='logs/plotting/{0}'.format(plotDir)+'.log'


    sendCommand = 'python ttHHistogrammer/scripts/plotting/plotHistograms.py -b --plotDir '+plotDir+' --inDir '+inDir+' --dataType '+dataType+' '
    if len(bkgType) > 0:
      sendCommand += '--bkgType '+bkgType+' '
    if stackBkg:
      sendCommand += '--stackBkg '
    if plotRatio:
      sendCommand += '--plotRatio '
    if lumi > 0:
      sendCommand += '--lumi '+str(lumi)+' '
    print sendCommand

    if not test:
      res = submit_local_job(sendCommand, logFile)
      pids.append(res[0])
      logFiles.append(res[1])

  wait_all(pids, logFiles)
  for f in logFiles:
    f.close()

def submit_local_job(exec_sequence, logfilename):
  output_f=open(logfilename, 'w')
  pid = subprocess.Popen(exec_sequence, shell=True, stderr=output_f, stdout=output_f)
  time.sleep(0.5)  #Wait to prevent opening / closing of several files

  return pid, output_f

def wait_completion(pids, logFiles):
  print """Wait until the completion of one of the launched jobs"""
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

if __name__ == "__main__":
    main()
