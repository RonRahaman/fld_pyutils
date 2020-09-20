//
// Created by Ronald Rahaman on 9/19/20.
//

#include "FldHeader.h"
#include <iostream>
#include <string>
#include <algorithm>

int main() {
  std::string filename{"/Users/ronald/repos/fld_pyutils/data/test0.f00001"};
  auto foo = fld::FldHeader<float, int>(filename);
  std::cout << foo.Nelgt << std::endl;
  std::cout << *std::min_element(foo.Glel.cbegin(), foo.Glel.cend()) << std::endl;
  std::cout << *std::max_element(foo.Glel.cbegin(), foo.Glel.cend()) << std::endl;
}
