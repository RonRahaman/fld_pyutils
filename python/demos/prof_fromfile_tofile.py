from fld_data import FldData
from fld_data_memmap import FldDataMemmap
import tracemalloc

tracemalloc.start()

d1 = FldData.fromfile('data/test0.f00001')
d1.tofile('fld_data0.f00001')
d2 = FldData.fromfile('fld_data0.f00001')
snapshot1 = tracemalloc.take_snapshot()

top_stats_1 = snapshot1.statistics('lineno')
print("[ Top 10 in FldData]")
for stat in top_stats_1[:10]:
    print(stat)

tracemalloc.stop()

tracemalloc.start()

d3 = FldDataMemmap.fromfile('data/test0.f00001', mode="r")
d3.tofile('fld_data_memmap0.f00001')
d4 = FldDataMemmap.fromfile('fld_data_memmap0.f00001')
snapshot2 = tracemalloc.take_snapshot()

top_stats_2 = snapshot2.statistics('lineno')
print("[ Top 10 in FldDataMemmap]")
for stat in top_stats_2[:10]:
    print(stat)
