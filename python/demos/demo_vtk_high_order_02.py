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
idx.append(gpt(1, 0, 0))
## Edge 10,11
idx.append(gpt(2, 1, 0))
## Edge 12,13
idx.append(gpt(1, 2, 0))
## Edge 14, 15
idx.append(gpt(0,1,0))
## Edge 16, 17
idx.append(gpt(1,0,2))
## Edge 18, 19
idx.append(gpt(2, 1, 2))
## Edge 20, 21
idx.append(gpt(1, 2, 2))
## Edge 22, 23
idx.append(gpt(0,1,2))
## Edge 24, 25
idx.append(gpt(0,0,1))
## Edge 26, 27
idx.append(gpt(2,0,1))
## Edge 28, 29
idx.append(gpt(2,2,1))
## Edge 30, 31
idx.append(gpt(0,2,1))

# Face 32
idx.append(gpt(1,0,1))
# Face 36
idx.append(gpt(1,2,1))
# Face 40
idx.append(gpt(0,1,1))
# Face 44
idx.append(gpt(2,1,1))
# Face 48
idx.append(gpt(1,1,0))
# Face 52
idx.append(gpt(1,1,2))

# Interior
idx.append(gpt(1,1,1))
#for t in range(1, nx - 1):
#    for s in range(1, nx - 1):
#        for r in range(1, nx - 1):
#            idx.append(gpt(r, s, t))

# FINALLY intantiate the hex cell itself
hex = vtk.vtkLagrangeHexahedron()
#hex = vtk.vtkQuadraticHexahedron()
hex.GetPointIds().SetNumberOfIds(nx**3)
hex.GetPoints().SetNumberOfPoints(nx**3)
hex.Initialize()


labels = vtk.vtkStringArray()
labels.SetName("globs")
for loc, glob in enumerate(idx):
    hex.GetPointIds().SetId(loc, glob)
    labels.InsertValue(glob, f"{loc}")


# ==================================================================
# The unstructured grid contain:
#   * Arbitrarily many cells (in this case, `hex`)
#   * One array of arbitrarily many points (in this case, `pts`)
# ==================================================================

hex_grid = vtk.vtkUnstructuredGrid()
hex_grid.Allocate(1)
hex_grid.InsertNextCell(hex.GetCellType(), hex.GetPointIds())
hex_grid.SetPoints(pts)

# Labeling
# ---------
# From https://www.programmersought.com/article/2153142323/
hex_grid.GetPointData().AddArray(labels)

text_prop = vtk.vtkTextProperty()
text_prop.SetFontSize(20)
#textProp.SetColor(whatever)
#text_prop.SetFontFamilyToArial()

hie = vtk.vtkPointSetToLabelHierarchy()
hie.SetInputData(hex_grid)
#hie.SetMaximumDepth(15)
hie.SetLabelArrayName("globs")
#hie.SetTargetLabelCount(100)
hie.SetTextProperty(text_prop)

label_mapper = vtk.vtkLabelPlacementMapper()
label_mapper.SetInputConnection(hie.GetOutputPort())

label_actor = vtk.vtkActor2D()
label_actor.SetMapper(label_mapper)


# ==================================================================
# Rendering
# ==================================================================

colors = vtk.vtkNamedColors()

# The unstructured grid itself
mapper = vtk.vtkDataSetMapper()
mapper.SetInputData(hex_grid)
actor = vtk.vtkActor()
actor.SetMapper(mapper)
actor.GetProperty().SetColor(colors.GetColor3d("Peacock"))
actor.GetProperty().EdgeVisibilityOn()

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
ren.AddActor(label_actor)

ren_win = vtk.vtkRenderWindow()
ren_win.AddRenderer(ren)

iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(ren_win)

ren.SetBackground(colors.GetColor3d("Grey"))
ren_win.SetSize(1600, 800)

# ------------------------------------
# Plotting option 1:  Just show faces
# ------------------------------------

# ------------------------------------
# Plotting option 2:  Label with GlobalIDs
# ------------------------------------

## From:  https://cmake.org/Wiki/VTK/Examples/Cxx/Visualization/LabelMesh
#ids = vtk.vtkIdFilter()
#ids.SetInputData(hex_grid)
##ids.PointIdsOn()
##ids.FieldDataOn()
#id_mapper = vtk.vtkLabeledDataMapper()
#id_mapper.SetInputConnection(ids.GetOutputPort())
#id_mapper.GetLabelTextProperty().SetFontSize(30)
#id_actor = vtk.vtkActor2D()
#id_actor.SetMapper(id_mapper)
#ren.AddActor(id_actor)
#
#
##actor.GetProperty().SetRepresentationToWireframe()

# --------------------------------------
ren_win.Render()
iren.Initialize()
iren.Start()








