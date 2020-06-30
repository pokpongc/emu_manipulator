//
// Academic License - for use in teaching, academic research, and meeting
// course requirements at degree granting institutions only.  Not for
// government, commercial, or other organizational use.
// File: updateWorkingSetForNewQP.h
//
// MATLAB Coder version            : 4.3
// C/C++ source code generated on  : 24-Jun-2020 08:27:59
//
#ifndef UPDATEWORKINGSETFORNEWQP_H
#define UPDATEWORKINGSETFORNEWQP_H

// Include Files
#include <cstddef>
#include <cstdlib>
#include "rtwtypes.h"
#include "timeOpt6DofGen_types.h"

// Function Declarations
extern void updateWorkingSetForNewQP(h_struct_T *WorkingSet, int mIneq, int
  mNonlinIneq, const emxArray_real_T *cIneq, int mEq, int mNonlinEq, const
  emxArray_real_T *cEq);

#endif

//
// File trailer for updateWorkingSetForNewQP.h
//
// [EOF]
//