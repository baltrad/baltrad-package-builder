#!/bin/bash

print_error_and_exit() {
  echo $1
  exit 127
}

# Brief usage
usage_brief() {
  echo "Usage: `basename $0` <buildnr> [<options>]"
}

# Usage
usage() {
  echo "Usage: `basename $0` <buildnr> [<options>]"
  echo "<buildnr>      - the build number, should always be provided"
  echo "Options:"
  echo "--builder-name=<name>   - Name of the node building this packages if it's relevant somehow'"
  echo "--version=<version>     - Version that all packages (except hlhdf) should get. Should be in format, <major>.<minor>.<patch>." 
  echo "                          Will override the setting in respective packages package.ini file"
  echo "--hlhdf-version=<version> - If hlhdf version shouldn't be default."
  echo ""
  echo "--artifacts=<loc>       - The directory where the artifacts should be placed (also support scp if "
  echo "                          the target location accepts copying without a password). In that case,"
  echo "                          the specified location should be like scp:<user>@<host>:<loc>"
  echo "                          If not specifying this the packages will be placed under "
  echo "                          packages/<package>/artifacts/<OS build>"
  echo "--build-log=<loc>       - The directory where the build log resides (if any)"
  echo "--rebuild-pippackages   - Rebuilds the pip-packages"
}

get_os_version()
{
  if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=`echo $NAME | sed -e "s/Linux//g" | sed -e"s/^[[:space:]]*//g" | sed -e's/[[:space:]]*$//g'`
    VER=$VERSION_ID
    if [ "$NAME" = "Rocky Linux" -o "$NAME" = "Red Hat Enterprise" ]; then
      VER=`echo $VER | cut -d'.' -f1`
    fi   
  elif type lsb_release >/dev/null 2>&1; then
    OS=$(lsb_release -si)
    VER=$(lsb_release -sr)
  elif [ -f /etc/lsb-release ]; then
    . /etc/lsb-release
    OS=$DISTRIB_ID
    VER=$DISTRIB_RELEASE
  elif [ -f /etc/debian_version ]; then
    OS=Debian
    VER=$(cat /etc/debian_version)
  elif [ -f /etc/redhat-release ]; then
    OS=`cat /etc/redhat-release | cut -d' ' -f1`
    VER=`cat /etc/redhat-release | cut -d' ' -f4 | cut -d'.' -f1`
  else
    OS=$(uname -s)
    VER=$(uname -r)
  fi
  echo "$OS-$VER"
}

if [ $# -lt 1 ]; then
  usage_brief $0
  exit 127
fi

PKG_BUILD_NUMBER=auto

BUILDER_NAME=
BALTRAD_VERSION=
HLHDF_VERSION=
ARTIFACTS=
OPT_INSTALL_ARTIFACTS=
REBUILD_PIPPACKAGES=no
BUILD_LOG=
DOCKER_BUILD=

for arg in $*; do
  case $arg in
    --help)
      usage $0
      exit 0
      ;;
    *) ;;
  esac
done

STR=`echo $1 | egrep -e "^[0-9]+$"`
if [ "$STR" != "" -o "$1" = "auto" ]; then
  PKG_BUILD_NUMBER=$1
else
  echo "Package number must be a digit"
  exit 127
fi
shift;

for arg in $*; do
  case $arg in
    --builder-name=*)
      BUILDER_NAME=`echo $arg | sed 's/[-a-zA-Z0-9]*=//'`
      ;;
    --version=*)
      BALTRAD_VERSION=`echo $arg | sed 's/[-a-zA-Z0-9]*=//'`
      ;;
    --hlhdf-version=*)
      HLHDF_VERSION=`echo $arg | sed 's/[-a-zA-Z0-9]*=//'`
      ;;
    --artifacts=*)
      ARTIFACTS=`echo $arg | sed 's/[-a-zA-Z0-9]*=//'`
      ;;
    --rebuild-pippackages)
      REBUILD_PIPPACKAGES=yes
      ;;
    --build-log=*)
      BUILD_LOG=`echo $arg | sed 's/[-a-zA-Z0-9]*=//'`
      ;;
    --docker=*)
      DOCKER_BUILD=`echo $arg | sed 's/--docker=//'`
      ;;      
    --help)
      usage $0
      exit 0
      ;;      
    *)
      echo "Unknown option or command: $arg"
      usage_brief $0
      exit 127
      ;;      
  esac
done

HLHDF_OPT_STR=
BALTRAD_OPT_STR=
BALTRAD_NO_VERSION_OPT_STR=
OS_VERSION=`get_os_version`

if [ "$BUILDER_NAME" != "" ]; then
  HLHDF_OPT_STR="$HLHDF_OPT_STR --builder-name=$BUILDER_NAME"
  BALTRAD_OPT_STR="$BALTRAD_OPT_STR --builder-name=$BUILDER_NAME"
  BALTRAD_NO_VERSION_OPT_STR="$BALTRAD_NO_VERSION_OPT_STR --builder-name=$BUILDER_NAME"
fi

if [ "$BALTRAD_VERSION" != "" ]; then
  BALTRAD_OPT_STR="$BALTRAD_OPT_STR --version=$BALTRAD_VERSION"
fi

if [ "$HLHDF_VERSION" != "" ]; then
  HLHDF_OPT_STR="$HLHDF_OPT_STR --version=$HLHDF_VERSION"
fi

if [ "$ARTIFACTS" != "" ]; then
  HLHDF_OPT_STR="$HLHDF_OPT_STR --artifacts=$ARTIFACTS"
  BALTRAD_OPT_STR="$BALTRAD_OPT_STR --artifacts=$ARTIFACTS"
  BALTRAD_NO_VERSION_OPT_STR="$BALTRAD_NO_VERSION_OPT_STR --artifacts=$ARTIFACTS"
fi

if [ "$BUILD_LOG" != "" ]; then
  HLHDF_OPT_STR="$HLHDF_OPT_STR --build-log=$BUILD_LOG"
  BALTRAD_OPT_STR="$BALTRAD_OPT_STR --build-log=$BUILD_LOG"
  BALTRAD_NO_VERSION_OPT_STR="$BALTRAD_NO_VERSION_OPT_STR  --build-log=$BUILD_LOG"
fi

if [ "$DOCKER_BUILD" != "" ]; then
  HLHDF_OPT_STR="$HLHDF_OPT_STR --docker=$DOCKER_BUILD"
  BALTRAD_OPT_STR="$BALTRAD_OPT_STR --docker=$DOCKER_BUILD"
  BALTRAD_NO_VERSION_OPT_STR="$BALTRAD_NO_VERSION_OPT_STR --docker=$DOCKER_BUILD"
fi

#if [[ "$OS_VERSION" != "Ubuntu-"* ]]; then
#  PIPARGS="--install"
#  if [ "$REBUILD_PIPPACKAGES" != "no" ]; then
#    PIPARGS="$PIPARGS --rebuild"
#  fi
#  if [ "$ARTIFACTS" != "" ]; then
#    PIPARGS="$PIPARGS --artifacts=$ARTIFACTS"
#  fi
#  if [ "$DOCKER_BUILD" != "" ]; then
#    PIPARGS="$PIPARGS --docker=$DOCKER_BUILD"
#  fi
#  ./pip-artifacts/create_3p_packages.sh $PIPARGS || print_error_and_exit "Failure during pip package build step"
#fi

#echo "OS_VERSION=$OS_VERSION"

#if [ "$OS_VERSION" = "Red Hat Enterprise-8" -o "$OS_VERSION" = "CentOS-8" -o "$DOCKER_BUILD" = "CentOS-8" -o "$DOCKER_BUILD" = "RedHat-8" -o "$OS_VERSION" = "CentOS Stream-8" -o "$OS_VERSION" = "Rocky-8" ]; then
#  ./scripts/build_package.sh proj49-blt        $PKG_BUILD_NUMBER $BALTRAD_NO_VERSION_OPT_STR || print_error_and_exit "Failed to build proj49-blt"
#fi

#if [ "$OS_VERSION" = "Red Hat Enterprise-8" -o "$OS_VERSION" = "CentOS-8" -o "$DOCKER_BUILD" = "CentOS-8" -o "$DOCKER_BUILD" = "RedHat-8" -o "$OS_VERSION" = "CentOS Stream-8" -o "$OS_VERSION" = "Rocky-8"  -o "$OS_VERSION" = "Rocky-9" -o "$OS_VERSION" = "Red Hat Enterprise-9.0" ]; then
#  ./scripts/build_package.sh baltrad-base        $PKG_BUILD_NUMBER $BALTRAD_OPT_STR || print_error_and_exit "Failed to build baltrad-base"
#  ./scripts/build_package.sh baltrad-crypto      $PKG_BUILD_NUMBER $BALTRAD_OPT_STR || print_error_and_exit "Failed to build baltrad-crypto"
#fi

./scripts/build_package.sh hlhdf               $PKG_BUILD_NUMBER $HLHDF_OPT_STR || print_error_and_exit "Failed to build hlhdf" 
./scripts/build_package.sh bbufr               $PKG_BUILD_NUMBER $BALTRAD_OPT_STR || print_error_and_exit "Failed to build bbufr"
./scripts/build_package.sh rave                $PKG_BUILD_NUMBER $BALTRAD_OPT_STR || print_error_and_exit "Failed to build rave"
exit 0
./scripts/build_package.sh bropo               $PKG_BUILD_NUMBER $BALTRAD_OPT_STR || print_error_and_exit "Failed to build bropo"
./scripts/build_package.sh beamb               $PKG_BUILD_NUMBER $BALTRAD_OPT_STR || print_error_and_exit "Failed to build beamb"
./scripts/build_package.sh baltrad-ppc         $PKG_BUILD_NUMBER $BALTRAD_OPT_STR || print_error_and_exit "Failed to build baltrad-ppc"
./scripts/build_package.sh baltrad-wrwp        $PKG_BUILD_NUMBER $BALTRAD_OPT_STR || print_error_and_exit "Failed to build baltrad-wrwp"
./scripts/build_package.sh baltrad-db          $PKG_BUILD_NUMBER $BALTRAD_OPT_STR || print_error_and_exit "Failed to build baltrad-db"
./scripts/build_package.sh baltrad-beast       $PKG_BUILD_NUMBER $BALTRAD_OPT_STR || print_error_and_exit "Failed to build baltrad-beast"
./scripts/build_package.sh baltrad-config      $PKG_BUILD_NUMBER $BALTRAD_OPT_STR || print_error_and_exit "Failed to build baltrad-config"
./scripts/build_package.sh baltrad-exchange      $PKG_BUILD_NUMBER $BALTRAD_OPT_STR || print_error_and_exit "Failed to build baltrad-exchange"

if [ "$OS_VERSION" = "CentOS-7" -o "$DOCKER_BUILD" = "CentOS-7" ]; then
  ./scripts/build_package.sh hdf-java            $PKG_BUILD_NUMBER $BALTRAD_NO_VERSION_OPT_STR || print_error_and_exit "Failed to build hdf-java"
fi

./scripts/build_package.sh baltrad-node-tomcat $PKG_BUILD_NUMBER $BALTRAD_NO_VERSION_OPT_STR || print_error_and_exit "Failed to build baltrad-node-tomcat"
./scripts/build_package.sh baltrad-dex         $PKG_BUILD_NUMBER $BALTRAD_OPT_STR || print_error_and_exit "Failed to build baltrad-dex"
./scripts/build_package.sh baltrad-viewer      $PKG_BUILD_NUMBER $BALTRAD_OPT_STR || print_error_and_exit "Failed to build baltrad-viewer"


