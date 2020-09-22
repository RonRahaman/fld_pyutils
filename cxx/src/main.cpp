//
// Created by Ronald Rahaman on 9/19/20.
//

#include "FldData.h"
#include "FldHeader.h"
#include <algorithm>
#include <iostream>
#include <string>

int main()
{
  std::string filename{ "/Users/ronald/repos/fld_pyutils/data/rod_short0.f00001" };

  // Header test
  // auto foo = fld::FldHeader<float, int>(filename);
  // std::cout << foo.Nelgt << std::endl;
  // std::cout << *std::min_element(foo.Glel.cbegin(), foo.Glel.cend()) << std::endl;
  // std::cout << *std::max_element(foo.Glel.cbegin(), foo.Glel.cend()) << std::endl;

  // Data test
  fld::FldData<float, int> bar(filename);
  std::cout << "Coords min/max: " << *std::min_element(bar.Coords.cbegin(), bar.Coords.cend())
            << ", " << *std::max_element(bar.Coords.cbegin(), bar.Coords.cend()) << std::endl;
  std::cout << "Velocity min/max: " << *std::min_element(bar.U.cbegin(), bar.U.cend()) << ", "
            << *std::max_element(bar.U.cbegin(), bar.U.cend()) << std::endl;
  std::cout << "Pressure min/max: " << *std::min_element(bar.P.cbegin(), bar.P.cend()) << ", "
            << *std::max_element(bar.P.cbegin(), bar.P.cend()) << std::endl;
  std::cout << "Temperature min/max: " << *std::min_element(bar.T.cbegin(), bar.T.cend()) << ", "
            << *std::max_element(bar.T.cbegin(), bar.T.cend()) << std::endl;
  std::cout << bar.U.size() << " " << bar.T.size() << " " << bar.T.size() << std::endl;
}
