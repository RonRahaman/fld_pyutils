from fld_data_memmap import FldDataMemmap
import vtk
from fld_data import FldData

#d1 = FldDataMemmap.fromfile('demos/data/test0.f00001')
d1 = FldData.fromfile('testA/rod_short0.f00001')
hex_grid = d1.get_hex_grid()
#hex_grid = d1.get_lagrange_hex_grid()

# Clipping:  https://lorensen.github.io/VTKExamples/site/Python/UnstructuredGrid/ClipUnstructuredGridWithPlane2/
colors = vtk.vtkNamedColors()

clip_plane = vtk.vtkPlane()
clip_plane.SetOrigin(hex_grid.GetCenter())
clip_plane.SetNormal([1.0, 0.0, 0.0])

clipper = vtk.vtkClipDataSet()
clipper.SetClipFunction(clip_plane)
clipper.SetInputData(hex_grid)
clipper.SetValue(0.0)
clipper.GenerateClippedOutputOn()
clipper.Update()

mapper = vtk.vtkDataSetMapper()
mapper.SetInputData(clipper.GetOutput())
mapper.SetScalarRange(hex_grid.GetScalarRange())

# mapper = vtk.vtkDataSetMapper()
# mapper.SetInputData(hex_grid)
# mapper.SetScalarRange(hex_grid.GetScalarRange())

# Plot it!

actor = vtk.vtkActor()
actor.SetMapper(mapper)
# actor.GetProperty().SetRepresentationToWireframe()
# actor.GetProperty().SetColor(colors.GetColor3d("Peacock"))
actor.GetProperty().EdgeVisibilityOn()
actor.GetProperty().SetLineWidth(0.25)
actor.GetProperty().SetAmbient(50)

ren = vtk.vtkRenderer()
ren.AddActor(actor)
ren.SetBackground(colors.GetColor3d("Beige"))

ren_win = vtk.vtkRenderWindow()
ren_win.AddRenderer(ren)
ren_win.SetSize(1600, 800)

iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(ren_win)

ren_win.Render()

iren.Initialize()
iren.Start()

#d1 = FldDataMemmap.fromfile('demos/data/test0.f00001')
d1 = FldData.fromfile('testA/rod_short0.f00001')
