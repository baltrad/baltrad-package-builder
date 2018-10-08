#!/bin/sh

if [ $# -lt 3 ]; then
  echo "Usage: $0 <package name> <buildnr> <node_name>"
  exit 127
fi

CHANGELOG_MESSAGE="Autobuild"

PACKAGE_NAME=$1
BUILD_NUMBER=$2
NODE_NAME=$3
BUILD_NAME=$PACKAGE_NAME

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

  dch --distribution UNRELEASED --package $2 --newversion $3 "Autogenerated packaging"

  debuild -b -uc -us || exit 127
  
  #if [ "$4" = "true" ]; then
  #    sudo dpkg -i ../$2*_$3*.deb || exit 127
  #fi
  if [ ! -d ../../artifacts ]; then
    mkdir ../../artifacts || exit 127
  fi
  mv ../$2*_$3*.deb ../../artifacts/
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
  #First we need to create a source tarball. Remove the old one
  if [ -f "$RPM_TOP_DIR/SOURCES/$2-$3.tar.gz" ]; then
    \rm -f "$RPM_TOP_DIR/SOURCES/$2-$3.tar.gz"
  fi
  CFILES=`ls -1 "$1"/ | egrep '.conf$' | wc -l`
  if [ $CFILES -gt 0 ]; then
    cp -f "$1"/*.conf "$RPM_TOP_DIR/SOURCES/"
  fi
  CFILES=`ls -1 "$1"/ | egrep '.patch$' | wc -l`
  if [ $CFILES -gt 0 ]; then
    cp -f "$1"/*.patch "$RPM_TOP_DIR/SOURCES/"
  fi
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
  #if [ "$6" = "true" ]; then
  #  if [ "$RPM_PCK_DIR" != "" ]; then
  #    sudo rpm -Uvh "$RPM_PCK_DIR/$3*-$4-$5*.$RPM_ARCH_DIR.rpm"
  #  fi
  #fi
  if [ ! -d ../../artifacts ]; then
    mkdir ../../artifacts || exit 127
  fi
  if [ "$RPM_PCK_DIR" != "" ]; then
    mv "$RPM_PCK_DIR"/$3*-$4-$5*.$RPM_ARCH_DIR.rpm ../../artifacts/
  fi
}

if [ "$BUILD_NUMBER" = "" ]; then
  BUILD_NUMBER=1
fi

OS_VARIANT=`get_os_version`

echo "Building $BUILD_NAME-$PACKAGE_VERSION-$BUILD_NUMBER on $OS_VARIANT on node $NODE_NAME"

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
  prepare_and_build_debian "$PACKAGEDIR/$PACKAGE_NAME/debian" $BUILD_NAME $PACKAGE_VERSION-$BUILD_NUMBER $INSTALL_ARTIFACTS
elif [ "$OS_VARIANT" = "CentOS-7" ]; then
  echo "Redhat build"
  prepare_and_build_centos "$PACKAGEDIR/$PACKAGE_NAME/centos" "$PACKAGEDIR/$PACKAGE_NAME/$SPECFILE" $BUILD_NAME $PACKAGE_VERSION $BUILD_NUMBER $INSTALL_ARTIFACTS $CREATE_TAR_FROM_FOLDER
else
  echo "Unsupported build variant"  
fi


