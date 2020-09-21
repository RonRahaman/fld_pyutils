#include "FldData.h"
#include "vtkPlane.h"
#include "vtkClipDataSet.h"
#include "vtkDataSetMapper.h"
#include "vtkActor.h"
#include "vtkProperty.h"
#include "vtkRenderer.h"
#include "vtkRenderWindow.h"
#include "vtkRenderWindowInteractor.h"

#include <cassert>

int main(int argc, char* argv[]) {

  //assert(argc > 1);
  //std::string filename{argv[1]};
  std::string filename{ "/Users/ronald/repos/fld_pyutils/data/rod_short0.f00001" };

  fld::FldData<float, int> data(filename);
  auto hexGrid = data.GetHexGrid();

  auto clipPlane = vtkSmartPointer<vtkPlane>::New();
  clipPlane->SetOrigin(hexGrid->GetCenter());
  clipPlane->SetNormal(1.0, 0.0, 0.0);

  auto clipper = vtkSmartPointer<vtkClipDataSet>::New();
  clipper->SetClipFunction(clipPlane);
  clipper->SetInputData(hexGrid);
  clipper->SetValue(0.0);
  clipper->GenerateClippedOutputOn();
  clipper->Update();

  auto mapper = vtkSmartPointer<vtkDataSetMapper>::New();
  mapper->SetInputData(clipper->GetOutput());
  mapper->SetScalarRange(hexGrid->GetScalarRange());

  auto actor = vtkSmartPointer<vtkActor>::New();
  actor->SetMapper(mapper);
  actor->GetProperty()->EdgeVisibilityOn();
  actor->GetProperty()->SetLineWidth(0.25);
  actor->GetProperty()->SetAmbient(50);

  auto ren = vtkSmartPointer<vtkRenderer>::New();
  ren->AddActor(actor);
  ren->SetBackground(245, 245, 220);  // beige

  auto renWin = vtkSmartPointer<vtkRenderWindow>::New();
  renWin->AddRenderer(ren);
  renWin->SetSize(1600, 800);

  auto iren = vtkSmartPointer<vtkRenderWindowInteractor>::New();
  iren->SetRenderWindow(renWin);

  renWin->Render();
  iren->Initialize();
  iren->Start();
}