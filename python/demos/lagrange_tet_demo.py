# from docs/Source_Issue_43.py

import numpy as np
import vtk

# Making a 6-th order tetrahedron
order = 6
n_points = int((order + 1) * (order + 2) * (order + 3) / 6)

# Create a tetrahedron with given number of points.
# Internally, Lagrange cells compute their order according to
# the number of points they hold
tet = vtk.vtkLagrangeTetra()
tet.GetPointIds().SetNumberOfIds(n_points)
tet.GetPoints().SetNumberOfPoints(n_points)
tet.Initialize()

point = [0., 0., 0.]
barycentric_index = [0, 0, 0, 0]

for i in range(n_points):
    tet.GetPointIds().SetId(i, i)
    tet.ToBarycentricIndex(i, barycentric_index)
    for j in range(3):
        point[j] = barycentric_index[j] / order
    tet.GetPoints().SetPoint(i, point[0], point[1], point[2])

tets = vtk.vtkCellArray()
tets.InsertNextCell(tet)

# TODO for Ron:  Compare this to the other ugrid examples.
#  Pretty much boilerplate from here on down
ugrid = vtk.vtkUnstructuredGrid()
ugrid.SetPoints(tet.GetPoints())
ugrid.InsertNextCell(tet.GetCellType(), tet.GetPointIds())

colors = vtk.vtkNamedColors()

mapper = vtk.vtkDataSetMapper()
mapper.SetInputData(ugrid)

actor = vtk.vtkActor()
actor.SetMapper(mapper)
actor.GetProperty().SetColor(colors.GetColor3d("Peacock"))
actor.GetProperty().EdgeVisibilityOn()

ren = vtk.vtkRenderer()
ren_win = vtk.vtkRenderWindow()
ren_win.AddRenderer(ren)
iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(ren_win)

ren.AddActor(actor)
ren.SetBackground(colors.GetColor3d("Beige"))

iren.Initialize()
ren_win.Render()
iren.Start()
