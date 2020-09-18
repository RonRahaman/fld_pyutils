import vtk

nx = 3    # Number of gridpoints in each dim
dx = 1  # Spacing between gridpoints

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

# Get the index in `pts` array that corresponds to a given (r, s, t) point in cell
def gpt(r, s, t):
    return (r * nx**2) + (s * nx) + t

# Idx maps a point ID (in cell) -> point ID (in entire model).
idx = [
    gpt(0, 0, 0),  # Vertex 0
    gpt(nx - 1, 0, 0),  # Vertex 1
    gpt(nx - 1, nx - 1, 0),  # Vertex 2
    gpt(0, nx - 1, 0),  # Vertex 3
    gpt(0, 0, nx - 1),  # Vertex 4
    gpt(nx - 1, 0, nx - 1),  # Vertex 5
    gpt(nx - 1, nx - 1, nx - 1),  # Vertex 6
    gpt(0, nx - 1, nx - 1),  # Vertex 8
]

# Edge 8,9
for i in range(1, nx - 1):
    idx.append(gpt(i, 0, 0))
# Edge 10,11
for i in range(1, nx - 1):
    idx.append(gpt(nx - 1, i, 0))
# Edge 12,13
for i in range(1, nx - 1):
    idx.append(gpt(i, nx - 1, 0))
# Edge 14, 15
for i in range(1, nx - 1):
    idx.append(gpt(0, i, 0))
# Edge 16, 17
for i in range(1, nx - 1):
    idx.append(gpt(i, 0, nx - 1))
# Edge 18, 19
for i in range(1, nx - 1):
    idx.append(gpt(nx - 1, i, nx - 1))
# Edge 20, 21
for i in range(1, nx - 1):
    idx.append(gpt(i, nx - 1, nx - 1))
# Edge 22, 23
for i in range(1, nx - 1):
    idx.append(gpt(0, i, nx - 1))
# Edge 24, 26
for i in range(1, nx - 1):
    idx.append(gpt(0, 0, i))
# Edge 26, 27
for i in range(1, nx - 1):
    idx.append(gpt(nx - 1, 0, i))
# Edge 28, 29
for i in range(1, nx - 1):
    idx.append(gpt(nx - 1, nx - 1, i))
# Edge 30, 31
for i in range(1, nx - 1):
    idx.append(gpt(0, nx - 1, i))

# Face 32
for t in range(1, nx - 1):
    for r in range(1, nx - 1):
        idx.append(gpt(r, 0, t))
# Face 36
for t in range(1, nx - 1):
    for r in range(1, nx - 1):
        idx.append(gpt(r, nx - 1, t))
# Face 40
for t in range(1, nx - 1):
    for s in range(1, nx - 1):
        idx.append(gpt(0, s, t))
# Face 44
for t in range(1, nx - 1):
    for s in range(1, nx - 1):
        idx.append(gpt(nx - 1, s, t))
# Face 48
for s in range(1, nx - 1):
    for r in range(1, nx - 1):
        idx.append(gpt(r, s, 0))
# Face 52
for s in range(1, nx - 1):
    for r in range(1, nx - 1):
        idx.append(gpt(r, s, nx - 1))

# Interior
for t in range(1, nx - 1):
    for s in range(1, nx - 1):
        for r in range(1, nx - 1):
            idx.append(gpt(r, s, t))

# FINALLY intantiate the hex cell itself
hex = vtk.vtkLagrangeHexahedron()
#hex = vtk.vtkQuadraticHexahedron()
hex.GetPointIds().SetNumberOfIds(nx**3)
hex.GetPoints().SetNumberOfPoints(nx**3)
hex.Initialize()
for i, x in enumerate(idx):
    hex.GetPointIds().SetId(i, x)

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
# Color pts by point ID (in cell)
# ==================================================================
#scalars = vtk.vtkFloatArray()
#for i in range(nx**3):
#    scalars.InsertTuple1(i, i)
#hex_grid.GetPointData().SetScalars(scalars)

# ==================================================================
# Rendering
# ==================================================================

colors = vtk.vtkNamedColors()

# The unstructured grid itself
mapper = vtk.vtkDataSetMapper()
mapper.SetInputData(hex_grid)
actor = vtk.vtkActor()
actor.SetMapper(mapper)

# The Axes
axes = vtk.vtkAxesActor()
l = dx * (nx + 1)
axes.SetTotalLength(l, l, l)
s = 5
axes.GetXAxisCaptionActor2D().GetTextActor().GetTextProperty().SetFontSize(s)
axes.GetYAxisCaptionActor2D().GetTextActor().GetTextProperty().SetFontSize(s)
axes.GetZAxisCaptionActor2D().GetTextActor().GetTextProperty().SetFontSize(s)

ren = vtk.vtkRenderer()
ren.AddActor(actor)
ren.AddActor(axes)

ren_win = vtk.vtkRenderWindow()
ren_win.AddRenderer(ren)

iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(ren_win)

ren.SetBackground(colors.GetColor3d("Black"))
ren_win.SetSize(1600, 800)

# ------------------------------------
# Plotting option 1:  Just show faces
# ------------------------------------
#actor.GetProperty().SetColor(colors.GetColor3d("Peacock"))
#actor.GetProperty().EdgeVisibilityOn()

# ------------------------------------
# Plotting option 2:  Label IDs
# ------------------------------------

# From:  https://cmake.org/Wiki/VTK/Examples/Cxx/Visualization/LabelMesh
ids = vtk.vtkIdFilter()
ids.SetInputData(hex_grid)
ids.PointIdsOn()
id_mapper = vtk.vtkLabeledDataMapper()
id_mapper.SetInputConnection(ids.GetOutputPort())
id_mapper.GetLabelTextProperty().SetFontSize(30)
id_actor = vtk.vtkActor2D()
id_actor.SetMapper(id_mapper)
ren.AddActor(id_actor)

actor.GetProperty().SetRepresentationToWireframe()

# --------------------------------------
ren_win.Render()
iren.Initialize()
iren.Start()








