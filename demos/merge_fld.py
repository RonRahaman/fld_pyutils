import numpy as np
from fld_data import FldData
from fld_data_memmap import FldDataMemmap
import time

# ============================================================================
# Inputs
# `shifts` is shaped to allow array broadcasting.  So something like this:
# >>> shifts = [np.array([i * 2., 0., 0.]).reshape(1, 3, 1) for i in range(3)]
# Will produce this:
# >>> shifts
# [array([[[0.],
#          [0.],
#          [0.]]]),
#  array([[[2.],
#          [0.],
#          [0.]]]),
#  array([[[4.],
#          [0.],
#          [0.]]])]
# This means that:
# * fld file 0 will have its x-coords shifted by 0.0
# * fld file 1 will have its x-coords shifted by 2.0
# * fld file 2 will have its x coords shifted by 4.0
# ============================================================================

fld_files = ['/Users/rahaman/output/localq-longrod-nek5000-1K-steps-20K-particles/rod_l0.f00006',
             '/Users/rahaman/output/localq-longrod-nek5000-1K-steps-20K-particles/rod_l0.f00006',
             '/Users/rahaman/output/localq-longrod-nek5000-1K-steps-20K-particles/rod_l0.f00006']
shifts = [np.array([i * 2., 0., 0.]).reshape(1, 3, 1) for i in range(len(fld_files))]

# ============================================================================
# Don't need to change anything below this
# ============================================================================

starttime = time.time()

fld_objs = [FldDataMemmap.fromfile(f) for f in fld_files]

nelgt = sum(f.nelgt for f in fld_objs)
nx1 = fld_objs[0].nx1
ny1 = nx1
nz1 = nx1
nelt = sum(f.nelt for f in fld_objs)
glel = np.arange(start=1, stop=nelgt + 1)
merged_coords = np.concatenate([f.coords + s for f, s in zip(fld_objs, shifts)])
merged_u = np.concatenate([f.u for f in fld_objs])
merged_p = np.concatenate([f.p for f in fld_objs])
merged_t = np.concatenate([f.t for f in fld_objs])

merged_fld = FldData.fromvalues(
    nelgt=nelgt,
    nelt=nelt,
    nx1=nx1,
    ny1=ny1,
    nz1=nz1,
    glel=glel,
    coords=merged_coords,
    u=merged_u,
    p=merged_p,
    t=merged_t
)

merged_fld.tofile('merged0.f00001')

endtime = time.time()
print('time used: {} s'.format(endtime - starttime))
