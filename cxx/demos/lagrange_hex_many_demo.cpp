#include "vtkActor.h"
#include "vtkActor2D.h"
#include "vtkAxes.h"
#include "vtkAxesActor.h"
#include "vtkCaptionActor2D.h"
#include "vtkDataSetMapper.h"
#include "vtkLabelPlacementMapper.h"
#include "vtkLagrangeHexahedron.h"
#include "vtkPointData.h"
#include "vtkPoints.h"
#include "vtkProperty.h"
#include "vtkRenderWindow.h"
#include "vtkRenderWindowInteractor.h"
#include "vtkRenderer.h"
#include "vtkSmartPointer.h"
#include "vtkTextActor.h"
#include "vtkTextProperty.h"
#include "vtkUnstructuredGrid.h"

#include <vector>

int nx = 4;
int nelt = 10;
int dx = 1;

int gpt(int e, int r, int s, int t)
{
  return (e * nx * nx * nx) + (r * nx * nx) + (s * nx) + t;
}

vtkSmartPointer<vtkLagrangeHexahedron> makeHex(int e)
{
  // Very recent versions allow vtkNew as return type:
  // https://discourse.vtk.org/t/vtknew-and-vtksmartpointer/469/10 For now, use vtkSmartPointer:
  // https://vtk.org/Wiki/VTK/Tutorials/SmartPointers

  std::vector<int> glid{ gpt(e, 0, 0, 0), gpt(e, nx - 1, 0, 0), gpt(e, nx - 1, nx - 1, 0),
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
  hex->GetPointIds()->SetNumberOfIds(nx * nx * nx);
  hex->GetPoints()->SetNumberOfPoints(nx * nx * nx);
  hex->Initialize();

  for (int locid = 0; locid < glid.size(); ++locid)
  {
    hex->GetPointIds()->SetId(locid, glid[locid]);
  }

  return hex;
}

int main()
{
  vtkNew<vtkPoints> pts;
  pts->Allocate(nx * nx * nx);

  for (int e = 0; e < nelt; ++e)
  {
    for (int r = 0; r < nx; ++r)
    {
      for (int s = 0; s < nx; ++s)
      {
        for (int t = 0; t < nx; ++t)
        {
          pts->InsertNextPoint(e * ((nx - 1) * dx + 0.2) + r * dx, s * dx, t * dx);
        }
      }
    }
  }

  vtkNew<vtkUnstructuredGrid> hexGrid;
  hexGrid->Allocate(nelt);

  // Works!
  for (int e = 0; e < nelt; ++e)
  {
    auto hex = makeHex(e);
    hexGrid->InsertNextCell(hex->GetCellType(), hex->GetPointIds());
  }

  hexGrid->SetPoints(pts);

  //================================================================
  // Rendering
  //================================================================

  vtkNew<vtkDataSetMapper> mapper;
  mapper->SetInputData(hexGrid);

  vtkNew<vtkActor> actor;
  actor->SetMapper(mapper);
  actor->GetProperty()->EdgeVisibilityOn();
  actor->GetProperty()->SetColor(0, 0.5, 1);

  vtkNew<vtkAxesActor> axes;
  auto l = dx * (nx + 1);
  axes->SetTotalLength(l, l, l);
  int s = 5;
  axes->GetXAxisCaptionActor2D()->GetTextActor()->GetTextProperty()->SetFontSize(s);
  axes->GetYAxisCaptionActor2D()->GetTextActor()->GetTextProperty()->SetFontSize(s);
  axes->GetZAxisCaptionActor2D()->GetTextActor()->GetTextProperty()->SetFontSize(s);

  vtkNew<vtkRenderer> ren;
  ren->AddActor(actor);
  ren->AddActor(axes);
  ren->SetBackground(0, 0, 0); // beige

  vtkNew<vtkRenderWindow> renWin;
  renWin->AddRenderer(ren);
  renWin->SetSize(1200, 800);

  vtkNew<vtkRenderWindowInteractor> iren;
  iren->SetRenderWindow(renWin);

  renWin->Render();
  iren->Initialize();
  iren->Start();
}
