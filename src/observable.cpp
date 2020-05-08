#include "observable.h"
#include "propagator.h"
#include "utility/abort.h"
#include "utility/fmt/format.h"
#include "utility/fmt/printf.h"
#include "utility/utility.h"
#include <cmath>
#include <iostream>

using namespace std;
using namespace obs;

extern parameter Para;
extern variable Var;

oneBodyObs::oneBodyObs() {
  Normalization = 1.0e-10;

  if (DiagType == POLAR) {
    PhyWeight = Para.ExtMomBinSize * Para.TauBinSize;
    Name = "polar";
  } else if (DiagType == SIGMA) {
    PhyWeight = Para.ExtMomBinSize * Para.TauBinSize;
    // PhyWeight = ExtMomBinSize / Para.Beta;
    Name = "sigma";
  } else if (DiagType == DELTA) {
    PhyWeight = Para.ExtMomBinSize * Para.TauBinSize;
    // PhyWeight = ExtMomBinSize;
    Name = "delta";
  } else
    return;

  _Estimator.Initialize({Para.Order + 1, Para.ExtMomBinSize, Para.TauBinSize});
}

void oneBodyObs::Measure0(double Factor) { Normalization += 1.0 * Factor; }
void oneBodyObs::Measure(int Order, int KBin, int TauBin, double Weight,
                         double Factor) {
  ASSERT(KBin >= 0 && KBin < Para.ExtMomBinSize, "Kidx is out of range!");
  ASSERT(TauBin >= 0 && TauBin < Para.TauBinSize, "TauIdx is out of range!");

  _Estimator(Order, KBin, TauBin) += Weight * Factor;
  _Estimator(0, KBin, TauBin) += Weight * Factor;
}

void oneBodyObs::Save() {

  string FileName = fmt::format("{0}_pid{1}.dat", Name, Para.PID);
  ofstream VerFile;
  VerFile.open(FileName, ios::out | ios::trunc);

  if (VerFile.is_open()) {

    VerFile << "# Counter: " << Var.Counter << endl;
    VerFile << "# Norm: " << Normalization << endl;
    for (int order = 0; order <= Para.Order; order++)
      for (int qindex = 0; qindex < Para.ExtMomBinSize; ++qindex)
        for (int tindex = 0; tindex < Para.TauBinSize; ++tindex)
          VerFile << _Estimator(order, qindex, tindex) * PhyWeight << "  ";
    VerFile.close();
  } else {
    LOG_WARNING(Name << " for PID " << Para.PID << " fails to save!");
  }
}

ver4Obs::ver4Obs() {
  Normalization = 1.0e-10;
  PhyWeight = Para.AngBinSize;
  for (auto &estimator : _Estimator)
    estimator.Initialize({Para.Order + 1, Para.AngBinSize, Para.ExtMomBinSize});
};

void ver4Obs::Measure0(double Factor) { Normalization += 1.0 * Factor; }

void ver4Obs::Measure(int Order, int QIndex, int AngleIndex,
                      const std::vector<verWeight> &Weight, double Factor) {

  ASSERT(Order != 0, "Order must be >=1!");

  ASSERT(AngleIndex >= 0 && AngleIndex < Para.AngBinSize,
         "AngleIndex out of range!");

  for (int chan = 0; chan < 4; ++chan) {
    // cout << "chan=" << chan << ", " << AngleIndex << ", " << QIndex << endl;
    // cout << Weight[chan] << endl;
    _Estimator[chan](Order, AngleIndex, QIndex) += Weight[chan] * Factor;
    _Estimator[chan](0, AngleIndex, QIndex) += Weight[chan] * Factor;
  }
  return;
}
void ver4Obs::Save() {
  for (int chan = 0; chan < 4; chan++) {
    for (int order = 0; order <= Para.Order; order++) {
      string FileName =
          fmt::format("vertex{0}_{1}_pid{2}.dat", order, chan, Para.PID);
      ofstream VerFile;
      VerFile.open(FileName, ios::out | ios::trunc);

      if (VerFile.is_open()) {

        VerFile << fmt::sprintf("#PID:%d, rs:%.3f, Beta: %.3f, Step: %d\n",
                                Para.PID, Para.Rs, Para.Beta, Var.Counter);

        VerFile << "# Norm: " << Normalization << endl;

        VerFile << "# AngleTable: ";
        for (int angle = 0; angle < Para.AngBinSize; ++angle)
          VerFile << Para.AngleTable[angle] << " ";

        VerFile << endl;
        VerFile << "# ExtMomBinTable: ";
        for (int qindex = 0; qindex < Para.ExtMomBinSize; ++qindex)
          VerFile << Para.ExtMomTable[qindex][0] << " ";
        VerFile << endl;

        for (int angle = 0; angle < Para.AngBinSize; ++angle)
          for (int qindex = 0; qindex < Para.ExtMomBinSize; ++qindex)
            for (int dir = 0; dir < 2; ++dir)
              VerFile << _Estimator[chan](order, angle, qindex)[dir] * PhyWeight
                      << "  ";
        VerFile.close();
      } else {
        LOG_WARNING("Vertex4 for PID " << Para.PID << " fails to save!");
      }
    }
  }
};