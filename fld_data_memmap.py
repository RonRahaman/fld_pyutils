from fld_data_base import FldDataBase
from fld_header import FldHeader
import numpy as np
import re
import vtk


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

    def make_hex(self, elem_id):
        n_gll = self.nx1 * self.ny1 * self.nz1

        hex = vtk.vtkLagrangeHexahedron()
        hex.GetPointIds().SetNumberOfIds(n_gll)
        hex.GetPoints().SetNumberOfPoints(n_gll)
        hex.Initialize()

        for i in range(n_gll):
            idx = elem_id * n_gll + i
            hex.GetPointIds().SetId(i, idx)

        return hex

    def plot(self):
        n_gll = self.nx1 * self.ny1 * self.nz1

        # Setup the points

        points = vtk.vtkPoints()
        points.Allocate(self.nelt * n_gll)

        for i in range(self.nelt):
            for j in range(n_gll):
                points.InsertPoint(i * n_gll + j, list(self.coords[i, :, j]))

        # Setup the grid and cells

        hex_grid = vtk.vtkUnstructuredGrid()
        hex_grid.Allocate(self.nelt)

        for i in range(self.nelt):
            hex = self.make_hex(i)
            hex_grid.InsertNextCell(hex.GetCellType(), hex.GetPointIds())
            print("\rProcessed {} / {} elements ...".format(i, self.nelt), end='')
        print(" done!")
        hex_grid.SetPoints(points)

        # Plot it!

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

        ren.ResetCamera()
        ren.GetActiveCamera().Azimuth(30)
        ren.GetActiveCamera().Elevation(20)
        ren.GetActiveCamera().Dolly(2.8)
        ren.GetActiveCamera().Zoom(5)
        ren.ResetCameraClippingRange()

        ren_win.Render()

        iren.Initialize()
        iren.Start()
