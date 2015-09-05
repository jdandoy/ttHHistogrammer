#!/usr/bin/python

#####################################
# Submit grid jobs using text files with lists of containers
# For questions contact Jeff.Dandoy@cern.ch
#####################################

import os, math, sys, glob
from time import strftime

def main():
  test = True # does not run the jobs
  if not test:
    if not os.path.exists("gridOutput"):
      os.system("mkdir gridOutput")
    if not os.path.exists("gridOutput/localJobs"):
      os.system("mkdir gridOutput/localJobs")

  config_name = "$ROOTCOREBIN/data/ttHPlotter/ttHPlotter.config"

  fileDir = ''
  inputTag = ''
  outputTag = ''

  timestamp = strftime("_%Y%m%d")
  outputTag += timestamp

  files = glob.glob(fileDir+'/*'+inputTag+'*.root')

  pids, logFiles = [], []
  NCORES = 6

  if not os.path.exists('logs/'+outputTag+'/'):
    os.makedirs('logs/'+outputTag+'/')

  for file in files:

    fileTag = ''
    logFile='logs/'+outputTag+'/ttHPlotter_{0}'.format(fileTag)
    submit_dir = 'gridOutput/localJobs/'
    this_output_tag = '...'+outputTag

    command = 'runMiniTree  -inFile '+file+' -outputTag '+this_output_tag+' -submitDir '+submit_dir+' -configName '+config_name

    if not test:
      res = submit_local_job(command, logFile)
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
