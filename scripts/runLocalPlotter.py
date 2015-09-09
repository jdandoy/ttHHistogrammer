#!/usr/bin/python

##############################################################
# runLocalPlotter.py                                         #
##############################################################
# Submit PlotMinitree jobs locally on a folder of TTrees     #
##############################################################
# Jeff.Dandoy and Nedaa.Asbah                                #
##############################################################

import os, math, sys, glob, subprocess, time, shutil

def main():
  test = False # does not run the jobs
  if not test:
    if not os.path.exists("gridOutput/localJobs"):
      os.makedirs('gridOutput/localJobs')

  config_name = "$ROOTCOREBIN/data/ttHHistogrammer/ttHHistogrammer.config"

  fileDir = '/home/jdandoy/Documents/ttHFW/gridOutput/output/'
  inputTag = ''
  outputTag = 'test'

  timestamp = time.strftime("_%Y%m%d")
  outputTag += timestamp

  files = glob.glob(fileDir+'/*'+inputTag+'*.root')


  if not os.path.exists('logs/'+outputTag+'/'):
    os.makedirs('logs/'+outputTag+'/')

  pids, logFiles = [], []
  NCORES = 6
  ## Submit histogramming jobs ##
  for file in files:
    if len(pids) >= NCORES:
      wait_completion(pids, logFiles)

    fileTag = os.path.basename(file)[:-5] #remove path and .root
    logFile='logs/'+outputTag+'/ttHHistogrammer_{0}'.format(fileTag)+'.log'
    submit_dir = 'gridOutput/localJobs/'+fileTag
    #this_output_tag = '...'+outputTag

    command = 'runttHHistogrammer  --file '+file+' --submitDir '+submit_dir+' --configName '+config_name
    print command
    #command = 'runMiniTree  -inFile '+file+' -outputTag '+this_output_tag+' -submitDir '+submit_dir+' -configName '+config_name

    if not test:
      res = submit_local_job(command, logFile)
      pids.append(res[0])
      logFiles.append(res[1])

  wait_all(pids, logFiles)
  for f in logFiles:
    f.close()

  ## Now collect output ##
  if not os.path.exists("gridOutput/histOutput"):
    os.makedirs('gridOutput/histOutput')


  print 'Moving files to gridOutput/histOutput'
  outDirs = glob.glob('gridOutput/localJobs/*')
  for outDir in outDirs:
    shutil.move( outDir+'/hist-output.root', 'gridOutput/histOutput/hists_'+os.path.basename(outDir)+'.root' )


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
