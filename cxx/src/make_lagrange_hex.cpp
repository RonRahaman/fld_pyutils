#include "make_lagrange_hex.h"
#include "vtkPointData.h"
#include "vtkPoints.h"

vtkSmartPointer<vtkLagrangeHexahedron> fld::MakeLagrangeHex(std::size_t e, std::size_t nx)
{

  // Very recent versions allow vtkNew as return type:
  // https://discourse.vtk.org/t/vtknew-and-vtksmartpointer/469/10 For now, use vtkSmartPointer:
  // https://vtk.org/Wiki/VTK/Tutorials/SmartPointers

  const auto nx2 = nx * nx;
  const auto nx3 = nx * nx * nx;

  auto gpt = [nx3, nx2, nx](std::size_t e, std::size_t r, std::size_t s, std::size_t t) {
    return e * nx3 + r * nx2 + s * nx + t;
  };

  std::vector<std::size_t> glid{ gpt(e, 0, 0, 0), gpt(e, nx - 1, 0, 0), gpt(e, nx - 1, nx - 1, 0),
    gpt(e, 0, nx - 1, 0), gpt(e, 0, 0, nx - 1), gpt(e, nx - 1, 0, nx - 1),
    gpt(e, nx - 1, nx - 1, nx - 1), gpt(e, 0, nx - 1, nx - 1) };

  // Edge 8, 9
  for (int i = 1; i < nx - 1; ++i)
  {
    glid.push_back(gpt(e, i, 0, 0));
  }
  // Edge 10, 11
  for (int i = 1; i < nx - 1; ++i)
  {
    glid.push_back(gpt(e, nx - 1, i, 0));
  }
  // Edge 12, 13
  for (int i = 1; i < nx - 1; ++i)
  {
    glid.push_back(gpt(e, i, nx - 1, 0));
  }
  // Edge 14, 15
  for (int i = 1; i < nx - 1; ++i)
  {
    glid.push_back(gpt(e, 0, i, 0));
  }
  // Edge 16, 17
  for (int i = 1; i < nx - 1; ++i)
  {
    glid.push_back(gpt(e, i, 0, nx - 1));
  }
  // Edge 18, 19
  for (int i = 1; i < nx - 1; ++i)
  {
    glid.push_back(gpt(e, nx - 1, i, nx - 1));
  }
  // Edge 20, 21
  for (int i = 1; i < nx - 1; ++i)
  {
    glid.push_back(gpt(e, i, nx - 1, nx - 1));
  }
  // Edge 22, 23
  for (int i = 1; i < nx - 1; ++i)
  {
    glid.push_back(gpt(e, 0, i, nx - 1));
  }
  // Edge 24, 25
  for (int i = 1; i < nx - 1; ++i)
  {
    glid.push_back(gpt(e, 0, 0, i));
  }
  // Edge 26, 27
  for (int i = 1; i < nx - 1; ++i)
  {
    glid.push_back(gpt(e, nx - 1, 0, i));
  }
  // Edge 30, 31
  for (int i = 1; i < nx - 1; ++i)
  {
    glid.push_back(gpt(e, 0, nx - 1, i));
  }
  // Edge 28, 29
  for (int i = 1; i < nx - 1; ++i)
  {
    glid.push_back(gpt(e, nx - 1, nx - 1, i));
  }

  // Face 40
  for (int t = 1; t < nx - 1; ++t)
  {
    for (int s = 1; s < nx - 1; ++s)
    {
      glid.push_back(gpt(e, 0, s, t));
    }
  }
  // Face 44
  for (int t = 1; t < nx - 1; ++t)
  {
    for (int s = 1; s < nx - 1; ++s)
    {
      glid.push_back(gpt(e, nx - 1, s, t));
    }
  }
  // Face 32
  for (int t = 1; t < nx - 1; ++t)
  {
    for (int r = 1; r < nx - 1; ++r)
    {
      glid.push_back(gpt(e, r, 0, t));
    }
  }
  // Face 36
  for (int t = 1; t < nx - 1; ++t)
  {
    for (int r = 1; r < nx - 1; ++r)
    {
      glid.push_back(gpt(e, r, nx - 1, t));
    }
  }
  // Face 48
  for (int s = 1; s < nx - 1; ++s)
  {
    for (int r = 1; r < nx - 1; ++r)
    {
      glid.push_back(gpt(e, r, s, 0));
    }
  }
  // Face 52
  for (int s = 1; s < nx - 1; ++s)
  {
    for (int r = 1; r < nx - 1; ++r)
    {
      glid.push_back(gpt(e, r, s, nx - 1));
    }
  }

  // Interior
  for (int t = 1; t < nx - 1; ++t)
  {
    for (int s = 1; s < nx - 1; ++s)
    {
      for (int r = 1; r < nx - 1; ++r)
      {
        glid.push_back(gpt(e, r, s, t));
      }
    }
  }

  auto hex = vtkSmartPointer<vtkLagrangeHexahedron>::New();
  hex->GetPointIds()->SetNumberOfIds(nx3);
  hex->GetPoints()->SetNumberOfPoints(nx3);
  hex->Initialize();

  for (int locid = 0; locid < glid.size(); ++locid)
  {
    hex->GetPointIds()->SetId(locid, glid[locid]);
  }

  return hex;
}
