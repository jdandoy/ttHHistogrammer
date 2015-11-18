//////////////////////////////////////////////////////////////////
// HistogramMiniTree.cxx                                             //
//////////////////////////////////////////////////////////////////
// Fairly generic EventLoop for creating histograms from TTrees //
// Currently optimized for the ttH TTree output                 //
//////////////////////////////////////////////////////////////////
// Jeff.Dandoy@cern.ch , Nedaa.Asbah@cern.ch                    //
//////////////////////////////////////////////////////////////////

#include <EventLoop/Job.h>
#include <EventLoop/Worker.h>
#include "EventLoop/OutputStream.h"
#include "AthContainers/ConstDataVector.h"

#include "xAODTracking/VertexContainer.h"
#include <xAODJet/JetContainer.h>
#include "xAODEventInfo/EventInfo.h"
#include <ttHHistogrammer/HistogramMiniTree.h>
#include <xAODAnaHelpers/HelperFunctions.h>
#include <xAODAnaHelpers/tools/ReturnCheck.h>

#include "TFile.h"
#include "TLeaf.h"
#include "TKey.h"
#include "TLorentzVector.h"
#include "TEnv.h"
#include "TSystem.h"

#include <utility>
#include <iostream>
#include <fstream>
#include <sstream>
#include <stdlib.h>

using namespace std;

// this is needed to distribute the algorithm to the workers
ClassImp(HistogramMiniTree)

// !B! Add branch Variable here
HistogramMiniTree :: HistogramMiniTree () :
//  HLT_mu50(0),
  el_pt(0),
  el_eta(0),
  el_phi(0),
  el_e(0),
  el_charge(0),
  el_topoetcone20(0),
  el_ptvarcone20(0),
  mu_pt(0),
  mu_eta(0),
  mu_phi(0),
  mu_e(0),
  mu_charge(0),
  mu_topoetcone20(0),
  mu_ptvarcone30(0),
  jet_pt(0),
  jet_eta(0),
  jet_phi(0),
  jet_e(0),
  jet_mv1(0),
  jet_mvb(0),
  jet_mv1c(0),
  jet_mv2c00(0),
  jet_mv2c10(0),
  jet_mv2c20(0),
  jet_ip3dsv1(0),
  jet_jvt(0)
{
  Info("HistogramMiniTree()", "Calling constructor");

  m_debug = false;
  m_bTagWP = -0.4434;
  m_trigger = "";
  m_isMC = true;
  m_XSWeight = 1.0;
  m_mcChannelNumber = "";
}


// !S! Add Selections here
EL::StatusCode  HistogramMiniTree :: configure ()
{
  m_configName = gSystem->ExpandPathName( m_configName.c_str() );
  Info("configure()", "Configuing HistogramMiniTree Interface. User configuration read from : %s \n", m_configName.c_str());
  TEnv* config = new TEnv(m_configName.c_str());
  if( !config ) {
    Error("configure()", "Failed to read config file!");
    Error("configure()", "config name : %s",m_configName.c_str());
    return EL::StatusCode::FAILURE;
  }

  // Read Input from .config file
  m_debug                    = config->GetValue("Debug" ,          m_debug );
  m_bTagWP                   = config->GetValue("BTagWP" ,         m_bTagWP );
  m_trigger                  = config->GetValue("Trigger" ,        m_trigger.c_str() );

  HistogramMiniTree::Selection *selection_el_4j = new HistogramMiniTree::Selection( "sel_el_4j", "1 Electron, = 4 jets" );
  selection_el_4j->elNum = 1;
  selection_el_4j->muNum = 0;
  selection_el_4j->jetNum = 4;
  selections.push_back( selection_el_4j );

  HistogramMiniTree::Selection *selection_mu_4j = new HistogramMiniTree::Selection( "sel_mu_4j", "1 Muon, = 4 jets" );
  selection_mu_4j->elNum = 0;
  selection_mu_4j->muNum = 1;
  selection_mu_4j->jetNum = 4;
  selections.push_back( selection_mu_4j );

  HistogramMiniTree::Selection *selection_mu_4j2b = new HistogramMiniTree::Selection( "sel_mu_4j_2b", "1 Muon, = 4 jets, = 2 b-jets" );
  selection_mu_4j2b->elNum = 0;
  selection_mu_4j2b->muNum = 1;
  selection_mu_4j2b->jetNum = 4;
  selection_mu_4j2b->bJetNum = 2;
  selections.push_back( selection_mu_4j2b );

  HistogramMiniTree::Selection *selection_mu_4j3b = new HistogramMiniTree::Selection( "sel_mu_4j_3b", "1 Muon, = 4 jets, = 3 b-jets" );
  selection_mu_4j3b->elNum = 0;
  selection_mu_4j3b->muNum = 1;
  selection_mu_4j3b->jetNum = 4;
  selection_mu_4j3b->bJetNum = 3;
  selections.push_back( selection_mu_4j3b );

  HistogramMiniTree::Selection *selection_mu_4j4b = new HistogramMiniTree::Selection( "sel_mu_4j_4b", "1 Muon, = 4 jets, = 4 b-jets" );
  selection_mu_4j4b->elNum = 0;
  selection_mu_4j4b->muNum = 1;
  selection_mu_4j4b->jetNum = 4;
  selection_mu_4j4b->bJetNum = 4;
  selection_mu_4j4b->bJetEquality = false;
  selections.push_back( selection_mu_4j4b );

  HistogramMiniTree::Selection *selection_el_4j2b = new HistogramMiniTree::Selection( "sel_el_4j_2b", "1 Electron, = 4 jets, = 2 b-jets" );
  selection_el_4j2b->elNum = 1;
  selection_el_4j2b->muNum = 0;
  selection_el_4j2b->jetNum = 4;
  selection_el_4j2b->bJetNum = 2;
  selections.push_back( selection_el_4j2b );

  HistogramMiniTree::Selection *selection_el_4j3b = new HistogramMiniTree::Selection( "sel_el_4j_3b", "1 Electron, = 4 jets, = 3 b-jets" );
  selection_el_4j3b->elNum = 1;
  selection_el_4j3b->muNum = 0;
  selection_el_4j3b->jetNum = 4;
  selection_el_4j3b->bJetNum = 3;
  selections.push_back( selection_el_4j3b );

  HistogramMiniTree::Selection *selection_el_4j4b = new HistogramMiniTree::Selection( "sel_el_4j_4b", "1 Electron, = 4 jets, = 4 b-jets" );
  selection_el_4j4b->elNum = 1;
  selection_el_4j4b->muNum = 0;
  selection_el_4j4b->jetNum = 4;
  selection_el_4j4b->bJetNum = 4;
  selection_el_4j4b->bJetEquality = false;
  selections.push_back( selection_el_4j4b );

  HistogramMiniTree::Selection *selection_mu_5j2b = new HistogramMiniTree::Selection( "sel_mu_5j_2b", "1 Muon, = 5 jets, = 2 b-jets" );
  selection_mu_5j2b->elNum = 0;
  selection_mu_5j2b->muNum = 1;
  selection_mu_5j2b->jetNum = 5;
  selection_mu_5j2b->bJetNum = 2;
  selections.push_back( selection_mu_5j2b );

  HistogramMiniTree::Selection *selection_mu_5j3b = new HistogramMiniTree::Selection( "sel_mu_5j_3b", "1 Muon, = 5 jets, = 3 b-jets" );
  selection_mu_5j3b->elNum = 0;
  selection_mu_5j3b->muNum = 1;
  selection_mu_5j3b->jetNum = 5;
  selection_mu_5j3b->bJetNum = 3;
  selections.push_back( selection_mu_5j3b );

  HistogramMiniTree::Selection *selection_mu_5j4b = new HistogramMiniTree::Selection( "sel_mu_5j_4b", "1 Muon, = 5 jets, = 4 b-jets" );
  selection_mu_5j4b->elNum = 0;
  selection_mu_5j4b->muNum = 1;
  selection_mu_5j4b->jetNum = 5;
  selection_mu_5j4b->bJetNum = 4;
  selection_mu_5j4b->bJetEquality = false;
  selections.push_back( selection_mu_5j4b );

  HistogramMiniTree::Selection *selection_el_5j2b = new HistogramMiniTree::Selection( "sel_el_5j_2b", "1 Electron, = 5 jets, = 2 b-jets" );
  selection_el_5j2b->elNum = 1;
  selection_el_5j2b->muNum = 0;
  selection_el_5j2b->jetNum = 5;
  selection_el_5j2b->bJetNum = 2;
  selections.push_back( selection_el_5j2b );

  HistogramMiniTree::Selection *selection_el_5j3b = new HistogramMiniTree::Selection( "sel_el_5j_3b", "1 Electron, = 5 jets, = 3 b-jets" );
  selection_el_5j3b->elNum = 1;
  selection_el_5j3b->muNum = 0;
  selection_el_5j3b->jetNum = 5;
  selection_el_5j3b->bJetNum = 3;
  selections.push_back( selection_el_5j3b );

  HistogramMiniTree::Selection *selection_el_5j4b = new HistogramMiniTree::Selection( "sel_el_5j_4b", "1 Electron, = 5 jets, = 4 b-jets" );
  selection_el_5j4b->elNum = 1;
  selection_el_5j4b->muNum = 0;
  selection_el_5j4b->jetNum = 5;
  selection_el_5j4b->bJetNum = 4;
  selection_el_5j4b->bJetEquality = false;
  selections.push_back( selection_el_5j4b );

  HistogramMiniTree::Selection *selection_mu_6j2b = new HistogramMiniTree::Selection( "sel_mu_6j_2b", "1 Muon, = 6 jets, = 2 b-jets" );
  selection_mu_6j2b->elNum = 0;
  selection_mu_6j2b->muNum = 1;
  selection_mu_6j2b->jetNum = 6;
  selection_mu_6j2b->jetEquality = false;
  selection_mu_6j2b->bJetNum = 2;
  selections.push_back( selection_mu_6j2b );

  HistogramMiniTree::Selection *selection_mu_6j3b = new HistogramMiniTree::Selection( "sel_mu_6j_3b", "1 Muon, = 6 jets, = 3 b-jets" );
  selection_mu_6j3b->elNum = 0;
  selection_mu_6j3b->muNum = 1;
  selection_mu_6j3b->jetNum = 6;
  selection_mu_6j3b->jetEquality = false;
  selection_mu_6j3b->bJetNum = 3;
  selections.push_back( selection_mu_6j3b );

  HistogramMiniTree::Selection *selection_mu_6j4b = new HistogramMiniTree::Selection( "sel_mu_6j_4b", "1 Muon, = 6 jets, = 4 b-jets" );
  selection_mu_6j4b->elNum = 0;
  selection_mu_6j4b->muNum = 1;
  selection_mu_6j4b->jetNum = 6;
  selection_mu_6j4b->jetEquality = false;
  selection_mu_6j4b->bJetNum = 4;
  selection_mu_6j4b->bJetEquality = false;
  selections.push_back( selection_mu_6j4b );

  HistogramMiniTree::Selection *selection_el_6j2b = new HistogramMiniTree::Selection( "sel_el_6j_2b", "1 Electron, = 6 jets, = 2 b-jets" );
  selection_el_6j2b->elNum = 1;
  selection_el_6j2b->muNum = 0;
  selection_el_6j2b->jetNum = 6;
  selection_el_6j2b->jetEquality = false;
  selection_el_6j2b->bJetNum = 2;
  selections.push_back( selection_el_6j2b );

  HistogramMiniTree::Selection *selection_el_6j3b = new HistogramMiniTree::Selection( "sel_el_6j_3b", "1 Electron, = 6 jets, = 3 b-jets" );
  selection_el_6j3b->elNum = 1;
  selection_el_6j3b->muNum = 0;
  selection_el_6j3b->jetNum = 6;
  selection_el_6j3b->jetEquality = false;
  selection_el_6j3b->bJetNum = 3;
  selections.push_back( selection_el_6j3b );

  HistogramMiniTree::Selection *selection_el_6j4b = new HistogramMiniTree::Selection( "sel_el_6j_4b", "1 Electron, = 6 jets, = 4 b-jets" );
  selection_el_6j4b->elNum = 1;
  selection_el_6j4b->muNum = 0;
  selection_el_6j4b->jetNum = 6;
  selection_el_6j4b->jetEquality = false;
  selection_el_6j4b->bJetNum = 4;
  selection_el_6j4b->bJetEquality = false;
  selections.push_back( selection_el_6j4b );

  // Save triggers to use
  std::stringstream ss(m_trigger);
  std::string thisTrigger;
  while (std::getline(ss, thisTrigger, ',')) {
    cout << "trigger is " << thisTrigger << endl;
    Char_t tmpTrigger;
    triggers.push_back( tmpTrigger );
    triggerNames.push_back( thisTrigger );
  }

  return EL::StatusCode::SUCCESS;
}


EL::StatusCode HistogramMiniTree :: setupJob (EL::Job& job)
{
  // Here you put code that sets up the job on the submission object
  // so that it is ready to work with your algorithm, e.g. you can
  // request the D3PDReader service or add output files.  Any code you
  // put here could instead also go into the submission script.  The
  // sole advantage of putting it here is that it gets automatically
  // activated/deactivated when you add/remove the algorithm from your
  // job, which may or may not be of value to you.

  return EL::StatusCode::SUCCESS;
}



EL::StatusCode HistogramMiniTree :: histInitialize ()
{
  // Here you do everything that needs to be done at the very
  // beginning on each worker node, e.g. create histograms and output
  // trees.  This method gets called before any input files are
  // connected.
  Info("histInitialize()", "Calling histInitialize \n");
  if ( this->configure() == EL::StatusCode::FAILURE ) {
    Error("initialize()", "Failed to properly configure. Exiting." );
    return EL::StatusCode::FAILURE;
  }


  //if( m_debug)  Info("histInitialize()()", " Defining histograms \n");
  HistogramManager* HM = new HistogramManager("tmpName", "tmpDetail");
  //HistogramManager::HistogramManager* HM = new HistogramManager::HistogramManager("tmpName", "tmpDetail");

  // Basic histograms
  std::string outDir = "";
  numHistElectrons = 1;
  numHistMuons = 1;
  numHistJets = 6;

  // A new TDirectory for each selection
  for(unsigned int iS=0; iS < selections.size(); ++iS){
// !H! Book histograms here

    outDir = selections.at(iS)->name+"/";

    // Electrons //
    h_el_pt_all.push_back( HM->book(outDir, "h_el_pt_all", "Electron P_{T} (GeV)", 50, 0, 300.) );
    h_el_eta_all.push_back( HM->book( outDir,"h_el_eta_all", "Electron #eta", 50, -4., 4.) );
    h_el_phi_all.push_back( HM->book( outDir,"h_el_phi_all", "Electron #phi", 50, -3.14, 3.14) );
    h_el_e_all.push_back( HM->book( outDir,"h_el_e_all", "Electron Energy (GeV)", 50, 0, 300.) );

    vector<TH1F*> vh_el_pt_tmp;
    vector<TH1F*> vh_el_eta_tmp;
    vector<TH1F*> vh_el_phi_tmp;
    vector<TH1F*> vh_el_e_tmp;
    for(unsigned int iE=0; iE < numHistElectrons; ++iE){
      vh_el_pt_tmp.push_back( HM->book( outDir, ("h_el_"+to_string(iE)+"_pt").c_str(),  ("P_{T} of Electron "+to_string(iE+1)+" (GeV)").c_str(), 50, 0, 300.) );
      vh_el_eta_tmp.push_back( HM->book( outDir, ("h_el_"+to_string(iE)+"_eta").c_str(), ("#eta of Electron "+to_string(iE+1)).c_str(), 50, -4, 4) );
      vh_el_phi_tmp.push_back( HM->book( outDir, ("h_el_"+to_string(iE)+"_phi").c_str(), ("#phi of Electron "+to_string(iE+1)).c_str(), 50, -3.14, 3.14) );
      vh_el_e_tmp.push_back( HM->book( outDir, ("h_el_"+to_string(iE)+"_e").c_str(),   ("Energy of Electron "+to_string(iE+1)+" (GeV)").c_str(), 50, 0, 300.) );
    }
    vh_el_pt.push_back( vh_el_pt_tmp );
    vh_el_eta.push_back( vh_el_eta_tmp );
    vh_el_phi.push_back( vh_el_phi_tmp );
    vh_el_e.push_back( vh_el_e_tmp );


    // Muons //
    h_mu_pt_all.push_back( HM->book(outDir, "h_mu_pt_all", "Muon P_{T} (GeV)", 50, 0, 300.) );
    h_mu_eta_all.push_back( HM->book( outDir,"h_mu_eta_all", "Muon #eta", 50, -4., 4.) );
    h_mu_phi_all.push_back( HM->book( outDir,"h_mu_phi_all", "Muon #phi", 50, -3.14, 3.14) );
    h_mu_e_all.push_back( HM->book( outDir,"h_mu_e_all", "Muon Energy (GeV)", 50, 0, 300.) );

    vector<TH1F*> vh_mu_pt_tmp;
    vector<TH1F*> vh_mu_eta_tmp;
    vector<TH1F*> vh_mu_phi_tmp;
    vector<TH1F*> vh_mu_e_tmp;
    for(unsigned int iE=0; iE < numHistMuons; ++iE){
      vh_mu_pt_tmp.push_back( HM->book( outDir, ("h_mu_"+to_string(iE)+"_pt").c_str(),  ("P_{T} of Muon "+to_string(iE+1)+" (GeV)").c_str(), 50, 0, 300.) );
      vh_mu_eta_tmp.push_back( HM->book( outDir, ("h_mu_"+to_string(iE)+"_eta").c_str(), ("#eta of Muon "+to_string(iE+1)).c_str(), 50, -4, 4) );
      vh_mu_phi_tmp.push_back( HM->book( outDir, ("h_mu_"+to_string(iE)+"_phi").c_str(), ("#phi of Muon "+to_string(iE+1)).c_str(), 50, -3.14, 3.14) );
      vh_mu_e_tmp.push_back( HM->book( outDir, ("h_mu_"+to_string(iE)+"_e").c_str(),   ("Energy of Muon "+to_string(iE+1)+" (GeV)").c_str(), 50, 0, 300.) );
    }
    vh_mu_pt.push_back( vh_mu_pt_tmp );
    vh_mu_eta.push_back( vh_mu_eta_tmp );
    vh_mu_phi.push_back( vh_mu_phi_tmp );
    vh_mu_e.push_back( vh_mu_e_tmp );

    // Jets //
    h_jet_n.push_back( HM->book(outDir, "h_jet_n", "Number of Jets", 20, 0, 20.) );
    h_jet_ht.push_back( HM->book(outDir, "h_jet_ht", "H_{T} of All Jets (GeV)", 50, 0, 300.) );
    h_jet_pt_all.push_back( HM->book(outDir, "h_jet_pt_all", "P_{T} of All Jets (GeV)", 50, 0, 300.) );
    h_jet_eta_all.push_back( HM->book( outDir,"h_jet_eta_all", "#eta of All Jets", 50, -4., 4.) );
    h_jet_phi_all.push_back( HM->book( outDir,"h_jet_phi_all", "#phi of All Jets", 50, -3.14, 3.14) );
    h_jet_e_all.push_back( HM->book( outDir,"h_jet_e_all", "Energy of All Jets (GeV)", 50, 0, 300.) );
    h_jet_mv2c20_all.push_back( HM->book(outDir, "h_jet_mv2c20_all", "Mv2c20 of All Jets", 50, -1., 1.) );

    vector<TH1F*> vh_jet_pt_tmp;
    vector<TH1F*> vh_jet_eta_tmp;
    vector<TH1F*> vh_jet_phi_tmp;
    vector<TH1F*> vh_jet_e_tmp;
    vector<TH1F*> vh_jet_mv2c20_tmp;
    for(unsigned int iE=0; iE < numHistJets; ++iE){
      vh_jet_pt_tmp.push_back( HM->book( outDir, ("h_jet_"+to_string(iE)+"_pt").c_str(),  ("P_{T} of Jet "+to_string(iE+1)+" (GeV)").c_str(), 50, 0, 300.) );
      vh_jet_eta_tmp.push_back( HM->book( outDir, ("h_jet_"+to_string(iE)+"_eta").c_str(), ("#eta of Jet "+to_string(iE+1)).c_str(), 50, -4, 4) );
      vh_jet_phi_tmp.push_back( HM->book( outDir, ("h_jet_"+to_string(iE)+"_phi").c_str(), ("#phi of Jet "+to_string(iE+1)).c_str(), 50, -3.14, 3.14) );
      vh_jet_e_tmp.push_back( HM->book( outDir, ("h_jet_"+to_string(iE)+"_e").c_str(),   ("Energy of Jet "+to_string(iE+1)+" (GeV)").c_str(), 50, 0, 300.) );
      vh_jet_mv2c20_tmp.push_back( HM->book( outDir, ("h_jet_"+to_string(iE)+"_mv2c20").c_str(),   ("Mv2c20 of Jet "+to_string(iE+1)).c_str(), 50, -1., 1.) );
    }
    vh_jet_pt.push_back( vh_jet_pt_tmp );
    vh_jet_eta.push_back( vh_jet_eta_tmp );
    vh_jet_phi.push_back( vh_jet_phi_tmp );
    vh_jet_e.push_back( vh_jet_e_tmp );
    vh_jet_mv2c20.push_back( vh_jet_mv2c20_tmp );

    // B-Jets //
    h_bjet_n.push_back( HM->book(outDir, "h_bjet_n", "Number of B-Jets", 20, 0, 20.) );
    h_bjet_ht.push_back( HM->book(outDir, "h_bjet_ht", "H_{T} of All B-Jets (GeV)", 50, 0, 300.) );
    h_bjet_pt_all.push_back( HM->book(outDir, "h_bjet_pt_all", "P_{T} of All B-Jets (GeV)", 50, 0, 300.) );
    h_bjet_eta_all.push_back( HM->book( outDir,"h_bjet_eta_all", "#eta of All B-Jets", 50, -4., 4.) );
    h_bjet_phi_all.push_back( HM->book( outDir,"h_bjet_phi_all", "#phi of All B-Jets", 50, -3.14, 3.14) );
    h_bjet_e_all.push_back( HM->book( outDir,"h_bjet_e_all", "Energy of All B-Jets (GeV)", 50, 0, 300.) );
    h_bjet_mv2c20_all.push_back( HM->book(outDir, "h_bjet_mv2c20_all", "Mv2c20 of All B-Jets", 50, -1., 1.) );

    vector<TH1F*> vh_bjet_pt_tmp;
    vector<TH1F*> vh_bjet_eta_tmp;
    vector<TH1F*> vh_bjet_phi_tmp;
    vector<TH1F*> vh_bjet_e_tmp;
    vector<TH1F*> vh_bjet_mv2c20_tmp;
    for(unsigned int iE=0; iE < numHistJets; ++iE){
      vh_bjet_pt_tmp.push_back( HM->book( outDir, ("h_bjet_"+to_string(iE)+"_pt").c_str(),  ("P_{T} of B-Jet "+to_string(iE+1)+" (GeV)").c_str(), 50, 0, 300.) );
      vh_bjet_eta_tmp.push_back( HM->book( outDir, ("h_bjet_"+to_string(iE)+"_eta").c_str(), ("#eta of B-Jet "+to_string(iE+1)).c_str(), 50, -4, 4) );
      vh_bjet_phi_tmp.push_back( HM->book( outDir, ("h_bjet_"+to_string(iE)+"_phi").c_str(), ("#phi of B-Jet "+to_string(iE+1)).c_str(), 50, -3.14, 3.14) );
      vh_bjet_e_tmp.push_back( HM->book( outDir, ("h_bjet_"+to_string(iE)+"_e").c_str(),   ("Energy of B-Jet "+to_string(iE+1)+" (GeV)").c_str(), 50, 0, 300.) );
      vh_bjet_mv2c20_tmp.push_back( HM->book( outDir, ("h_bjet_"+to_string(iE)+"_mv2c20").c_str(),   ("Mv2c20 of B-Jet "+to_string(iE+1)).c_str(), 50, -1., 1.) );
    }
    vh_bjet_pt.push_back( vh_bjet_pt_tmp );
    vh_bjet_eta.push_back( vh_bjet_eta_tmp );
    vh_bjet_phi.push_back( vh_bjet_phi_tmp );
    vh_bjet_e.push_back( vh_bjet_e_tmp );
    vh_bjet_mv2c20.push_back( vh_bjet_mv2c20_tmp );

    // Others //
    h_met.push_back( HM->book(outDir, "h_met", "MET (GeV)", 50, 0, 300.) );
    h_ht_all.push_back( HM->book(outDir, "h_ht_all", "H_{T} of All Jets + Lepton + MET (GeV)", 50, 0, 300.) );

  }// for each selection

  HM->record( wk() ); //Add all histograms to EventLoop output
  return EL::StatusCode::SUCCESS;
}



EL::StatusCode HistogramMiniTree :: fileExecute ()
{
  // Here you do everything that needs to be done exactly once for every
  // single file, e.g. collect a list of all lumi-blocks processed
  return EL::StatusCode::SUCCESS;
}

// !B! Connect branch variable with tree here
EL::StatusCode HistogramMiniTree :: changeInput (bool firstFile)
{
  // Here you do everything you need to do when we change input files,
  // e.g. resetting branch addresses on trees.  If you are using
  // D3PDReader or a similar service this method is not needed.

//  if( m_debug)  Info("changeInput()", "Loading Cutflows \n");
  TFile* inputFile = wk()->inputFile();
  std::string inputFileName = inputFile->GetName();
  //Remove directory structure if present
  const size_t iLastSlash = inputFileName.find_last_of("\\/");
  if (std::string::npos != iLastSlash)
  {
      inputFileName.erase(0, iLastSlash + 1);
  }
  if (inputFileName.find("data15") != std::string::npos){
    Info("changeInput()","Setting to Data");
    m_isMC = false;
  } else {
    Info("changeInput()","Setting to MC");
    m_isMC = true;

    // Get MC number from string
    std::stringstream ss(inputFileName);
    std::string thisField;
    int fieldCount = 0;
    while (std::getline(ss, thisField, '.')) {
      if (fieldCount == 3){
        m_mcChannelNumber = thisField;
        m_mcChannelNumber.erase(0, m_mcChannelNumber.find_first_not_of('0')); //Remove leading zeros
        break;
      }else{
        fieldCount++;
      }
    } //while get fields

    getLumiWeights(); //retrieve XS+FiltEff weights for MC

    //Get totalEventsWeighted
    /*    TTree* eventNumTree = (TTree*) inputFile->Get("sumWeights");
    float totalEventsWeighted = 0;
    eventNumTree->SetBranchAddress("totalEventsWeighted", &totalEventsWeighted);
    int numTreeEntries = eventNumTree->GetEntries();
    m_totalNumEvents = 0;
    for (int iT = 0; iT < numTreeEntries; ++iT) {
      eventNumTree->GetEntry(iT);
      m_totalNumEvents += totalEventsWeighted;
      }*/

    //TDirectoryFile *dir = dynamic_cast<TDirectoryFile *>(f->Get("ejets"));
    TH1F* cutflow = (TH1F*) inputFile->Get("ejets/cutflow_mc_pu_zvtx");
    m_totalNumEvents = cutflow->GetBinContent(1);
    //cout << "m_totalNumEvents : " << m_totalNumEvents << endl;
    Info("changeInput()", "From sumWeights TTree, found totalNumber of events %s", m_totalNumEvents);
  }// if MC

//  TIter next(inputFile->GetListOfKeys());
//  TKey *key;
//  while ((key = (TKey*)next())) {
//    std::string keyName = key->GetName();
//
//    std::size_t found = keyName.find("cutflow");
//
//    found = keyName.find("weighted");
//    bool foundWeighted = (found!=std::string::npos);
//
//  }//over Keys

  if( m_debug)  Info("changeInput()", "Loading Branches \n");
  TTree *tree = wk()->tree();
  tree->SetBranchStatus ("*", 0);


  tree->SetBranchStatus("ejets", 1);   tree->SetBranchAddress( "ejets", &ejets);
  tree->SetBranchStatus("mujets", 1);   tree->SetBranchAddress( "mujets", &mujets);

  if(m_isMC){
    tree->SetBranchStatus("weight_mc", 1);        tree->SetBranchAddress( "weight_mc", &weight_mc );
    tree->SetBranchStatus("weight_pileup", 1);     tree->SetBranchAddress( "weight_pileup", &weight_pileup);
    tree->SetBranchStatus("weight_bTagSF_77", 1);     tree->SetBranchAddress( "weight_bTagSF_77", &weight_bTagSF);
    tree->SetBranchStatus("weight_leptonSF", 1);   tree->SetBranchAddress( "weight_leptonSF", &weight_leptonSF);
  }

  tree->SetBranchStatus("el_pt", 1);   tree->SetBranchAddress( "el_pt", &el_pt);
  tree->SetBranchStatus("el_eta", 1);  tree->SetBranchAddress( "el_eta", &el_eta);
  tree->SetBranchStatus("el_phi", 1);  tree->SetBranchAddress( "el_phi", &el_phi);
  tree->SetBranchStatus("el_e", 1);    tree->SetBranchAddress( "el_e", &el_e);
  tree->SetBranchStatus("el_charge", 1);        tree->SetBranchAddress( "el_charge", &el_charge);
  tree->SetBranchStatus("el_topoetcone20", 1);  tree->SetBranchAddress( "el_topoetcone20", &el_topoetcone20);
  tree->SetBranchStatus("el_ptvarcone20", 1);   tree->SetBranchAddress( "el_ptvarcone20", &el_ptvarcone20);

  tree->SetBranchStatus("mu_pt", 1);             tree->SetBranchAddress( "mu_pt", &mu_pt );
  tree->SetBranchStatus("mu_eta", 1);           tree->SetBranchAddress( "mu_eta" , &mu_eta);
  tree->SetBranchStatus("mu_phi", 1);           tree->SetBranchAddress( "mu_phi" , &mu_phi);
  tree->SetBranchStatus("mu_e", 1);             tree->SetBranchAddress( "mu_e" , &mu_e);
  tree->SetBranchStatus("mu_charge", 1);         tree->SetBranchAddress( "mu_charge", &mu_charge);
  tree->SetBranchStatus("mu_topoetcone20", 1);   tree->SetBranchAddress( "mu_topoetcone20", &mu_topoetcone20);
  tree->SetBranchStatus("mu_ptvarcone30", 1);   tree->SetBranchAddress( "mu_ptvarcone30" , &mu_ptvarcone30);

  tree->SetBranchStatus("jet_pt", 1);           tree->SetBranchAddress( "jet_pt" , &jet_pt);
  tree->SetBranchStatus("jet_eta", 1);           tree->SetBranchAddress( "jet_eta", &jet_eta);
  tree->SetBranchStatus("jet_phi", 1);           tree->SetBranchAddress( "jet_phi", &jet_phi);
  tree->SetBranchStatus("jet_e", 1);             tree->SetBranchAddress( "jet_e" , &jet_e );
  tree->SetBranchStatus("jet_mv1", 1);           tree->SetBranchAddress( "jet_mv1", &jet_mv1);
  tree->SetBranchStatus("jet_mvb", 1);           tree->SetBranchAddress( "jet_mvb", &jet_mvb);
  tree->SetBranchStatus("jet_mv1c", 1);         tree->SetBranchAddress( "jet_mv1c" , &jet_mv1c);
  tree->SetBranchStatus("jet_mv2c00", 1);       tree->SetBranchAddress( "jet_mv2c00" , &jet_mv2c00);
  tree->SetBranchStatus("jet_mv2c10", 1);       tree->SetBranchAddress( "jet_mv2c10" , &jet_mv2c10);
  tree->SetBranchStatus("jet_mv2c20", 1);       tree->SetBranchAddress( "jet_mv2c20" , &jet_mv2c20);
  tree->SetBranchStatus("jet_ip3dsv1", 1);       tree->SetBranchAddress( "jet_ip3dsv1", &jet_ip3dsv1);
  tree->SetBranchStatus("jet_jvt", 1);           tree->SetBranchAddress( "jet_jvt", &jet_jvt);

  tree->SetBranchStatus("met_met", 1);           tree->SetBranchAddress( "met_met", &met_met);
  tree->SetBranchStatus("met_phi", 1);           tree->SetBranchAddress( "met_phi", &met_phi);

  for( unsigned int iT=0; iT < triggers.size(); ++iT){
    tree->SetBranchStatus( triggerNames.at(iT).c_str(), 1);
    tree->SetBranchAddress( triggerNames.at(iT).c_str(), &triggers.at(iT) );
  }

  return EL::StatusCode::SUCCESS;
}



EL::StatusCode HistogramMiniTree :: initialize ()
{
  // Here you do everything that you need to do after the first input
  // file has been connected and before the first event is processed,
  // e.g. create additional histograms based on which variables are
  // available in the input files.  You can also create all of your
  // histograms and trees in here, but be aware that this method
  // doesn't get called if no events are processed.  So any objects
  // you create here won't be available in the output if you have no
  // input events.
  m_eventCounter = -1;




  Info("initialize()", "Succesfully initialized! \n");
  return EL::StatusCode::SUCCESS;
}


EL::StatusCode HistogramMiniTree :: execute ()
{
  // Here you do everything that needs to be done on every single
  // event, e.g. read input variables, apply cuts, and fill
  // histograms and trees.  This is where most of your actual analysis
  // code will go.
  //if(m_debug) Info("execute()", "Processing Event");
  ++m_eventCounter;

  if( (m_eventCounter%1000) == 0) Info("execute()", "Event number %i", m_eventCounter);

  //weight_mc = weight_pileup = weight_leptonSF = weight_bTagSF = 1.; //Set ahead of time for data
  wk()->tree()->GetEntry (wk()->treeEntry());


  if( m_debug)  Info("execute()", "Starting execute() \n");
  bool passedTriggers = false;
  //If no triggers selected, then let all pass
  if (triggers.size() == 0)
    passedTriggers = true;

  //otherwise check all triggers
  for(unsigned int iT=0; iT < triggers.size(); ++iT){
    if( triggers.at(iT) )
      passedTriggers = true;
  }

  // If no trigger passed, skip event
//!!  if( passedTriggers == false ){
//!!    return EL::StatusCode::SUCCESS;
//!!  }

  float eventWeight = 1.;
  if(m_isMC)
    //cout << "weight_pileup : " << weight_pileup << endl;   
    //eventWeight = weight_mc*weight_pileup*weight_leptonSF*m_XSWeight/m_totalNumEvents;
  //cout << "Weights: \n mc: " << weight_mc << "\n pileup " << weight_pileup << " \n leptonSF " << weight_leptonSF << "\n XS " << m_XSWeight << " \n " << m_totalNumEvents << endl;
    eventWeight *= weight_mc*weight_pileup*weight_leptonSF*weight_bTagSF*m_XSWeight/m_totalNumEvents;
  // Start different selections
  for(unsigned int iS=0; iS < selections.size(); ++iS){

    if( m_debug)  Info("execute()", "Starting selection %s \n", selections.at(iS)->name.c_str() );
    //selections
    if (selections.at(iS)->jetNum != -1){ //jet Selection is set
       if( selections.at(iS)->jetEquality && jet_pt->size() != selections.at(iS)->jetNum)
        continue;
       else if( (!selections.at(iS)->jetEquality) && jet_pt->size() < selections.at(iS)->jetNum)
        continue;
    }

    // Get selections from Preselection //
    if (selections.at(iS)->elNum == 1 && ejets != 1)
      continue;
    if (selections.at(iS)->muNum == 1 && mujets != 1)
      continue;

//!!    if (selections.at(iS)->elNum != -1 && el_pt->size() != selections.at(iS)->elNum)
//!!      continue;
//!!    if (selections.at(iS)->muNum != -1 && mu_pt->size() != selections.at(iS)->muNum)
//!!      continue;

    vector<int> BJetIndicies;
    for(unsigned int iJet=0; iJet < jet_mv2c20->size(); ++iJet){
      if( jet_mv2c20->at(iJet) > m_bTagWP )
        BJetIndicies.push_back(iJet);
    }

    if (selections.at(iS)->bJetNum != -1){
      if( selections.at(iS)->bJetEquality &&  BJetIndicies.size() != selections.at(iS)->bJetNum)
        continue;
      if( (!selections.at(iS)->bJetEquality) &&  BJetIndicies.size() < selections.at(iS)->bJetNum)
        continue;
    }
    
    // Histogram Filling //
    if( m_debug)  Info("execute()", "Starting Histogram filling \n");
    float lepton_sumPt = 0.0;

    //electrons
    for(unsigned int iE=0; iE < el_pt->size(); ++iE){
      h_el_pt_all.at(iS)->Fill( el_pt->at(iE)/1e3, eventWeight );
      h_el_eta_all.at(iS)->Fill( el_eta->at(iE), eventWeight );
      h_el_phi_all.at(iS)->Fill( el_phi->at(iE), eventWeight );
      h_el_e_all.at(iS)->Fill( el_e->at(iE)/1e3, eventWeight );

      lepton_sumPt += el_pt->at(iE)/1e3;

      if( iE < numHistElectrons){
        vh_el_pt.at(iS).at(iE)->Fill( el_pt->at(iE)/1e3, eventWeight );
        vh_el_eta.at(iS).at(iE)->Fill( el_eta->at(iE), eventWeight );
        vh_el_phi.at(iS).at(iE)->Fill( el_phi->at(iE), eventWeight );
        vh_el_e.at(iS).at(iE)->Fill( el_e->at(iE)/1e3, eventWeight );
      }
    }//end electrons

    //muons
    for(unsigned int iM=0; iM < mu_pt->size(); ++iM){
      h_mu_pt_all.at(iS)->Fill( mu_pt->at(iM)/1e3, eventWeight );
      h_mu_eta_all.at(iS)->Fill( mu_eta->at(iM), eventWeight );
      h_mu_phi_all.at(iS)->Fill( mu_phi->at(iM), eventWeight );
      h_mu_e_all.at(iS)->Fill( mu_e->at(iM)/1e3, eventWeight );

      lepton_sumPt += mu_pt->at(iM)/1e3;

      if( iM < numHistMuons){
        vh_mu_pt.at(iS).at(iM)->Fill( mu_pt->at(iM)/1e3, eventWeight );
        vh_mu_eta.at(iS).at(iM)->Fill( mu_eta->at(iM), eventWeight );
        vh_mu_phi.at(iS).at(iM)->Fill( mu_phi->at(iM), eventWeight );
        vh_mu_e.at(iS).at(iM)->Fill( mu_e->at(iM)/1e3, eventWeight );
      }
    }//end muons

    //jets
    float ht_hadronic = 0.0;

    h_jet_n.at(iS)->Fill( jet_pt->size(), eventWeight );
    for(unsigned int iJ=0; iJ < jet_pt->size(); ++iJ){
      ht_hadronic += jet_pt->at(iJ)/1e3;

      h_jet_pt_all.at(iS)->Fill( jet_pt->at(iJ)/1e3, eventWeight );
      h_jet_eta_all.at(iS)->Fill( jet_eta->at(iJ), eventWeight );
      h_jet_phi_all.at(iS)->Fill( jet_phi->at(iJ), eventWeight );
      h_jet_e_all.at(iS)->Fill( jet_e->at(iJ)/1e3, eventWeight );
      h_jet_mv2c20_all.at(iS)->Fill( jet_mv2c20->at(iJ), eventWeight );

      if( iJ < numHistJets){
        vh_jet_pt.at(iS).at(iJ)->Fill( jet_pt->at(iJ)/1e3, eventWeight );
        vh_jet_eta.at(iS).at(iJ)->Fill( jet_eta->at(iJ), eventWeight );
        vh_jet_phi.at(iS).at(iJ)->Fill( jet_phi->at(iJ), eventWeight );
        vh_jet_e.at(iS).at(iJ)->Fill( jet_e->at(iJ)/1e3, eventWeight );
        vh_jet_mv2c20.at(iS).at(iJ)->Fill( jet_mv2c20->at(iJ), eventWeight );
      }
    }//end jets
    h_jet_ht.at(iS)->Fill( ht_hadronic, eventWeight );

    float ht_hadronic_bjet = 0.0;
    //b-jets
    h_bjet_n.at(iS)->Fill( BJetIndicies.size(), eventWeight );
    for(unsigned int iB=0; iB < BJetIndicies.size(); ++iB){
      unsigned int iJ = BJetIndicies.at(iB);

      ht_hadronic_bjet += jet_pt->at(iJ)/1e3;

      h_bjet_pt_all.at(iS)->Fill( jet_pt->at(iJ)/1e3, eventWeight );
      h_bjet_eta_all.at(iS)->Fill( jet_eta->at(iJ), eventWeight );
      h_bjet_phi_all.at(iS)->Fill( jet_phi->at(iJ), eventWeight );
      h_bjet_e_all.at(iS)->Fill( jet_e->at(iJ)/1e3, eventWeight );
      h_bjet_mv2c20_all.at(iS)->Fill( jet_mv2c20->at(iJ), eventWeight );

      if( iJ < numHistJets){
        vh_bjet_pt.at(iS).at(iJ)->Fill( jet_pt->at(iJ)/1e3, eventWeight );
        vh_bjet_eta.at(iS).at(iJ)->Fill( jet_eta->at(iJ), eventWeight );
        vh_bjet_phi.at(iS).at(iJ)->Fill( jet_phi->at(iJ), eventWeight );
        vh_bjet_e.at(iS).at(iJ)->Fill( jet_e->at(iJ)/1e3, eventWeight );
        vh_bjet_mv2c20.at(iS).at(iJ)->Fill( jet_mv2c20->at(iJ), eventWeight );
      }
    }//end b-jets
    h_bjet_ht.at(iS)->Fill( ht_hadronic_bjet, eventWeight );

    //others
    if( m_debug)  Info("execute()", "Starting other histograms \n");
    h_met.at(iS)->Fill( met_met/1e3 , eventWeight );
    h_ht_all.at(iS)->Fill( ht_hadronic + lepton_sumPt + met_met/1e3, eventWeight );

    // mtw ?!


  } //selections

  return EL::StatusCode::SUCCESS;
}


EL::StatusCode HistogramMiniTree :: postExecute ()
{
  // Here you do everything that needs to be done after the main event
  // processing.  This is typically very rare, particularly in user
  // code.  It is mainly used in implementing the NTupleSvc.
  return EL::StatusCode::SUCCESS;
}



EL::StatusCode HistogramMiniTree :: finalize ()
{
  // This method is the mirror image of initialize(), meaning it gets
  // called after the last event has been processed on the worker node
  // and allows you to finish up any objects you created in
  // initialize() before they are written to disk.  This is actually
  // fairly rare, since this happens separately for each worker node.
  // Most of the time you want to do your post-processing on the
  // submission node after all your histogram outputs have been
  // merged.  This is different from histFinalize() in that it only
  // gets called on worker nodes that processed input events.

  return EL::StatusCode::SUCCESS;
}



EL::StatusCode HistogramMiniTree :: histFinalize ()
{
  // This method is the mirror image of histInitialize(), meaning it
  // gets called after the last event has been processed on the worker
  // node and allows you to finish up any objects you created in
  // histInitialize() before they are written to disk.  This is
  // actually fairly rare, since this happens separately for each
  // worker node.  Most of the time you want to do your
  // post-processing on the submission node after all your histogram
  // outputs have been merged.  This is different from finalize() in
  // that it gets called on all worker nodes regardless of whether
  // they processed input events.
  return EL::StatusCode::SUCCESS;
}

//This grabs cross section and acceptance from XS_Samples.txt
EL::StatusCode HistogramMiniTree :: getLumiWeights() {

  m_XSWeight = 1.;
  if(!m_isMC){
    return EL::StatusCode::SUCCESS;
  }

  ifstream fileIn(  gSystem->ExpandPathName("$ROOTCOREBIN/data/ttHHistogrammer/XS_Samples.txt") );
  std::string line;
  std::string subStr;


  bool foundFile = false;
  float thisXS;
  float thisFiltEff;
  while (getline(fileIn, line)){
    istringstream iss(line);
    iss >> subStr;
    if (subStr.find(m_mcChannelNumber) != string::npos){
      foundFile = true;
      iss >> subStr;
      sscanf(subStr.c_str(), "%e", &thisXS);
      iss >> subStr;
      sscanf(subStr.c_str(), "%e", &thisFiltEff);
      cout << "Setting xs / acceptance " << thisXS << ":" << thisFiltEff << endl;
      m_XSWeight = thisXS*thisFiltEff;
      continue;
    }
  }
  if( !foundFile ){
    cerr << "ERROR: Could not find proper file information for file number " << m_mcChannelNumber << endl;
    return EL::StatusCode::FAILURE;
  }
  return EL::StatusCode::SUCCESS;
}

