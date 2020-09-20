#ifndef FLD_PYUTILS_CXX_SRC_FLDDATA_H
#define FLD_PYUTILS_CXX_SRC_FLDDATA_H

#include <string>

class FldData {
public:
  explicit FldData(std::string filename);

  std::size_t nx1;
  std::size_t ny1;
  std::size_t nz1;

};

#endif //FLD_PYUTILS_CXX_SRC_FLDDATA_H
