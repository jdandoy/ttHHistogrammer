//////////////////////////////////////////////////////////////////
// HistogramMiniTree.h                                               //
//////////////////////////////////////////////////////////////////
// Fairly generic EventLoop for creating histograms from TTrees //
// Currently optimized for the ttH TTree output                 //
//////////////////////////////////////////////////////////////////
// Jeff.Dandoy@cern.ch , Nedaa.Asbah@cern.ch                    //
//////////////////////////////////////////////////////////////////

#ifndef ttHHistogrammer_HistogramMiniTree_H
#define ttHHistogrammer_HistogramMiniTree_H

#include <EventLoop/StatusCode.h>
#include <EventLoop/Algorithm.h>
#include <EventLoop/Worker.h>

// rootcore includes
#include "GoodRunsLists/GoodRunsListSelectionTool.h"

//algorithm wrapper
#include "xAODAnaHelpers/Algorithm.h"
#include "xAODAnaHelpers/HistogramManager.h"

// ROOT include(s):
#include "TH1D.h"
#include "TH2D.h"
#include "TProfile.h"
#include "TLorentzVector.h"

#include <sstream>
#include <vector>

using namespace std;



class HistogramMiniTree : public xAH::Algorithm
{
  // put your configuration variables here as public variables.
  // that way they can be set directly from CINT and python.
  public:

    // float cutValue;
    int m_eventCounter;     //!

    std::string m_name;
    float m_mcEventWeight;  //!

    struct Selection{
      string name;
      string displayName;
      unsigned int jetNum;
      unsigned int bJetNum;
      unsigned int elNum;
      unsigned int muNum;

      Selection(std::string thisName, std::string thisDisplayName = ""){
        name = thisName;
        displayName = thisDisplayName;
        jetNum = 0;
        bJetNum = 0;
        elNum = 0;
        muNum = 0;
      }
    };

  private:


    bool m_isMC; //!
    std::string m_mcChannelNumber; //!
    float m_XSWeight; //!
    float m_totalNumEvents; //!

    // Config file options //
    float m_bTagWP;
    std::string m_trigger;




    // Histograms //
// !H! Define histogram containers here

    // Electrons //
    unsigned int numHistElectrons; //!
    vector<TH1F*> h_el_pt_all; //!
    vector<TH1F*> h_el_eta_all; //!
    vector<TH1F*> h_el_phi_all; //!
    vector<TH1F*> h_el_e_all; //!
    vector< vector<TH1F*> > vh_el_pt; //!
    vector< vector<TH1F*> > vh_el_eta; //!
    vector< vector<TH1F*> > vh_el_phi; //!
    vector< vector<TH1F*> > vh_el_e; //!

    // Muons //
    unsigned int numHistMuons; //!
    vector<TH1F*> h_mu_pt_all; //!
    vector<TH1F*> h_mu_eta_all; //!
    vector<TH1F*> h_mu_phi_all; //!
    vector<TH1F*> h_mu_e_all; //!
    vector< vector<TH1F*> > vh_mu_pt; //!
    vector< vector<TH1F*> > vh_mu_eta; //!
    vector< vector<TH1F*> > vh_mu_phi; //!
    vector< vector<TH1F*> > vh_mu_e; //!

    // Jets //
    unsigned int numHistJets; //!
    vector<TH1F*> h_jet_n; //!
    vector<TH1F*> h_jet_ht; //!
    vector<TH1F*> h_jet_pt_all; //!
    vector<TH1F*> h_jet_eta_all; //!
    vector<TH1F*> h_jet_phi_all; //!
    vector<TH1F*> h_jet_e_all; //!
    vector<TH1F*> h_jet_mv2c20_all; //!
    vector< vector<TH1F*> > vh_jet_pt; //!
    vector< vector<TH1F*> > vh_jet_eta; //!
    vector< vector<TH1F*> > vh_jet_phi; //!
    vector< vector<TH1F*> > vh_jet_e; //!
    vector< vector<TH1F*> > vh_jet_mv2c20; //!

    // B-Jets //
    vector<TH1F*> h_bjet_n; //!
    vector<TH1F*> h_bjet_ht; //!
    vector<TH1F*> h_bjet_pt_all; //!
    vector<TH1F*> h_bjet_eta_all; //!
    vector<TH1F*> h_bjet_phi_all; //!
    vector<TH1F*> h_bjet_e_all; //!
    vector<TH1F*> h_bjet_mv2c20_all; //!
    vector< vector<TH1F*> > vh_bjet_pt; //!
    vector< vector<TH1F*> > vh_bjet_eta; //!
    vector< vector<TH1F*> > vh_bjet_phi; //!
    vector< vector<TH1F*> > vh_bjet_e; //!
    vector< vector<TH1F*> > vh_bjet_mv2c20; //!


    // Others //
    vector<TH1F*> h_met; //!
    vector<TH1F*> h_ht_all; //!


    vector< Selection* > selections;


    // Branches //
// !B! Define branch variable here
    vector<std::string> triggerNames; //!
    vector<Char_t> triggers; //!
//    Char_t *HLT_mu50; //!

    float met_met; //!
    float met_phi; //!
    float weight_mc; //!
    float weight_pileup; //!
    float weight_bTagSF; //!
    float weight_leptonSF; //!

    vector<float> *el_pt; //!
    vector<float> *el_eta; //!
    vector<float> *el_phi; //!
    vector<float> *el_e; //!
    vector<float> *el_charge; //!
    vector<float> *el_topoetcone20; //!
    vector<float> *el_ptvarcone20; //!
    vector<float> *mu_pt; //!
    vector<float> *mu_eta; //!
    vector<float> *mu_phi; //!
    vector<float> *mu_e; //!
    vector<float> *mu_charge; //!
    vector<float> *mu_topoetcone20; //!
    vector<float> *mu_ptvarcone30; //!
    vector<float> *jet_pt; //!
    vector<float> *jet_eta; //!
    vector<float> *jet_phi; //!
    vector<float> *jet_e; //!
    vector<float> *jet_mv1; //!
    vector<float> *jet_mvb; //!
    vector<float> *jet_mv1c; //!
    vector<float> *jet_mv2c00; //!
    vector<float> *jet_mv2c10; //!
    vector<float> *jet_mv2c20; //!
    vector<float> *jet_ip3dsv1; //!
    vector<float> *jet_jvt; //!

  // variables that don't get filled at submission time should be
  // protected from being send from the submission node to the worker
  // node (done by the //!)
public:
  // Tree *myTree; //!
  // TH1 *myHist; //!

  EL::StatusCode getLumiWeights();

  // this is a standard constructor
  HistogramMiniTree ();

  // these are the functions inherited from Algorithm
  virtual EL::StatusCode setupJob (EL::Job& job);
  virtual EL::StatusCode fileExecute ();
  virtual EL::StatusCode histInitialize ();
  virtual EL::StatusCode changeInput (bool firstFile);
  virtual EL::StatusCode initialize ();
  virtual EL::StatusCode execute ();
  virtual EL::StatusCode postExecute ();
  virtual EL::StatusCode finalize ();
  virtual EL::StatusCode histFinalize ();

  // these are the functions not inherited from Algorithm
  virtual EL::StatusCode configure ();

  // this is needed to distribute the algorithm to the workers
  ClassDef(HistogramMiniTree, 1);
};

#endif
