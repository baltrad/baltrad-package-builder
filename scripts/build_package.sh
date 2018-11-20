#!/bin/sh

# Brief usage
usage_brief() {
  echo "Usage: `basename $0` <package name> <buildnr> [<options>]"
}

# Usage
usage() {
  echo "Usage: `basename $0` <package name> <buildnr> [<options>]"
  echo "<package name> - the name of the package to be built, e.g. bbufr, rave, baltrad-db ...."
  echo "<buildnr>      - the build number, should always be provided"
  echo "Options:"
  echo "--builder-name=<name>   - Name of the node building this packages if it's relevant somehow'"
  echo "--version=<version>     - Version that the packages should get. Should be in format, <major>.<minor>.<patch>." 
  echo "                          Will override the setting in respective packages package.ini file"
  echo "--artifacts=<loc>       - The directory where the artifacts should be placed (can also support scp if "
  echo "                          specifying scp: like usual with either user / pwd or that the current user is"
  echo "                          allowed to scp without pwd question). If not specifying this the packages will"
  echo "                          be placed under packages/<package>/artifacts/<OS build>"
  echo "--install-artifacts=true|false  - If the build artifacts should be installed or not. Default is to use "
  echo "                                  the package.ini setting, but usually true is a good choice since"
  echo "                                  packages built after might have dependencies to this artifact"
}

if [ $# -lt 2 ]; then
  exit 127
fi

PACKAGE_NAME=$1
BUILD_NUMBER=$2
BUILD_NAME=$PACKAGE_NAME
BUILDER_NAME=
RELEASE_VERSION=
ARTIFACTS=
OPT_INSTALL_ARTIFACTS=

shift;shift

for arg in $*; do
  case $arg in
    --builder-name=*)
      BUILDER_NAME=`echo $arg | sed 's/[-a-zA-Z0-9]*=//'`
      ;;
    --version=*)
      RELEASE_VERSION=`echo $arg | sed 's/[-a-zA-Z0-9]*=//'`
      ;;
    --artifacts=*)
      ARTIFACTS=`echo $arg | sed 's/[-a-zA-Z0-9]*=//'`
      ;;
    --install-artifacts=*)
      OPT_INSTALL_ARTIFACTS=`echo $arg | sed 's/[-a-zA-Z0-9]*=//'`
      if [ "$OPT_INSTALL_ARTIFACTS" != "true" -a "$OPT_INSTALL_ARTIFACTS" != "false" ]; then
        echo "--install-artifacts must be either true or false"
        exit 127
      fi
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

CHANGELOG_MESSAGE="Autobuild"

if [ ! -f packages/$PACKAGE_NAME/package.ini ]; then
  echo "No package named $PACKAGE_NAME"
  exit 127
fi

PACKAGE_VERSION=`cat packages/$PACKAGE_NAME/package.ini | egrep -e "^pkg_version" | sed -e"s/pkg_version=//g"`
GIT_URI=`cat packages/$PACKAGE_NAME/package.ini | egrep -e "^git_uri" | sed -e"s/git_uri=//g"`
TAR_BALL=`cat packages/$PACKAGE_NAME/package.ini | egrep -e "^tar_ball" | sed -e"s/tar_ball=//g"`
TAR_STRIP_ROOT=`cat packages/$PACKAGE_NAME/package.ini | egrep -e "^tar_strip_root" | sed -e"s/tar_strip_root=//g"`
SPECFILE=$PACKAGENAME/`cat packages/$PACKAGE_NAME/package.ini | egrep -e "^spec_file" | sed -e"s/spec_file=//g"`
INSTALL_ARTIFACTS=`cat packages/$PACKAGE_NAME/package.ini | egrep -e "^install_artifacts" | sed -e"s/install_artifacts=//g"`
TBUILD_NAME=`cat packages/$PACKAGE_NAME/package.ini | egrep -e "^pkg_name" | sed -e"s/pkg_name=//g"`
RPM_ARTIFACTS=`cat packages/$PACKAGE_NAME/package.ini | egrep -e "^rpm_artifacts" | sed -e "s/rpm_artifacts=//g"`

if [ "$TBUILD_NAME" != "" ]; then
  BUILD_NAME=$TBUILD_NAME
fi

if [ "$PACKAGE_VERSION" = "" -o "$INSTALL_ARTIFACTS" = "" ]; then
  echo "Could not extract information from packages/$PACKAGE_NAME/package.ini"
  exit 127
fi

if [ "$GIT_URI" = "" -a "$TAR_BALL" = "" ]; then
  echo "Could not extract information from packages/$PACKAGE_NAME/package.ini"
  exit 127
fi

if [ "$GIT_URI" != "" -a "$TAR_BALL" != "" ]; then
  echo "Can not specify both tar_ball and git_uri in packages/$PACKAGE_NAME/package.ini"
  exit 127
fi

if [ "$RELEASE_VERSION" != "" ]; then
  PACKAGE_VERSION=$RELEASE_VERSION
fi

if [ "$OPT_INSTALL_ARTIFACTS" != "" ]; then
  INSTALL_ARTIFACTS=$OPT_INSTALL_ARTIFACTS
fi

SCRIPTDIR=`dirname $(python -c "import os; print(os.path.abspath(\"$0\"))")`
PACKAGEDIR=$(dirname $SCRIPTDIR)/packages

get_os_version()
{
  if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=`echo $NAME | sed -e "s/Linux//g" | sed -e"s/^[[:space:]]*//g" | sed -e's/[[:space:]]*$//g'`
    VER=$VERSION_ID
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

prepare_and_build_debian()
{
  if [ -d "debian" ]; then
    \rm -fr "debian"
  fi
  cp -r "$1" . || exit 127

  OVERWRITE_FILES=`ls -1 "$1" | egrep -e "\.$5\\$"`
  if [ "$OVERWRITE_FILES" != "" ]; then
    for f in $OVERWRITE_FILES; do
      wo=`echo $f | sed -e "s/.$5\\$//g"`
      echo "Overwriting $wo with $1/$f, standing in `pwd`"
      cp -f "$1/$f" ./debian/$wo
    done
  fi

  dch --distribution UNRELEASED --package $2 --newversion $3 "Autogenerated packaging"

  debuild -b -uc -us || exit 127
  
  if [ "$4" = "true" ]; then
      sudo dpkg -i ../$2*_$3*.deb || exit 127
  fi
  if [ ! -d ../../artifacts/$5 ]; then
    mkdir ../../artifacts/$5 || exit 127
  fi
  mv ../$2*_$3*.deb ../../artifacts/$5/
}

prepare_and_build_centos()
{
  if [ ! -z "${RPM_ROOT}" ]; then
    RPM_TOP_DIR="${RPM_ROOT}"
  else
    RPM_TOP_DIR=`rpmbuild --eval '%_topdir'`
  fi
  RPM_ARCH_DIR=`rpmbuild --eval '%_arch'`
  RPM_PCK_DIR=`rpmbuild --eval '%_rpmdir/%_arch'`
  RPM_PCK_NOARCH_DIR=`rpmbuild --eval '%_rpmdir/noarch'`
  #First we need to create a source tarball. Remove the old one
  if [ -f "$RPM_TOP_DIR/SOURCES/$2-$3.tar.gz" ]; then
    \rm -f "$RPM_TOP_DIR/SOURCES/$2-$3.tar.gz"
  fi
  BNAME=`basename $2`
  FILES=`ls -1 "$1"/ | grep -v "$BNAME"`
  for f in $FILES; do
    cp "$1/$f" "$RPM_TOP_DIR/SOURCES/"
  done

  #HOW DO WE DETERMINE BUILDROOT? NOW, just fake it...
  if [ "$7" = "false" ]; then # If not tar ball should be created from folder, it must be a git archive
    git archive --format="tar.gz" --prefix="$3-$4/" master -o "$RPM_TOP_DIR/SOURCES/$3-$4.tar.gz"
    if [ $? -ne 0 ]; then
      echo "Failed to create source archive..."
      exit 127
    fi
  else
    cd ..
    tar -cvzf "$RPM_TOP_DIR/SOURCES/$3-$4.tar.gz" "$3"
    cd "$3"
  fi
  rpmbuild --define="version $4" --define "snapshot $5" -v -ba "$2" || exit 127

  if [ ! -d ../../artifacts/$8 ]; then
    mkdir -p ../../artifacts/$8 || exit 127
  fi
  
  if [ "$RPM_ARTIFACTS" != "" ]; then
    RPMS_TOPDIR=`rpmbuild --eval '%_rpmdir'`
    RPMS_TO_INSTALL=
    for X in $RPM_ARTIFACTS; do
      fname=`echo $X | sed -e "s/<buildver>/$PACKAGE_VERSION-$BUILD_NUMBER/g"`
      FILES=`ls -1 $RPMS_TOPDIR/$fname`
      for f in $FILES; do
        cp "$f" ../../artifacts/$8/
        RPMS_TO_INSTALL="$RPMS_TO_INSTALL ../../artifacts/$8/`basename $f`"
      done
    done
    if [ "$RPMS_TO_INSTALL" != "" ]; then
      echo "Installing $RPMS_TO_INSTALL"
      sudo rpm --force -Uvh $RPMS_TO_INSTALL
    fi
  else
    if [ "$6" = "true" ]; then
      if [ "$RPM_PCK_DIR" != "" ]; then
        # Use --force to be able to use same pck-number
        sudo rpm --force -Uvh "$RPM_PCK_DIR/$3*-$4-$5*.$RPM_ARCH_DIR.rpm"
      fi
    fi
    if [ "$RPM_PCK_DIR" != "" ]; then
      mv "$RPM_PCK_DIR"/$3*-$4-$5*.$RPM_ARCH_DIR.rpm ../../artifacts/$8/ >> /dev/null 2>&1
    fi
    if [ "$RPM_PCK_NOARCH_DIR" != "" ]; then
      mv "$RPM_PCK_NOARCH_DIR"/$3*-$4-$5*.noarch.rpm ../../artifacts/$8/ >> /dev/null 2>&1
    fi
  fi
}

if [ "$BUILD_NUMBER" = "" ]; then
  BUILD_NUMBER=1
fi

OS_VARIANT=`get_os_version`

if [ "$BUILDER_NAME" != "" ]; then
  echo "Building $BUILD_NAME-$PACKAGE_VERSION-$BUILD_NUMBER for $OS_VARIANT on node $BUILDER_NAME"
else
  echo "Building $BUILD_NAME-$PACKAGE_VERSION-$BUILD_NUMBER for $OS_VARIANT"
fi

cd packages/$PACKAGE_NAME

# If tar ball, then always remove previous build
if [ "$TAR_BALL" != "" ]; then
  if [ -d "build/$BUILD_NAME" ]; then
    \rm -fr "build/$BUILD_NAME" || exit 127
  fi
fi

if [ ! -d build/$BUILD_NAME ]; then
  if [ ! -d build ]; then
    mkdir build || exit 127
  fi
  cd build || exit 127
  if [ "$TAR_BALL" != "" ]; then
    mkdir $BUILD_NAME || exit 127
    if [ "$TAR_STRIP_ROOT" = "true" ]; then
      tar -xzf "../$TAR_BALL" --strip 1 --directory $BUILD_NAME || exit 127
    else
      tar -xzf "../$TAR_BALL" --directory $BUILD_NAME || exit 127
    fi 
  else
    git clone $GIT_URI $BUILD_NAME || exit 127
  fi
  cd $BUILD_NAME
else
  cd build/$BUILD_NAME
  git checkout . || exit 127 # REMOVE ALL OLD STUFF
  git checkout master || exit 127
  git pull || exit 127
fi
CREATE_TAR_FROM_FOLDER=false
if [ "$TAR_BALL" != "" ]; then
  CREATE_TAR_FROM_FOLDER=true
fi

if [ "$OS_VARIANT" = "Ubuntu-16.04" -o "$OS_VARIANT" = "Ubuntu-18.04" ]; then
  echo "Debian build"
  prepare_and_build_debian "$PACKAGEDIR/$PACKAGE_NAME/debian" $BUILD_NAME $PACKAGE_VERSION-$BUILD_NUMBER $INSTALL_ARTIFACTS $OS_VARIANT
  exit 0
elif [ "$OS_VARIANT" = "CentOS-7" ]; then
  echo "Redhat build"
  prepare_and_build_centos "$PACKAGEDIR/$PACKAGE_NAME/centos" "$PACKAGEDIR/$PACKAGE_NAME/$SPECFILE" $BUILD_NAME $PACKAGE_VERSION $BUILD_NUMBER $INSTALL_ARTIFACTS $CREATE_TAR_FROM_FOLDER $OS_VARIANT
  exit 0
else
  echo "Unsupported build variant $OS_VARIANT"
  exit 127  
fi


