from fld_data_base import FldDataBase
from fld_header import FldHeader
import numpy as np
import re
import vtk

colors = vtk.vtkNamedColors()

# TODO: This uses tofile from the base class, which probably creates some intermediate byte arrays
# Might want to see if this is significant memory disadvantage...

class FldDataMemmap(FldDataBase):

    def __init__(self,
                 header: FldHeader,
                 readonly: bool = False,
                 coords: np.ndarray = None,
                 u: np.ndarray = None,
                 p: np.ndarray = None,
                 t: np.ndarray = None,
                 s: np.ndarray = None):

        super().__init__(header)

        self._readonly = readonly
        self._coords = np.array([], self.float_type)
        self._u = np.array([], self.float_type)
        self._p = np.array([], self.float_type)
        self._t = np.array([], self.float_type)
        self._s = np.array([], self.float_type)

        if coords is not None:
            self._coords = coords
        if u is not None:
            self._u = u
        if p is not None:
            self._p = p
        if t is not None:
            self._t = t
        if s is not None:
            self._s = s

        self._set_rdcode()

    @classmethod
    def fromfile(cls, filename: str, mode: str = "r"):

        # Validate mode
        if mode not in ('r', 'r+', 'w+', 'c'):
            raise ValueError(f"User specified mode was {mode}, but mode must be 'r', 'r+', 'w+', or 'c'")

        # Read header and get offset where field data begin
        h = FldHeader.fromfile(filename)
        nxyz = h.nx1 * h.ny1 * h.nz1
        offset = 136 + h.nelt * h.int_type.itemsize

        # Some convenience functions
        def notify(msg: str):
            print("[{}] : {}".format(filename, msg))

        def error(msg: str):
            raise Exception("[{}] : {}".format(filename, msg))

        def read_memmap(shape):
            nonlocal offset
            v = np.memmap(filename, dtype=h.float_type, offset=offset, mode=mode, shape=shape)
            offset += v.nbytes
            return v

        # Now parse everything!
        coords = None
        u = None
        p = None
        t = None
        s = None
        notify("Attempting to fields from rdcode {}".format(h.rdcode))
        code_list = [s.upper() for s in re.split(r'(\D\d*)', h.rdcode) if s]
        for code in code_list:
            # Coordinate data
            if code == 'X':
                notify("Located coordinates X")
                coords = read_memmap((h.nelt, h.ndims, nxyz))
            # Velocity field
            elif code == 'U':
                notify("Located velocity field U")
                u = read_memmap((h.nelt, h.ndims, nxyz))
            # Pressure field
            elif code == 'P':
                notify("Located pressure field P")
                p = read_memmap((h.nelt, nxyz))
            # Temperature field
            elif code == 'T':
                notify("Located temperature field T")
                t = read_memmap((h.nelt, nxyz))
            # Passive scalars
            elif code.startswith('S'):
                try:
                    nscalars = int(code[1:])
                except ValueError:
                    error("Couldn'_t parse number of passive scalar fields")
                else:
                    notify("Located {} passive scalar fields".format(nscalars))
                    s = read_memmap((nscalars, h.nelt, nxyz))
            else:
                error("Warning: Unsupported rdcode '{}'".format(code))

        return cls(header=h, readonly=(mode == 'r'), coords=coords, u=u, p=p, t=t, s=s)

    @FldDataBase.coords.setter
    def coords(self, other: np.ndarray):
        if self._readonly:
            raise AttributeError("FldDataMemmap in read-only mode does not support field assignment.")
        if other.size != 0 and other.shape != (self.nelt, self.ndims, self.nx1 * self.ny1 * self.nz1):
            raise ValueError("Incorrect shape for coords: coords.shape must equal (nelt, ndims,  nx1 * ny1 * nz1)")
        self._coords = other.astype(self.float_type)
        self._set_rdcode()

    @FldDataBase.u.setter
    def u(self, other: np.ndarray):
        if self._readonly:
            raise AttributeError("FldDataMemmap in read-only mode does not support field assignment.")
        if other.size != 0 and other.shape != (self.nelt, self.ndims, self.nx1 * self.ny1 * self.nz1):
            raise ValueError("Incorrect shape for u: u.shape must equal (nelt, ndims, nx1 * ny1 * nz1)")
        self._u = other.astype(self.float_type)
        self._set_rdcode()

    @FldDataBase.p.setter
    def p(self, other: np.ndarray):
        if self._readonly:
            raise AttributeError("FldDataMemmap in read-only mode does not support field assignment.")
        if other.size != 0 and other.shape != (self.nelt, self.nx1 * self.ny1 * self.nz1,):
            raise ValueError("Incorrect shape for p: p.shape must equal (nelt * nx1 * ny1 * nz1,)")
        self._p = other.astype(self.float_type)
        self._set_rdcode()

    @FldDataBase.t.setter
    def t(self, other: np.ndarray):
        if self._readonly:
            raise AttributeError("FldDataMemmap in read-only mode does not support field assignment.")
        if other.size != 0 and other.shape != (self.nelt, self.nx1 * self.ny1 * self.nz1,):
            raise ValueError("Incorrect shape for t: t.shape must equal ``(nelt * nx1 * ny1 * nz1,)``")
        self._t = other.astype(self.float_type)
        self._set_rdcode()

    @FldDataBase.s.setter
    def s(self, other: np.ndarray):
        if self._readonly:
            raise AttributeError("FldDataMemmap in read-only mode does not support field assignment.")
        if other.size != 0 and (
                len(other.shape) != 3 or other.shape[1:] != (self.nelt, self.nx1 * self.ny1 * self.nz1)):
            raise ValueError(
                "Incorrect shape for s: s.shape must equal (x, nelt, nx1 * ny1 * nz1) for arbitrary number of scalars x")
        self._s = other.astype(self.float_type)
        self._set_rdcode()

    def make_hex(self, e):
        # For debugging
        nx = self.nx1   # Assume nx1 == ny1 == nz1
        gpt = lambda x, y, z: (e * nx**3) + (z * nx**2) + (y * nx) + x  # Get the gridpoint corresponding to an (x, y, z) coordinate

        # Start with vertices
        idx = [
            gpt(0, 0, 0),  # Vertex 0
            gpt(nx-1, 0, 0),  # Vertex 1
            gpt(nx-1, nx-1, 0),  # Vertex 2
            gpt(0, nx-1, 0), # Vertex 3
            gpt(0, 0, nx-1), # Vertex 4
            gpt(nx-1, 0, nx-1), # Vertex 5
            gpt(nx-1, nx-1, nx-1), # Vertex 6
            gpt(0, nx-1, nx-1), # Vertex 8
        ]

        # Edge 8
        idx.append(gpt(nx//2, 0, 0))
        # Edge 9
        idx.append(gpt(nx-1, nx//2, 0))
        # Edge 10
        idx.append(gpt(nx//2, nx-1, 0))
        # Edge 11
        idx.append(gpt(0, nx//2, 0))
        # Edge 12
        idx.append(gpt(nx//2, 0, nx-1))
        # Edge 13
        idx.append(gpt(nx-1, nx//2, nx-1))
        # Edge 14
        idx.append(gpt(nx//2, nx-1, nx-1))
        # Edge 15
        idx.append(gpt(0, nx//2, nx-1))
        # Edge 16
        idx.append(gpt(0, 0, nx//2))
        # Edge 17
        idx.append(gpt(nx-1, 0, nx//2))
        # Edge 18
        idx.append(gpt(nx-1, nx-1, nx//2))
        # Edge 19
        idx.append(gpt(0, nx-1, nx//2))

        hex = vtk.vtkQuadraticHexahedron()
        hex.GetPointIds().SetNumberOfIds(25)
        hex.GetPoints().SetNumberOfPoints(25)
        hex.Initialize()
        for i, x in enumerate(idx):
            hex.GetPointIds().SetId(i, x)
        return hex

    def make_lagrange_hex(self, e):
        nx = self.nx1   # Assume nx1 == ny1 == nz1
        gpt = lambda r, s, t: (e * nx**3) + r * nx**2 + s * nx + t  # Get the gridpoint corresponding to an (x, y, z) coordinate

        # From https://blog.kitware.com/wp-content/uploads/2018/09/Source_Issue_43.pdf
        # with some corrections due to inconsistencies in diagram (see notes below)

        # Start with vertices
        idx = [
            gpt(0, 0, 0),  # Vertex 0
            gpt(nx-1, 0, 0),  # Vertex 1
            gpt(nx-1, nx-1, 0),  # Vertex 2
            gpt(0, nx-1, 0), # Vertex 3
            gpt(0, 0, nx-1), # Vertex 4
            gpt(nx-1, 0, nx-1), # Vertex 5
            gpt(nx-1, nx-1, nx-1), # Vertex 6
            gpt(0, nx-1, nx-1), # Vertex 8
        ]

        # Edge 8,9
        for i in range(1, nx-1):
            idx.append(gpt(i, 0, 0))
        # Edge 10,11
        for i in range(1, nx-1):
            idx.append(gpt(nx-1, i, 0))
        # Edge 12,13
        for i in range(1, nx-1):
            idx.append(gpt(i, nx-1, 0))
        # Edge 14, 15
        for i in range(1, nx-1):
            idx.append(gpt(0, i, 0))
        # Edge 16, 17
        for i in range(1, nx-1):
            idx.append(gpt(i, 0, nx-1))
        # Edge 18, 19
        for i in range(1, nx-1):
            idx.append(gpt(nx-1, i, nx-1))
        # Edge 20, 21
        for i in range(1, nx-1):
            idx.append(gpt(i, nx-1, nx-1))
        # Edge 22, 23
        for i in range(1, nx-1):
            idx.append(gpt(0, i, nx-1))
        # Edge 24, 26
        for i in range(1, nx-1):
            idx.append(gpt(0, 0, i))
        # Edge 26, 27
        for i in range(1, nx-1):
            idx.append(gpt(nx-1, 0, i))

        # /****** Swapped these two edges vs blog ******
        # Edge 30, 31
        for i in range(1, nx-1):
            idx.append(gpt(0, nx-1, i))
        # Edge 28, 29
        for i in range(1, nx-1):
            idx.append(gpt(nx-1, nx-1, i))
        # **********************************************/

        # /****** Swapped these faces vs blog ***********
        # Face 40
        for t in range(1, nx-1):
            for s in range(1, nx-1):
                idx.append(gpt(0, s, t))
        # Face 44
        for t in range(1, nx-1):
            for s in range(1, nx-1):
                idx.append(gpt(nx-1, s, t))
        # Face 32
        for t in range(1, nx-1):
            for r in range(1, nx - 1):
                idx.append(gpt(r, 0, t))
        # Face 36
        for t in range(1, nx-1):
            for r in range(1, nx - 1):
                idx.append(gpt(r, nx-1, t))
        # **********************************************/

        # Face 48
        for s in range(1, nx-1):
            for r in range(1, nx-1):
                idx.append(gpt(r, s, 0))
        # Face 52
        for s in range(1, nx-1):
            for r in range(1, nx-1):
                idx.append(gpt(r, s, nx-1))

        # Interior
        for t in range(1, nx - 1):
            for s in range(1, nx-1):
                for r in range(1, nx - 1):
                    idx.append(gpt(r, s, t))

        hex = vtk.vtkLagrangeHexahedron()
        hex.GetPointIds().SetNumberOfIds(nx**3)
        hex.GetPoints().SetNumberOfPoints(nx**3)
        hex.Initialize()
        for i, x in enumerate(idx):
            hex.GetPointIds().SetId(i, x)
        return hex

    def plot(self):
        N = self.nelt
        n_gll = self.nx1 * self.ny1 * self.nz1

        # Setup the points

        points = vtk.vtkPoints()
        points.Allocate(N * n_gll)

        scalars = vtk.vtkDoubleArray()
        scalars.Allocate(N * n_gll)

        for e in range(N):
            for i in range(n_gll):
                pt = [self.coords[e,0,i], self.coords[e,1,i], self.coords[e,2,i]]
                points.InsertNextPoint(pt)
                scalars.InsertNextTuple1(self.t[e,i])

        # Setup the grid and cells

        hex_grid = vtk.vtkUnstructuredGrid()
        hex_grid.Allocate(N)

        for i in range(N):
            hex = self.make_lagrange_hex(i)
            hex_grid.InsertNextCell(hex.GetCellType(), hex.GetPointIds())
            print("\rProcessed {} / {} elements ...".format(i, N), end='')
        print(" done!")
        hex_grid.SetPoints(points)
        hex_grid.GetPointData().SetScalars(scalars)

        # Clipping:  https://lorensen.github.io/VTKExamples/site/Python/UnstructuredGrid/ClipUnstructuredGridWithPlane2/

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

        #mapper = vtk.vtkDataSetMapper()
        #mapper.SetInputData(hex_grid)
        #mapper.SetScalarRange(hex_grid.GetScalarRange())

        # Plot it!

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        # actor.GetProperty().SetRepresentationToWireframe()
        #actor.GetProperty().SetColor(colors.GetColor3d("Peacock"))
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
