#!/bin/sh

print_error_and_exit() {
  echo $1
  exit 127
}
PKG_BUILD_NUMBER=1

STR=`echo $1 | egrep -e "^[0-9]+$"`
if [ "$STR" != "" ]; then
  PKG_BUILD_NUMBER=$1
else
  echo "Package number must be a digit"
  exit 127
fi

./scripts/build_package.sh hlhdf               $PKG_BUILD_NUMBER || print_error_and_exit "Failed to build hlhdf" 
./scripts/build_package.sh bbufr               $PKG_BUILD_NUMBER || print_error_and_exit "Failed to build bbufr"
./scripts/build_package.sh rave                $PKG_BUILD_NUMBER || print_error_and_exit "Failed to build rave"
./scripts/build_package.sh bropo               $PKG_BUILD_NUMBER || print_error_and_exit "Failed to build bropo"
./scripts/build_package.sh beamb               $PKG_BUILD_NUMBER || print_error_and_exit "Failed to build beamb"
./scripts/build_package.sh baltrad-wrwp        $PKG_BUILD_NUMBER || print_error_and_exit "Failed to build baltrad-wrwp"
./scripts/build_package.sh baltrad-db          $PKG_BUILD_NUMBER || print_error_and_exit "Failed to build baltrad-db"
./scripts/build_package.sh baltrad-beast       $PKG_BUILD_NUMBER || print_error_and_exit "Failed to build baltrad-beast"
./scripts/build_package.sh baltrad-config      $PKG_BUILD_NUMBER || print_error_and_exit "Failed to build baltrad-config"
./scripts/build_package.sh hdf-java            $PKG_BUILD_NUMBER || print_error_and_exit "Failed to build hdf-java"
./scripts/build_package.sh baltrad-node-tomcat $PKG_BUILD_NUMBER || print_error_and_exit "Failed to build baltrad-node-tomcat"
./scripts/build_package.sh baltrad-dex         $PKG_BUILD_NUMBER || print_error_and_exit "Failed to build baltrad-dex"


