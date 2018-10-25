#!/bin/sh

print_error_and_exit() {
  echo $1
  exit 127
}

./scripts/build_package.sh hlhdf               1 Ubuntu1604 || print_error_and_exit "Failed to build hlhdf" 
./scripts/build_package.sh bbufr               1 Ubuntu1604 || print_error_and_exit "Failed to build bbufr"
./scripts/build_package.sh rave                1 Ubuntu1604 || print_error_and_exit "Failed to build rave"
./scripts/build_package.sh bropo               1 Ubuntu1604 || print_error_and_exit "Failed to build bropo"
./scripts/build_package.sh beamb               1 Ubuntu1604 || print_error_and_exit "Failed to build beamb"
./scripts/build_package.sh baltrad-wrwp        1 Ubuntu1604 || print_error_and_exit "Failed to build baltrad-wrwp"
./scripts/build_package.sh baltrad-db          1 Ubuntu1604 || print_error_and_exit "Failed to build baltrad-db"
./scripts/build_package.sh baltrad-beast       1 Ubuntu1604 || print_error_and_exit "Failed to build baltrad-beast"
./scripts/build_package.sh baltrad-config      1 Ubuntu1604 || print_error_and_exit "Failed to build baltrad-config"
#./scripts/build_package.sh hdf-java   #  NO NEED FOR HDF-JAVA ON DEBIAN
./scripts/build_package.sh baltrad-node-tomcat 1 Ubuntu1604 || print_error_and_exit "Failed to build baltrad-node-tomcat"
./scripts/build_package.sh baltrad-dex         1 Ubuntu1604 || print_error_and_exit "Failed to build baltrad-dex"


