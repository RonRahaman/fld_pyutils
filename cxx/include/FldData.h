#ifndef FLD_PYUTILS_CXX_SRC_FLDDATA_H
#define FLD_PYUTILS_CXX_SRC_FLDDATA_H

#include "FldHeader.h"
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
  inline std::size_t gpt(std::size_t e, std::size_t r, std::size_t s, std::size_t t) const;

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
std::size_t FldData<FloatT, IntT>::gpt(
  std::size_t e, std::size_t r, std::size_t s, std::size_t t) const
{
  return (e * H->Nx1 * H->Nx1 * H->Nx1) + (r * H->Nx1 * H->Nx1) + (s * H->Nx1) + t;
}

template <typename FloatT, typename IntT>
vtkSmartPointer<vtkUnstructuredGrid> FldData<FloatT, IntT>::GetHexGrid()
{
  auto nx = H->Nx1; // Assume Nx1 == Ny1 == Nz1

  // ========================================================================
  // Initialize points and scalars (for temperature)
  // ========================================================================

  auto points = vtkSmartPointer<vtkPoints>::New();
  points->Allocate(H->Nelt * nx * nx * nx);

  auto scalars = vtkSmartPointer<vtkFloatArray>::New();

  for (std::size_t e = 0; e < H->Nelt; ++e)
  {
      for (std::size_t r = 0; r < nx; ++r)
      {
        for (std::size_t s = 0; s < nx; ++s)
        {
          for (std::size_t t = 0; t < nx; ++t)
          {
            points->InsertNextPoint(
              Coords[(e * nx * nx * nx * H->Ndims) + (0 * nx * nx * nx) + (r * nx * nx) + (s * nx) + t],
              Coords[(e * nx * nx * nx * H->Ndims) + (1 * nx * nx * nx) + (r * nx * nx) + (s * nx) + t],
              Coords[(e * nx * nx * nx * H->Ndims) + (2 * nx * nx * nx) + (r * nx * nx) + (s * nx) + t]);
            scalars->InsertNextTuple1(
              T[(e * nx * nx * nx) + (r * nx * nx) + (s * nx) + t]);
          }
        }
     }
  }


  // ========================================================================
  // Initialize unstructured grid of hexes
  // ========================================================================

  auto grid = vtkSmartPointer<vtkUnstructuredGrid>::New();
  grid->Allocate(H->Nelt * nx * nx * nx);
  //grid->Allocate(1 * nx * nx * nx);

  for (std::size_t e = 0; e < H->Nelt; ++e)
  //for (std::size_t e = 0; e < 1; ++e)
  {
    for (std::size_t r = 0; r < nx-1; ++r)
    {
      for (std::size_t s = 0; s < nx-1; ++s)
      {
        for (std::size_t t = 0; t < nx-1; ++t)
        {
          //auto hex = vtkSmartPointer<vtkHexahedron>::New();
          vtkNew<vtkHexahedron> hex;
          hex->GetPointIds()->SetNumberOfIds(8);
          hex->Initialize();
          std::size_t verts[8] = {
            gpt(e, r, s, t),             // 0
            gpt(e, r + 1, s, t),         // 1
            gpt(e, r + 1, s + 1, t),     // 2
            gpt(e, r, s + 1, t),         // 3
            gpt(e, r, s, t + 1),         // 4
            gpt(e, r + 1, s, t + 1),     // 5
            gpt(e, r + 1, s + 1, t + 1), // 6
            gpt(e, r, s + 1, t + 1)      // 7
          };
          for (int i = 0; i < 8; ++i)
          {
            hex->GetPointIds()->SetId(i, verts[i]);
          }
          grid->InsertNextCell(hex->GetCellType(), hex->GetPointIds());
        }
      }
    }
    std::cout << "Finished " << e+1 << " / " << H->Nelt << " elements." << std::endl;
  }

  grid->SetPoints(points);
  grid->GetPointData()->SetScalars(scalars);

  return grid;
}

}

#endif // FLD_PYUTILS_CXX_SRC_FLDDATA_H
