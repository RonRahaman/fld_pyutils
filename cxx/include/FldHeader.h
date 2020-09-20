#ifndef FLD_PYUTILS_CXX_SRC_FLDHEADER_H
#define FLD_PYUTILS_CXX_SRC_FLDHEADER_H

#include <string>
#include <vector>
#include <fstream>
#include <iostream>

namespace fld {

template<typename floatTypeT, typename intTypeT>
class FldHeader
{
public:
  using FloatType = floatTypeT;
  using IntType = intTypeT;

  explicit FldHeader(const std::string &filename);

  std::size_t Nx1;
  std::size_t Ny1;
  std::size_t Nz1;
  std::size_t Nelt;
  std::size_t Nelgt;
  std::string Rdcode;
  double Time;
  int Iostep;
  int Fid0;
  int Nfileoo;
  double P0th;
  bool IfPressMesh;

  std::vector<IntType> Glel;
};

template <typename floatTypeT, typename intTypeT>
FldHeader<floatTypeT, intTypeT>::FldHeader(const std::string& filename)
{
  std::streampos binaryPos = 132;  // Position where binary portion of file begins
  float endianExpectVal = 6.54321f;  // Expected value for endianness test

  std::size_t floatSizeTest; // Used to test size of float type in file
  std::string pressMeshKey; // Used to determine if_press_mesh

  // The header is ASCII-encoded
  try
  {
    std::ifstream infile(filename);
    infile.exceptions(std::ifstream::failbit | std::ifstream::badbit);
    std::string scratch;      // Throwaway first token
    infile >> scratch >> floatSizeTest >> Nx1 >> Ny1 >> Nz1 >> Nelt >> Nelgt >> Time >> Iostep >>
           Fid0 >> Nfileoo >> Rdcode >> P0th >> pressMeshKey;
  }
  catch (std::ifstream::failure& e)
  {
    std::cerr << e.what() << ": Couldn't open or read fld.file in ASCII mode: " << filename
              << std::endl;
    throw e;
  }

  if (floatSizeTest != sizeof(FloatType))
  {
    // TODO: Handle different-sized floats.  Probably factory
    throw std::runtime_error("Error: .fld file " + filename + " has " + std::to_string(floatSizeTest) +
      "-byte floats, but the FldReader was instantiated to read " + std::to_string(sizeof(FloatType)) + "byte floats");
  }

  // The rest of the data is binary
  try
  {
    std::ifstream infile(filename, std::ifstream::binary);
    infile.seekg(binaryPos, std::ifstream::beg);

    // Test endianness.  TODO: Support non-natives endiannesses
    float endianTestVal;
    infile.read(reinterpret_cast<char*>(&endianTestVal), sizeof(float));
    if (endianTestVal != endianExpectVal) {
      throw std::runtime_error("Endianness of .fld file " + filename
                                 + " does not match endianness of current system.");
    }

    // Read Glel
    Glel.resize(Nelgt);
    infile.read(reinterpret_cast<char *>(Glel.data()), Nelgt * sizeof(IntType));
  }
  catch (std::ifstream::failure& e)
  {
    std::cerr << e.what() << ": Couldn't open or .fld file in binary mode: " << filename
              << std::endl;
    throw e;
  }
}

}

#endif // FLD_PYUTILS_CXX_SRC_FLDHEADER_H
