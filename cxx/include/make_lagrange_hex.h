#ifndef FLD_PYUTILS_CXX_INCLUDE_MAKE_LAGRANGE_HEX_H
#define FLD_PYUTILS_CXX_INCLUDE_MAKE_LAGRANGE_HEX_H

#include "vtkIdList.h"
#include "vtkLagrangeHexahedron.h"
#include "vtkSmartPointer.h"

namespace fld
{

vtkSmartPointer<vtkLagrangeHexahedron> MakeLagrangeHex(std::size_t e, std::size_t nx);
void MakeLagrandIDs(vtkIdType* pts, vtkIdType e, vtkIdType nx);
}

#endif // FLD_PYUTILS_CXX_INCLUDE_MAKE_LAGRANGE_HEX_H
