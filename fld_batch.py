from fld_data_memmap import FldDataMemmap
import glob

class FldBatch:

    def __init__(self, case: str):
        self._case = case

    def visnek(self):
        glob_dict = {
            f"{self._case}.fld[0-9][0-9]*" : f"{self._case}.fld%02d",
            f"A0/{self._case}0.f[0-9][0-9][0-9][0-9][0-9]": f"A%01d/{self._case}%01d.f%05d",
            f"{self._case}00.f[0-9][0-9][0-9][0-9][0-9]": f"A%01d/{self._case}%01d.f%05d",
            f"A00/{self._case}00.f[0-9][0-9][0-9][0-9][0-9]": f"A%02d/{self._case}%02d.f%05d",
            f"{self._case}000.f[0-9][0-9][0-9][0-9][0-9]": f"{self._case}%03d.f%05d",
            f"A000/{self._case}000.f[0-9][0-9][0-9][0-9][0-9]": f"A%03d/{self._case}%03d.f%05d",
            f"A0000/{self._case}0000.f[0-9][0-9][0-9][0-9][0-9]": f"A%04d/{self._case}%04d.f%05d",
            f"{self._case}0.f[0-9][0-9][0-9][0-9][0-9]": f"{self._case}%01d.f%05d",
        }

        template = ""
        nsteps = 0
        for p, t in glob_dict.items():
            files = glob.glob(p)
            if files:
                template = t
                nsteps = len(files)
                break

        if template:
            contents = f"filetemplate: {template}\nfirsttimestep: 1\nnumtimesteps: {nsteps}\n"
            with open(f"{self._case}.nek5000", "w") as f:
                f.write(contents)
        else:
            raise FileNotFoundError("Could not find any field files with a valid pattern")

if __name__ == "__main__":
