#ifndef FLD_PYUTILS_CXX_SRC_FLDHEADER_H
#define FLD_PYUTILS_CXX_SRC_FLDHEADER_H

#include <fstream>
#include <iostream>
#include <regex>
#include <string>
#include <vector>

namespace fld
{

template <typename FloatT, typename IntT>
class FldHeader
{
public:
  explicit FldHeader(const std::string& filename);

  std::vector<std::string> RdcodeTokens() const;

  std::string Filename;
  std::size_t Nx1;
  std::size_t Ny1;
  std::size_t Nz1;
  std::size_t Nelt;
  std::size_t Nelgt;
  int Ndims;
  std::string Rdcode;
  double Time;
  int Iostep;
  int Fid0;
  int Nfileoo;
  double P0th;
  bool IfPressMesh = false;

  const std::streampos EndianTestBegin = 132; // Position where binary portion of file begins
  const std::streampos GlelBegin = 136;       // Position where glel begins
  std::streampos FieldsBegin;

  const float EndianExpectVal = 6.54321f; // Expected value for endianness test

  std::vector<IntT> Glel;
};

template <typename FloatT, typename IntT>
FldHeader<FloatT, IntT>::FldHeader(const std::string& filename)
  : Filename(filename)
{

  std::size_t floatSizeTest; // Used to test size of float type in file
  std::string pressMeshKey;  // Used to determine if_press_mesh

  // The header is ASCII-encoded
  try
  {
    std::ifstream infile(Filename);
    infile.exceptions(std::ifstream::failbit | std::ifstream::badbit);
    std::string scratch; // Throwaway first token
    infile >> scratch >> floatSizeTest >> Nx1 >> Ny1 >> Nz1 >> Nelt >> Nelgt >> Time >> Iostep >>
      Fid0 >> Nfileoo >> Rdcode >> P0th >> pressMeshKey;
  }
  catch (std::ifstream::failure& e)
  {
    std::cerr << e.what() << ": Couldn't open or read fld.file in ASCII mode: " << Filename
              << std::endl;
    throw e;
  }

  // Set number of dimensions
  Ndims = (Nz1 == 1) ? 2 : 3;

  // See if fld file has double or single precision data.  Usually float
  // TODO: Handle different-sized floats.  Probably factory
  if (floatSizeTest != sizeof(FloatT))
  {
    throw std::runtime_error("Error: .fld file " + Filename + " has " +
      std::to_string(floatSizeTest) + "-byte floats, but the FldReader was instantiated to read " +
      std::to_string(sizeof(FloatT)) + "byte floats");
  }

  // See if there's a pressure mesh
  if (pressMeshKey == "t" || pressMeshKey == "T")
  {
    throw std::runtime_error(
      "Error: .fld file " + Filename + "specifies if_press_mesh=F, but PnPn-2 is not supported.");
  }

  // The rest of the data is binary
  try
  {
    std::ifstream infile(Filename, std::ifstream::binary);

    // Test endianness.  TODO: Support non-natives endiannesses
    float endianTestVal;
    infile.seekg(EndianTestBegin, std::ifstream::beg);
    infile.read(reinterpret_cast<char*>(&endianTestVal), sizeof(float));
    if (endianTestVal != EndianExpectVal)
    {
      throw std::runtime_error(
        "Endianness of .fld file " + Filename + " does not match endianness of current system.");
    }

    // Read Glel
    Glel.resize(Nelgt);
    infile.seekg(GlelBegin, std::ifstream::beg);
    infile.read(reinterpret_cast<char*>(Glel.data()), Nelgt * sizeof(IntT));
  }
  catch (std::ifstream::failure& e)
  {
    std::cerr << e.what() << ": Couldn't open or .fld file in binary mode: " << Filename
              << std::endl;
    throw e;
  }

  // Finally, set beginning of field data
  FieldsBegin = GlelBegin + static_cast<std::streampos>(Nelgt * sizeof(IntT));
}

template <typename FloatT, typename IntT>
std::vector<std::string> FldHeader<FloatT, IntT>::RdcodeTokens() const
{
  std::vector<std::string> tokens;
  std::regex pattern("\\D\\d*");
  std::string sequence(Rdcode);

  std::regex_iterator<std::string::iterator> regIter(sequence.begin(), sequence.end(), pattern);
  std::regex_iterator<std::string::iterator> regEnd;
  while (regIter != regEnd)
  {
    tokens.push_back(regIter->str());
    ++regIter;
  }

  return tokens;
}

}

#endif // FLD_PYUTILS_CXX_SRC_FLDHEADER_H
