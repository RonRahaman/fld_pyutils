from fld_data_memmap import FldDataMemmap
import vtk
from fld_data import FldData


filename = '../data/rod_short0.f00001'
clip_origin = [0.0, 0.0, 2.5]
clip_normal = [1.0, 0.0, 0.0]


d1 = FldData.fromfile(filename)
#hex_grid = d1.get_hex_grid()
hex_grid = d1.get_lagrange_hex_grid()

# Clipping:  https://lorensen.github.io/VTKExamples/site/Python/UnstructuredGrid/ClipUnstructuredGridWithPlane2/
colors = vtk.vtkNamedColors()

clip_plane = vtk.vtkPlane()
#clip_plane.SetOrigin(hex_grid.GetCenter())
#clip_plane.SetNormal([1.0, 0.0, 0.0])
clip_plane.SetOrigin(clip_origin)
clip_plane.SetNormal(clip_normal)

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

actor = vtk.vtkLODActor()
actor.SetMapper(mapper)
# actor.GetProperty().SetRepresentationToWireframe()
# actor.GetProperty().SetColor(colors.GetColor3d("Peacock"))
actor.GetProperty().EdgeVisibilityOn()
actor.GetProperty().SetLineWidth(0.25)
actor.GetProperty().SetAmbient(50)

camera = vtk.vtkCamera()
camera.SetPosition([-5, 0, 20])
camera.SetFocalPoint([5, 0, 0])
camera.Zoom(4)

ren = vtk.vtkRenderer()
ren.AddActor(actor)
ren.SetActiveCamera(camera)
ren.SetBackground(colors.GetColor3d("Beige"))

ren_win = vtk.vtkRenderWindow()
ren_win.AddRenderer(ren)
ren_win.SetSize(1600, 800)

iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(ren_win)

ren_win.Render()

# https://lorensen.github.io/VTKExamples/site/Python/IO/ImageWriter/
writer = vtk.vtkBMPWriter()
win_to_img_filter = vtk.vtkWindowToImageFilter()
win_to_img_filter.SetInput(ren_win)
win_to_img_filter.SetScale(1)
win_to_img_filter.SetInputBufferTypeToRGB()
win_to_img_filter.ReadFrontBufferOff()
win_to_img_filter.Update()
writer.SetFileName('rod_short.bmp')
writer.SetInputConnection(win_to_img_filter.GetOutputPort())
writer.Write()

iren.Initialize()
iren.Start()