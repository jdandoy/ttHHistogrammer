#!/usr/bin/python

##############################################################
# runLocalPlotter.py                                         #
##############################################################
# Submit PlotMinitree jobs locally on a folder of TTrees     #
##############################################################
# Jeff.Dandoy and Nedaa.Asbah                                #
##############################################################

import os, math, sys, glob, subprocess, time, shutil
import argparse
parser = argparse.ArgumentParser(description="%prog [options]", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("--path", dest='fileDir', default="./",
     help="Path to the directory containing the input TTrees")
parser.add_argument("--inTag", dest='inputTag', default="",
     help="Input tag for choosing files")
parser.add_argument("--outTag", dest='outputTag', default="NewStudy",
     help="Output tag for the histogram root files")
parser.add_argument("--ncores", dest='ncores', default=4,
     type=int, help="Number of parallel jobs ")
parser.add_argument("--config", dest='config', default="$ROOTCOREBIN/data/ttHHistogrammer/ttHHistogrammer.config",
     help="ttHHistogrammer config file")
args = parser.parse_args()



def main():
  test = False # does not run the jobs
  if not test:
    if not os.path.exists("gridOutput/localJobs"):
      os.makedirs('gridOutput/localJobs')

  args.outputTag += time.strftime("_%Y%m%d")

  files = glob.glob(args.fileDir+'/*'+args.inputTag+'*.root')

  if not os.path.exists('logs/'+args.outputTag+'/'):
    os.makedirs('logs/'+args.outputTag+'/')

  pids, logFiles = [], []
  ## Submit histogramming jobs ##
  for file in files:
    if len(pids) >= args.ncores:
      wait_completion(pids, logFiles)

    fileTag = os.path.basename(file)[:-5] #remove path and .root
    logFile='logs/'+args.outputTag+'/ttHHistogrammer_{0}'.format(fileTag)+'.log'
    submit_dir = 'gridOutput/localJobs/'+fileTag
    #this_output_tag = '...'+args.outputTag

    command = 'runttHHistogrammer  --file '+file+' --submitDir '+submit_dir+' --configName '+args.config
    print command

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
  ## Output is named hist-output.root by default; Rename and move these files ##
  for outDir in outDirs:
    shutil.move( outDir+'/hist-output.root', 'gridOutput/histOutput/hists_'+os.path.basename(outDir)+'.root' )
  shutil.rmtree('gridOutput/localJobs')


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
