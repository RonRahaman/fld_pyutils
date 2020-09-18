import vtk

nx = 3    # Number of gridpoints in each dim
dx = 0.1  # Spacing between gridpoints

# ==================================================================
# `pts` is a list of all points' coordinates in the data set
# ==================================================================

pts = vtk.vtkPoints()
pts.Allocate(nx**3)

for r in range(nx):
    for s in range(nx):
        for t in range(nx):
            pts.InsertNextPoint([r * dx, s * dx, t * dx])

# ==================================================================
# A cell maps point IDs (in the cell) -> point IDs (in entire model)
#   * The IDs in the cell correspond to the orderings described here
#     https://blog.kitware.com/wp-content/uploads/2018/09/Source_Issue_43.pdf
#   * The IDs in the entire model correspond to the indices in the
#     `pts` array
# ==================================================================


# In this simple demo, we've ordered `pts` so that it is in the same
# order as the cell IDs
hex = vtk.vtkLagrangeHexahedron()
hex.GetPointIds().SetNumberOfIds(nx**3)
hex.GetPoints().SetNumberOfPoints(nx**3)
hex.Initialize()
for i in range(nx**3):
    hex.GetPointIds().SetId(i, i)

# ==================================================================
# The unstructured grid contain:
#   * Arbitrarily many cells (in this case, `hex`)
#   * One array of arbitrarily many points (in this case, `pts`)
# ==================================================================

hex_grid = vtk.vtkUnstructuredGrid()
hex_grid.Allocate(1)
hex_grid.InsertNextCell(hex.GetCellType(), hex.GetPointIds())
hex_grid.SetPoints(pts)

# ==================================================================
# Render it!  This is mostly boilerplate and can be safely ignored
# ==================================================================

colors = vtk.vtkNamedColors()

mapper = vtk.vtkDataSetMapper()
mapper.SetInputData(hex_grid)

actor = vtk.vtkActor()
actor.SetMapper(mapper)
# actor.GetProperty().SetRepresentationToWireframe()
actor.GetProperty().SetColor(colors.GetColor3d("Peacock"))
actor.GetProperty().EdgeVisibilityOn()

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








