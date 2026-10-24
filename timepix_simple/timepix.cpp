// Timepix-like silicon pixel detector: 256x256 pixels of 55 um, 400 um thick.
#include <G4RunManagerFactory.hh>
#include <G4UImanager.hh>
#include <G4UIExecutive.hh>
#include <G4VisExecutive.hh>
#include <G4VUserDetectorConstruction.hh>
#include <G4VUserActionInitialization.hh>
#include <G4VUserPrimaryGeneratorAction.hh>
#include <G4UserRunAction.hh>
#include <G4VSensitiveDetector.hh>
#include <G4SDManager.hh>
#include <FTFP_BERT.hh>
#include <G4EmStandardPhysics_option4.hh>
#include <G4NistManager.hh>
#include <G4Box.hh>
#include <G4LogicalVolume.hh>
#include <G4PVPlacement.hh>
#include <G4PVReplica.hh>
#include <G4VisAttributes.hh>
#include <G4Colour.hh>
#include <G4ParticleGun.hh>
#include <G4ParticleTable.hh>
#include <G4Event.hh>
#include <G4Step.hh>
#include <G4TouchableHistory.hh>
#include <G4AnalysisManager.hh>
#include <G4SystemOfUnits.hh>
#include <G4PhysicalConstants.hh>
#include <Randomize.hh>
#include <G4GenericMessenger.hh>

#include <map>
#include <utility>

namespace {
constexpr G4int kNPix = 256;
constexpr G4double kPitch = 55. * um;
constexpr G4double kThick = 400. * um;
constexpr G4double kPairEnergy = 3.6 * eV;  // e-h pair creation energy in Si
}

// ---------------------------------------------------------------- sensitive detector
class PixelSD : public G4VSensitiveDetector {
public:
  explicit PixelSD(const G4String& name) : G4VSensitiveDetector(name) {}

  void Initialize(G4HCofThisEvent*) override { fEdep.clear(); }

  G4bool ProcessHits(G4Step* step, G4TouchableHistory*) override {
    const G4double edep = step->GetTotalEnergyDeposit();
    if (edep <= 0.) return false;
    const auto* touch = step->GetPreStepPoint()->GetTouchable();
    // depth 0: pixel replica along y, depth 1: strip replica along x
    const G4int j = touch->GetCopyNumber(0);
    const G4int i = touch->GetCopyNumber(1);
    fEdep[{i, j}] += edep;
    return true;
  }

  void EndOfEvent(G4HCofThisEvent*) override {
    if (fEdep.empty()) return;
    auto* am = G4AnalysisManager::Instance();
    for (const auto& [ij, edep] : fEdep) {
      am->FillNtupleIColumn(0, ij.first);
      am->FillNtupleIColumn(1, ij.second);
      am->FillNtupleDColumn(2, edep / kPairEnergy);  // charge in units of e
      am->FillNtupleDColumn(3, edep / keV);
      am->AddNtupleRow(0);
    }
  }

private:
  std::map<std::pair<G4int, G4int>, G4double> fEdep;
};

// ---------------------------------------------------------------- geometry
class DetectorConstruction : public G4VUserDetectorConstruction {
public:
  G4VPhysicalVolume* Construct() override {
    auto* nist = G4NistManager::Instance();
    auto* vacuum = nist->FindOrBuildMaterial("G4_Galactic");
    auto* silicon = nist->FindOrBuildMaterial("G4_Si");

    const G4double size = kNPix * kPitch;  // 14.08 mm

    auto* worldS = new G4Box("World", 100. * mm, 100. * mm, 100. * mm);
    auto* worldLV = new G4LogicalVolume(worldS, vacuum, "World");
    auto* worldPV = new G4PVPlacement(nullptr, {}, worldLV, "World", nullptr, false, 0, true);
    worldLV->SetVisAttributes(G4VisAttributes::GetInvisible());

    auto* sensorS = new G4Box("Sensor", size / 2, size / 2, kThick / 2);
    auto* sensorLV = new G4LogicalVolume(sensorS, silicon, "Sensor");
    new G4PVPlacement(nullptr, {}, sensorLV, "Sensor", worldLV, false, 0, true);

    // Strip along y, replicated along x
    auto* stripS = new G4Box("Strip", kPitch / 2, size / 2, kThick / 2);
    auto* stripLV = new G4LogicalVolume(stripS, silicon, "Strip");
    new G4PVReplica("Strip", stripLV, sensorLV, kXAxis, kNPix, kPitch);

    // Pixel replicated along y inside the strip
    auto* pixelS = new G4Box("Pixel", kPitch / 2, kPitch / 2, kThick / 2);
    fPixelLV = new G4LogicalVolume(pixelS, silicon, "Pixel");
    new G4PVReplica("Pixel", fPixelLV, stripLV, kYAxis, kNPix, kPitch);

    // Drawing 65536 pixels is too heavy; only the sensor box is shown
    auto* va = new G4VisAttributes(G4Colour(0.2, 0.4, 0.9, 0.4));
    va->SetForceSolid(true);
    sensorLV->SetVisAttributes(va);
    stripLV->SetVisAttributes(G4VisAttributes::GetInvisible());
    fPixelLV->SetVisAttributes(G4VisAttributes::GetInvisible());

    return worldPV;
  }

  void ConstructSDandField() override {
    auto* sd = new PixelSD("PixelSD");
    G4SDManager::GetSDMpointer()->AddNewDetector(sd);
    SetSensitiveDetector(fPixelLV, sd);
  }

private:
  G4LogicalVolume* fPixelLV = nullptr;
};

// ---------------------------------------------------------------- primary generator
class PrimaryGenerator : public G4VUserPrimaryGeneratorAction {
public:
  PrimaryGenerator() : fGun(new G4ParticleGun(1)) {
    fGun->SetParticleDefinition(G4ParticleTable::GetParticleTable()->FindParticle("e-"));
    fMessenger = new G4GenericMessenger(this, "/source/", "Square parallel electron source");
    fMessenger->DeclarePropertyWithUnit("energy", "keV", fEnergy, "Kinetic energy");
    fMessenger->DeclarePropertyWithUnit("angle", "deg", fAngle,
                                        "Angle between beam and surface normal (tilt in x-z)");
    fMessenger->DeclarePropertyWithUnit("size", "mm", fSize, "Square source edge");
    fMessenger->DeclarePropertyWithUnit("distance", "mm", fDistance,
                                        "Source plane distance above the sensor surface");
  }
  ~PrimaryGenerator() override {
    delete fMessenger;
    delete fGun;
  }

  // Uniform square source perpendicular to the beam; its axis passes through the sensor-surface centre.
  void GeneratePrimaries(G4Event* event) override {
    const G4double a = (G4UniformRand() - 0.5) * fSize;
    const G4double b = (G4UniformRand() - 0.5) * fSize;
    const G4ThreeVector dir(std::sin(fAngle), 0., std::cos(fAngle));
    const G4ThreeVector u(std::cos(fAngle), 0., -std::sin(fAngle));
    const G4ThreeVector v(0., 1., 0.);
    const G4ThreeVector centre = G4ThreeVector(0., 0., -kThick / 2) - fDistance * dir;
    fGun->SetParticleEnergy(fEnergy);
    fGun->SetParticleMomentumDirection(dir);
    fGun->SetParticlePosition(centre + a * u + b * v);
    fGun->GeneratePrimaryVertex(event);
  }

private:
  G4ParticleGun* fGun;
  G4GenericMessenger* fMessenger = nullptr;
  G4double fEnergy = 20. * keV;
  G4double fAngle = 30. * deg;
  G4double fSize = 40. * mm;
  G4double fDistance = 1. * mm;
};

// ---------------------------------------------------------------- run action
class RunAction : public G4UserRunAction {
public:
  RunAction() {
    auto* am = G4AnalysisManager::Instance();
    am->SetVerboseLevel(1);
    am->SetNtupleMerging(true);
    am->CreateNtuple("pixels", "Pixels with signal");
    am->CreateNtupleIColumn("i");       // 0
    am->CreateNtupleIColumn("j");       // 1
    am->CreateNtupleDColumn("charge");  // 2, electrons
    am->CreateNtupleDColumn("edep");    // 3, keV
    am->FinishNtuple();
  }

  void BeginOfRunAction(const G4Run*) override {
    G4AnalysisManager::Instance()->OpenFile("timepix.root");
  }

  void EndOfRunAction(const G4Run*) override {
    auto* am = G4AnalysisManager::Instance();
    am->Write();
    am->CloseFile();
  }
};

class ActionInitialization : public G4VUserActionInitialization {
public:
  void BuildForMaster() const override { SetUserAction(new RunAction); }
  void Build() const override {
    SetUserAction(new PrimaryGenerator);
    SetUserAction(new RunAction);
  }
};

// ---------------------------------------------------------------- main
int main(int argc, char** argv) {
  G4String macro = "run.mac";
  G4bool interactive = (argc == 1);
  for (int k = 1; k < argc; ++k) {
    if (G4String(argv[k]) == "-i") interactive = true;
    else macro = argv[k];
  }
  G4UIExecutive* ui = interactive ? new G4UIExecutive(1, argv) : nullptr;

  auto* runManager = G4RunManagerFactory::CreateRunManager(G4RunManagerType::Default);
  runManager->SetUserInitialization(new DetectorConstruction);
  auto* physics = new FTFP_BERT;
  physics->ReplacePhysics(new G4EmStandardPhysics_option4);
  runManager->SetUserInitialization(physics);
  runManager->SetUserInitialization(new ActionInitialization);

  auto* vis = new G4VisExecutive;
  vis->Initialize();

  auto* uiManager = G4UImanager::GetUIpointer();
  uiManager->ApplyCommand("/control/execute " + macro);
  if (ui) {
    ui->SessionStart();
    delete ui;
  }

  delete vis;
  delete runManager;
  return 0;
}
