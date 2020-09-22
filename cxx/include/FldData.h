#ifndef FLD_PYUTILS_CXX_SRC_FLDDATA_H
#define FLD_PYUTILS_CXX_SRC_FLDDATA_H

#include "FldHeader.h"
#include "make_lagrange_hex.h"

#include "vtkFloatArray.h"
#include "vtkHexahedron.h"
#include "vtkPointData.h"
#include "vtkPoints.h"
#include "vtkSmartPointer.h"
#include "vtkUnstructuredGrid.h"

#include <memory>
#include <regex>
#include <string>

namespace fld
{

template <typename FloatT, typename IntT>
class FldData
{
public:
  explicit FldData(const std::string& filename);
  const std::unique_ptr<FldHeader<FloatT, IntT>> H;
  vtkSmartPointer<vtkUnstructuredGrid> GetHexGrid();
  vtkSmartPointer<vtkUnstructuredGrid> GetLagrangeHexGrid();

  std::vector<FloatT> Coords;
  std::vector<FloatT> U;
  std::vector<FloatT> P;
  std::vector<FloatT> T;
  std::vector<FloatT> S;

  int Nscalars;
};

template <typename FloatT, typename IntT>
FldData<FloatT, IntT>::FldData(const std::string& filename)
  : H(std::make_unique<FldHeader<FloatT, IntT>>(filename))
{
  auto tokens = H->RdcodeTokens();
  try
  {
    std::ifstream infile(H->Filename, std::ifstream::binary);
    infile.seekg(H->FieldsBegin);
    for (const auto& tok : tokens)
    {
      // Coordinate data
      if (tok == "X" || tok == "x")
      {
        std::cout << "Located coordinates X" << std::endl;
        auto sz = H->Nelt * H->Ndims * H->Nx1 * H->Ny1 * H->Nz1;
        Coords.resize(sz);
        infile.read(reinterpret_cast<char*>(Coords.data()), sz * sizeof(FloatT));
      }

      // Velocity field
      else if (tok == "U" || tok == "u")
      {
        std::cout << "Located velocity field U" << std::endl;
        auto sz = H->Nelt * H->Ndims * H->Nx1 * H->Ny1 * H->Nz1;
        U.resize(sz);
        infile.read(reinterpret_cast<char*>(U.data()), sz * sizeof(FloatT));
      }

      // Pressure Field
      else if (tok == "P" || tok == "p")
      {
        std::cout << "Located pressure field P" << std::endl;
        auto sz = H->Nelt * H->Nx1 * H->Ny1 * H->Nz1;
        P.resize(sz);
        infile.read(reinterpret_cast<char*>(P.data()), sz * sizeof(FloatT));
      }

      // Temperature field
      else if (tok == "T" || tok == "t")
      {
        std::cout << "Located temperature field T" << std::endl;
        auto sz = H->Nelt * H->Nx1 * H->Ny1 * H->Nz1;
        T.resize(sz);
        infile.read(reinterpret_cast<char*>(T.data()), sz * sizeof(FloatT));
      }

      // Passive scalars
      else if (tok[0] == 'S' || tok[0] == 's')
      {
        Nscalars = std::stoi(tok.substr(1));
        std::cout << "Located " << Nscalars << " scalar fields S" << std::endl;
        auto sz = Nscalars * H->Nelt * H->Nx1 * H->Ny1 * H->Nz1;
        S.resize(sz);
        infile.read(reinterpret_cast<char*>(S.data()), sz * sizeof(FloatT));
      }
    }
  }
  catch (std::ifstream::failure& e)
  {
    std::cerr << e.what() << ": Couldn't open or .fld file in binary mode: " << H->Filename
              << std::endl;
    throw e;
  }
}

template <typename FloatT, typename IntT>
vtkSmartPointer<vtkUnstructuredGrid> FldData<FloatT, IntT>::GetHexGrid()
{
  const vtkIdType nx = H->Nx1; // Assume Nx1 == Ny1 == Nz1
  const vtkIdType nx2 = nx * nx;
  const vtkIdType nx3 = nx * nx * nx;
  const vtkIdType nx3Ndims = nx * nx * nx * H->Ndims;

  // ========================================================================
  // Initialize points and scalars (for temperature)
  // ========================================================================

  vtkNew<vtkPoints> points;
  points->Allocate(H->Nelt * nx3Ndims);

  vtkNew<vtkFloatArray> scalars;
  scalars->Allocate(H->Nelt * nx3);

  for (std::size_t e = 0; e < H->Nelt; ++e)
  {
    for (std::size_t r = 0; r < nx; ++r)
    {
      for (std::size_t s = 0; s < nx; ++s)
      {
        for (std::size_t t = 0; t < nx; ++t)
        {
          points->InsertNextPoint(Coords[(e * nx3Ndims) + (0 * nx3) + (r * nx2) + (s * nx) + t],
            Coords[(e * nx3Ndims) + (1 * nx3) + (r * nx2) + (s * nx) + t],
              Coords[(e * nx3Ndims) + (2 * nx3) + (r * nx2) + (s * nx) + t]);
            scalars->InsertNextTuple1(T[(e * nx3) + (r * nx2) + (s * nx) + t]);
          }
        }
      }
  }

  // ========================================================================
  // Initialize unstructured grid of hexes
  // ========================================================================

  // Return type. In very recent versions of VTK, this can be vtkNew
  auto grid = vtkSmartPointer<vtkUnstructuredGrid>::New();
  grid->Allocate(H->Nelt * nx3);

  auto gpt = [nx3, nx2, nx](vtkIdType e, vtkIdType r, vtkIdType s, vtkIdType t) {
    return e * nx3 + r * nx2 + s * nx + t;
  };

  for (vtkIdType e = 0; e < H->Nelt; ++e)
  {
    for (vtkIdType r = 0; r < nx - 1; ++r)
    {
      for (vtkIdType s = 0; s < nx - 1; ++s)
      {
        for (vtkIdType t = 0; t < nx - 1; ++t)
        {
          vtkIdType verts[8] = {
            gpt(e, r, s, t),             // 0
            gpt(e, r + 1, s, t),         // 1
            gpt(e, r + 1, s + 1, t),     // 2
            gpt(e, r, s + 1, t),         // 3
            gpt(e, r, s, t + 1),         // 4
            gpt(e, r + 1, s, t + 1),     // 5
            gpt(e, r + 1, s + 1, t + 1), // 6
            gpt(e, r, s + 1, t + 1)      // 7
          };
          grid->InsertNextCell(VTK_HEXAHEDRON, 8, verts);
        }
      }
    }
    // std::cout << "Finished " << e+1 << " / " << H->Nelt << " elements." << std::endl;
  }

  grid->SetPoints(points);
  grid->GetPointData()->SetScalars(scalars);

  return grid;
}

template <typename FloatT, typename IntT>
vtkSmartPointer<vtkUnstructuredGrid> FldData<FloatT, IntT>::GetLagrangeHexGrid()
{
  const vtkIdType nx = H->Nx1; // Assume Nx1 == Ny1 == Nz1
  const vtkIdType nx2 = nx * nx;
  const vtkIdType nx3 = nx * nx * nx;
  const vtkIdType nx3Ndims = nx * nx * nx * H->Ndims;

  // ========================================================================
  // Initialize points and scalars (for temperature)
  // ========================================================================

  vtkNew<vtkPoints> points;
  points->Allocate(H->Nelt * nx3Ndims);

  vtkNew<vtkFloatArray> scalars;
  scalars->Allocate(H->Nelt * nx3);

  for (vtkIdType e = 0; e < H->Nelt; ++e)
  {
    for (vtkIdType r = 0; r < nx; ++r)
    {
      for (vtkIdType s = 0; s < nx; ++s)
      {
        for (vtkIdType t = 0; t < nx; ++t)
        {
          points->InsertNextPoint(Coords[(e * nx3Ndims) + (0 * nx3) + (r * nx2) + (s * nx) + t],
            Coords[(e * nx3Ndims) + (1 * nx3) + (r * nx2) + (s * nx) + t],
            Coords[(e * nx3Ndims) + (2 * nx3) + (r * nx2) + (s * nx) + t]);
          scalars->InsertNextTuple1(T[(e * nx3) + (r * nx2) + (s * nx) + t]);
        }
      }
    }
  }

  // Return type. In very recent versions of VTK, this can be vtkNew
  auto grid = vtkSmartPointer<vtkUnstructuredGrid>::New();
  grid->Allocate(H->Nelt);

  const std::size_t numPoints =
    8 + 12 * (nx - 2) + 6 * (nx - 2) * (nx - 2) + (nx - 2) * (nx - 2) * (nx - 2);
  vtkIdType pts[numPoints];
  for (vtkIdType e = 0; e < H->Nelt; ++e)
  {
    MakeLagrandIDs(pts, e, nx);
    grid->InsertNextCell(VTK_LAGRANGE_HEXAHEDRON, numPoints, pts);
    // std::cout << "Finished " << e+1 << " / " << H->Nelt << " elements." << std::endl;
  }

  grid->SetPoints(points);
  grid->GetPointData()->SetScalars(scalars);

  return grid;
}

}

#endif // FLD_PYUTILS_CXX_SRC_FLDDATA_H
