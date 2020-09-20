#ifndef FLD_PYUTILS_CXX_SRC_FLDDATA_H
#define FLD_PYUTILS_CXX_SRC_FLDDATA_H

#include "FldHeader.h"
#include <memory>
#include <regex>
#include <string>

namespace fld
{

template <typename floatTypeT, typename intTypeT>
class FldData
{
public:
  using floatType = floatTypeT;
  using intType = intTypeT;

  explicit FldData(const std::string& filename);
  const std::unique_ptr<FldHeader<floatType, intType>> Header;

  std::vector<intType> Coords;
  std::vector<floatType> U;
  std::vector<floatType> P;
  std::vector<floatType> T;
  std::vector<floatType> S;

  int Nscalars;
};

template <typename floatTypeT, typename intTypeT>
FldData<floatTypeT, intTypeT>::FldData(const std::string& filename)
  : Header(std::make_unique<FldHeader<floatTypeT, intTypeT>>(filename))
{
  auto tokens = Header->RdcodeTokens();
  try
  {
    std::ifstream infile(Header->Filename, std::ifstream::binary);
    infile.seekg(Header->FieldsBegin);
    for (const auto& tok : tokens)
    {
      // Coordinate data
      if (tok == "X" || tok == "x")
      {
        std::cout << "Located coordinates X" << std::endl;
        auto sz = Header->Nelt * Header->Ndims * Header->Nx1 * Header->Ny1 * Header->Nz1;
        Coords.resize(sz);
        infile.read(reinterpret_cast<char*>(Coords.data()), sz * sizeof(intType));
      }

      // Velocity field
      else if (tok == "U" || tok == "u")
      {
        std::cout << "Located velocity field U" << std::endl;
        auto sz = Header->Nelt * Header->Ndims * Header->Nx1 * Header->Ny1 * Header->Nz1;
        U.resize(sz);
        infile.read(reinterpret_cast<char*>(U.data()), sz * sizeof(floatType));
      }

      // Pressure Field
      else if (tok == "P" || tok == "p")
      {
        std::cout << "Located pressure field P" << std::endl;
        auto sz = Header->Nelt * Header->Nx1 * Header->Ny1 * Header->Nz1;
        P.resize(sz);
        infile.read(reinterpret_cast<char*>(P.data()), sz * sizeof(floatType));
      }

      // Temperature field
      else if (tok == "T" || tok == "t")
      {
        std::cout << "Located temperature field T" << std::endl;
        auto sz = Header->Nelt * Header->Nx1 * Header->Ny1 * Header->Nz1;
        T.resize(sz);
        infile.read(reinterpret_cast<char*>(T.data()), sz * sizeof(floatType));
      }

      // Passive scalars
      else if (tok[0] == 'S' || tok[0] == 's')
      {
        Nscalars = std::stoi(tok.substr(1));
        std::cout << "Located " << Nscalars << " scalar fields S" << std::endl;
        auto sz = Nscalars * Header->Nelt * Header->Nx1 * Header->Ny1 * Header->Nz1;
        S.resize(sz);
        infile.read(reinterpret_cast<char*>(S.data()), sz * sizeof(floatType));
      }
    }
  }
  catch (std::ifstream::failure& e)
  {
    std::cerr << e.what() << ": Couldn't open or .fld file in binary mode: " << Header->Filename
              << std::endl;
    throw e;
  }
}
}

#endif // FLD_PYUTILS_CXX_SRC_FLDDATA_H
