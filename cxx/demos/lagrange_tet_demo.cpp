#include "vtkActor.h"
#include "vtkCellArray.h"
#include "vtkDataSetMapper.h"
#include "vtkLagrangeTetra.h"
#include "vtkNamedColors.h"
#include "vtkPoints.h"
#include "vtkProperty.h"
#include "vtkRenderWindow.h"
#include "vtkRenderWindowInteractor.h"
#include "vtkRenderer.h"
#include "vtkSmartPointer.h"
#include "vtkUnstructuredGrid.h"

int main()
{
  int order = 6;
  int nPoints = int((order + 1) * (order + 2) * (order + 3) / 6);

  vtkNew<vtkLagrangeTetra> tet;
  tet->GetPointIds()->SetNumberOfIds(nPoints);
  tet->GetPoints()->SetNumberOfPoints(nPoints);
  tet->Initialize();

  double pt[] = { 0.0, 0.0, 0.0 };
  long long barycentricIndex[] = { 0, 0, 0, 0 };

  for (int i = 0; i < nPoints; ++i)
  {
    tet->GetPointIds()->SetId(i, i);
    tet->ToBarycentricIndex(i, barycentricIndex);
    for (int j = 0; j < 3; ++j)
    {
      pt[j] = double(barycentricIndex[j]) / order;
    }
    tet->GetPoints()->SetPoint(i, pt);
  }

  vtkNew<vtkCellArray> tets;
  tets->InsertNextCell(tet);

  vtkNew<vtkUnstructuredGrid> ugrid;
  ugrid->SetPoints(tet->GetPoints());
  ugrid->InsertNextCell(tet->GetCellType(), tet->GetPointIds());

  vtkNew<vtkDataSetMapper> mapper;
  mapper->SetInputData(ugrid);

  vtkNew<vtkActor> actor;
  actor->SetMapper(mapper);
  actor->GetProperty()->EdgeVisibilityOn();

  vtkNew<vtkRenderer> ren;
  vtkNew<vtkRenderWindow> renWin;
  renWin->AddRenderer(ren);
  vtkNew<vtkRenderWindowInteractor> iren;
  iren->SetRenderWindow(renWin);

  ren->AddActor(actor);
  ren->SetBackground(249, 228, 183); // beige

  renWin->Render();

  iren->Initialize();
  iren->Start();
}