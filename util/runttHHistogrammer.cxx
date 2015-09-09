//////////////////////////////////////////////////////////////////
// runtthPlotter.cxx                                            //
//////////////////////////////////////////////////////////////////
// Control script for the PlotMiniTree EventLoop.               //
// Selects general running options and controls grid submission.//
//////////////////////////////////////////////////////////////////
// Jeff.Dandoy@cern.ch , Nedaa.Asbah@cern.ch                    //
//////////////////////////////////////////////////////////////////

#include "EventLoop/Job.h"
#include "ttHPlotter/PlotMiniTree.h"

#include "xAODAnaHelpers/AnalysisBase.h"
#include <string>
#include <unistd.h>

#include "TEnv.h"
#include "TString.h"
#include "TSystem.h"

using namespace std;

int main( int argc, char* argv[] ) {

  //
  // Create the EventLoop job:
  //
  EL::Job job;

  //
  // Init various job options
  //
  std::string configName = "$ROOTCOREBIN/data/ttHPlotter/ttHPlotter.config";
  std::string treeName   = "nominal";
  std::string submitDir  = "submitDir";
  std::string outputName;
  bool doCondor          = false;

  /////////// Retrieve job arguments //////////////////////////
  std::vector< std::string> options;
  for(int ii=1; ii < argc; ++ii){
    options.push_back( std::string(argv[ii]) );
  }


  if (argc > 1 && options.at(0).compare("-h") == 0) {
    std::cout << std::endl
         << " job submission" << std::endl
         << std::endl
         << " Optional arguments:" << std::endl
         << "  -h                Prints this menu" << std::endl
         << "  --file            Path to a folder, root file, or text file" << std::endl
         << "  --outputTag       Version string to be appended to job name" << std::endl
         << "  --submitDir       Name of output directory" << std::endl
         << "  --configName      Path to config file" << std::endl
         << "  --treeName        Name of input TTree" << std::endl
         << "  --condor          Option for running condor (Disabled)" << std::endl
         << std::endl;
    exit(1);
  }

  std::string samplePath = ".";
  std::string outputTag = "";

  int iArg = 0;
  while(iArg < argc-1) {

    if (options.at(iArg).compare("-h") == 0) {
       // Ignore if not first argument
       ++iArg;

    } else if (options.at(iArg).compare("--file") == 0) {
       char tmpChar = options.at(iArg+1)[0];
       if (iArg+1 == argc || tmpChar == '-' ) {
         std::cout << " --file should be followed by a file or folder" << std::endl;
         return 1;
       } else {
         samplePath = options.at(iArg+1);
         iArg += 2;
       }

    } else if (options.at(iArg).compare("--outputTag") == 0) {
       char tmpChar = options.at(iArg+1)[0];
       if (iArg+1 == argc || tmpChar == '-' ) {
         std::cout << " --outputTag should be followed by a job version string" << std::endl;
         return 1;
       } else {
         outputTag = options.at(iArg+1);
         iArg += 2;
       }

    } else if (options.at(iArg).compare("--submitDir") == 0) {
       char tmpChar = options.at(iArg+1)[0];
       if (iArg+1 == argc || tmpChar == '-' ) {
         std::cout << " --submitDir should be followed by a folder name" << std::endl;
         return 1;
       } else {
         submitDir = options.at(iArg+1);
         iArg += 2;
       }

    } else if (options.at(iArg).compare("--configName") == 0) {
       char tmpChar = options.at(iArg+1)[0];
       if (iArg+1 == argc || tmpChar == '-' ) {
         std::cout << " --configName should be followed by a config file" << std::endl;
         return 1;
       } else {
         configName = options.at(iArg+1);
         iArg += 2;
       }

    } else if (options.at(iArg).compare("--treeName") == 0) {
       char tmpChar = options.at(iArg+1)[0];
       if (iArg+1 == argc || tmpChar == '-' ) {
         std::cout << " --treeName should be followed by a tree name" << std::endl;
         return 1;
       } else {
         treeName = options.at(iArg+1);
         iArg += 2;
       }

    } else if (options.at(iArg).compare("--condor") == 0) {
      std::cout << "Running on condor" << std::endl;
      doCondor = true;
      iArg += 1;

    }else{
      std::cout << "Couldn't understand argument " << options.at(iArg) << std::endl;
      return 1;
    }

  }//while arguments


  // Construct the samples to run on:
  SH::SampleHandler sh;
  std::string containerName;
  std::string userName = getlogin();

  //Check if input is a directory or a file
  struct stat buf;
  stat(samplePath.c_str(), &buf);
  if( S_ISDIR(buf.st_mode) ){ //if it is a directory
    SH::DiskListLocal list (samplePath);
    SH::scanDir (sh, list); // Run on all files within dir
    std::cout << "Running Locally on directory  " << samplePath << std::endl;

  } else {  //if it is a file
    if( samplePath.substr( samplePath.size()-4 ).find(".txt") != std::string::npos){ //It is a text file of samples

      std::ifstream inFile( samplePath );
      while(std::getline(inFile, containerName) ){
        if (containerName.size() > 1 && containerName.find("#") != 0 ){
          std::cout << "Adding container " << containerName << std::endl;
	  //Get full path of file
	  char fullPath[300];
	  realpath( containerName.c_str(), fullPath );
	  std::string thisPath = fullPath;
	  //split into fileName and directory two levels above file
	  std::string fileName = thisPath.substr(containerName.find_last_of("/")+1);
	  thisPath = thisPath.substr(0, thisPath.find_last_of("/"));
	  thisPath = thisPath.substr(0, thisPath.find_last_of("/"));
	  std::cout << "path and filename are " << thisPath << " and " << fileName << std::endl;

	  SH::DiskListLocal list (thisPath);
	  //SH::SampleHandler sh_tmp;
	  //SH::scanDir (sh_tmp, list);
	  //sh.add( sh_tmp.findByName, ("*"+fileName).c_str() );
	  SH::scanDir (sh, list, fileName); // specifying one particular file for testing
        }
      }

    }else{ //It is a single root file to run on
    //Get full path of file
    char fullPath[300];
    realpath( samplePath.c_str(), fullPath );
    std::string thisPath = fullPath;
    //split into fileName and directory two levels above file
    std::string fileName = thisPath.substr(thisPath.find_last_of("/")+1);
    thisPath = thisPath.substr(0, thisPath.find_last_of("/"));
    thisPath = thisPath.substr(0, thisPath.find_last_of("/"));

    std::cout << "path and file " << thisPath << " and " << fileName << std::endl;
    SH::DiskListLocal list (thisPath);
    SH::scanDir (sh, list, fileName); // specifying one particular file for testing

    }
  }//it's a file

  ///////// Set output container name //////////////
  if( outputTag.size() > 0)
    outputTag = "."+outputTag+"/";
  else
    outputTag = "/";

  outputName = "%in:name%"+outputTag;

  // Set the name of the input TTree. It's always "CollectionTree" for xAOD files.
  sh.setMetaString( "nc_tree", treeName );
  sh.print();

  job.sampleHandler( sh );
  // To automatically delete submitDir
  job.options()->setDouble(EL::Job::optRemoveSubmitDir, 1);

  //
  //  Set the number of events
  //
  TEnv* config = new TEnv(gSystem->ExpandPathName( configName.c_str() ));
  int nEvents = config->GetValue("MaxEvent",       -1);
  if(nEvents > 0)
    job.options()->setDouble(EL::Job::optMaxEvents, nEvents);

  //
  // Now the Event/Objection Selection
  //


  //
  // The Multijet analysis
  //   (defined in MultijetAlgo base class)
  std::string PlotMiniTreeConfig = configName;
  PlotMiniTreeConfig.erase(0, PlotMiniTreeConfig.find_last_of("/")+1); // correct config name to include $ROOTCOREBIN
  PlotMiniTreeConfig = "$ROOTCOREBIN/data/ttHPlotter/"+PlotMiniTreeConfig;
  PlotMiniTree* procMiniTree = new PlotMiniTree();
  cout << "PlotMiniTreeConfig is " << PlotMiniTreeConfig << endl;
  procMiniTree->setName("ttHPlotter")->setConfig( PlotMiniTreeConfig.c_str() );

  //
  // Add configured algos to event loop job
  //
  job.algsAdd( procMiniTree );

  //
  // Submit the job (defined in utils/AnalysisBase.h)
  //
  submitJob(job, outputName, submitDir, false, false, std::vector<std::string>(), doCondor );

  return 0;
}

