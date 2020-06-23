#!/bin/bash

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
  echo "--artifacts=<loc>       - The directory where the artifacts should be placed (also support scp if "
  echo "                          the target location accepts copying without a password). In that case,"
  echo "                          the specified location should be like scp:<user>@<host>:<loc>"
  echo "                          If not specifying this the packages will be placed under "
  echo                            "packages/<package>/artifacts/<OS build>"
  echo "--install-artifacts=true|false  - If the build artifacts should be installed or not. Default is to use "
  echo "                                  the package.ini setting, but usually true is a good choice since"
  echo "                                  packages built after might have dependencies to this artifact"
  echo "--build-log=<log>       - The file the current package with associated tag should be written to."
  echo                            If not specified, no history will be written. This is useful for generating"
  echo                            release notes or deployment information."
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
BUILD_LOG=

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
    --build-log=*)
      BUILD_LOG=`echo $arg | sed 's/[-a-zA-Z0-9]*=//'`
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

if [ ! -f packages/$PACKAGE_NAME/package.ini ]; then
  echo "No package named $PACKAGE_NAME"
  exit 127
fi

PACKAGE_VERSION=`cat packages/$PACKAGE_NAME/package.ini | egrep -e "^pkg_version" | sed -e"s/pkg_version=//g"`
GIT_URI=`cat packages/$PACKAGE_NAME/package.ini | egrep -e "^git_uri" | sed -e"s/git_uri=//g"`
GIT_PKG_NBR=`cat packages/$PACKAGE_NAME/package.ini | egrep -e "^git_pkg_nbr" | sed -e"s/git_pkg_nbr=//g"`
GIT_PKG_NO_EXTRACT=`cat packages/$PACKAGE_NAME/package.ini | egrep -e "^git_pkg_no_extract" | sed -e"s/git_pkg_no_extract=//g"`
GIT_PKG_OFFSET=`cat packages/$PACKAGE_NAME/package.ini | egrep -e "^git_pkg_offset" | sed -e"s/git_pkg_offset=//g"`
GIT_PKG_BUMP=`cat packages/$PACKAGE_NAME/package.ini | egrep -e "^git_pkg_bump" | sed -e"s/git_pkg_bump=//g"`
TAR_BALL=`cat packages/$PACKAGE_NAME/package.ini | egrep -e "^tar_ball" | sed -e"s/tar_ball=//g"`
TAR_STRIP_ROOT=`cat packages/$PACKAGE_NAME/package.ini | egrep -e "^tar_strip_root" | sed -e"s/tar_strip_root=//g"`
CENTOS7_SPECFILE=$PACKAGENAME/`cat packages/$PACKAGE_NAME/package.ini | egrep -e "^centos7_spec_file" | sed -e"s/centos7_spec_file=//g"`
CENTOS8_SPECFILE=$PACKAGENAME/`cat packages/$PACKAGE_NAME/package.ini | egrep -e "^centos8_spec_file" | sed -e"s/centos8_spec_file=//g"`
REDHAT8_SPECFILE=$PACKAGENAME/`cat packages/$PACKAGE_NAME/package.ini | egrep -e "^redhat8_spec_file" | sed -e"s/redhat8_spec_file=//g"`
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

if hash python 2> /dev/null; then
  SCRIPTDIR=`dirname $(python -c "import os; print(os.path.abspath(\"$0\"))")`
else
  SCRIPTDIR=`dirname $(python3.6 -c "import os; print(os.path.abspath(\"$0\"))")`
fi

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

copy_package_to_location() {
  XSTR=$1
  if [ "${XSTR:0:4}" = "scp:" ]; then
    TARGET=${XSTR:4}
    REMOTE_DIR=`echo "$TARGET" | sed -e "s/.*://g"`
    REMOTE_USER=`echo "$TARGET" | sed -e "s/:.*//g"`
    if [ "$REMOTE_DIR" != "" -a "$REMOTE_USER" != "" ]; then
      echo "Creating remote directory $REMOTE_DIR on $REMOTE_USER"
      ssh $REMOTE_USER "mkdir -p $REMOTE_DIR"
      echo "scp $2 $TARGET"
      scp $2 "$TARGET" 2>/dev/null
    else
      echo "Failed to identify scp. Format should be scp:<user>@<host>:<dir>, e.g. scp:baltrad@192.168.2.1:~/artifacts/2018-11-21"
      exit 127
    fi
  else
    XSTR=${XSTR/#\~/$HOME}
    if [ ! -d "$XSTR" ]; then
      mkdir -p "$XSTR" || exit 127
    fi
    FILES=`ls -1 $2 2>/dev/null`
    if [ "$FILES" != "" ]; then
      cp $2 "$XSTR/" 2>/dev/null
    fi
  fi
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

  copy_package_to_location "$6" "../$2*_$3*.deb"
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

  \rm -f "$RPM_PCK_DIR/$3-*.rpm"
  \rm -f "$RPM_PCK_NOARCH_DIR/$3-*.rpm"

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
  
  if [ "$RPM_ARTIFACTS" != "" ]; then
    RPMS_TOPDIR=`rpmbuild --eval '%_rpmdir'`
    RPMS_TO_INSTALL=
    for X in $RPM_ARTIFACTS; do
      fname=`echo $X | sed -e "s/<buildver>/$PACKAGE_VERSION-$BUILD_NUMBER/g"`
      FILES=`ls -1 $RPMS_TOPDIR/$fname 2>&1`
      if [ $? -eq 0 ]; then
        for f in $FILES; do
          copy_package_to_location "$9" "$f"
          RPMS_TO_INSTALL="$RPMS_TO_INSTALL $f"
        done
      fi
    done
    if [ "$6" = "true" -a "$RPMS_TO_INSTALL" != "" ]; then
      echo "Installing $RPMS_TO_INSTALL"
      sudo rpm --force -Uvh $RPMS_TO_INSTALL
    fi
  else
    if [ "$6" = "true" ]; then
      if [ "$RPM_PCK_DIR" != "" ]; then
        # Use --force to be able to use same pck-number
        FILES=`ls -1 $RPM_PCK_DIR/$3*-$4-$5*.$RPM_ARCH_DIR.rpm 2>/dev/null`
        if [ "$FILES" != "" ]; then
          sudo rpm --force -Uvh "$RPM_PCK_DIR/$3*-$4-$5.*$RPM_ARCH_DIR.rpm" 
	    fi
      fi
      if [ "$RPM_PCK_NOARCH_DIR" != "" ]; then
        FILES=`ls -1 $RPM_PCK_NOARCH_DIR/$3*-$4-$5*.noarch.rpm 2>/dev/null`
        if [ "$FILES" != "" ]; then
          sudo rpm --force -Uvh "$RPM_PCK_NOARCH_DIR/$3*-$4-$5.*noarch.rpm"
        fi
      fi
    fi
    if [ "$RPM_PCK_DIR" != "" ]; then
      copy_package_to_location "$9" "$RPM_PCK_DIR/$3*-$4-$5.*$RPM_ARCH_DIR.rpm"
    fi
    if [ "$RPM_PCK_NOARCH_DIR" != "" ]; then
      copy_package_to_location "$9" "$RPM_PCK_NOARCH_DIR/$3*-$4-$5.*noarch.rpm"
    fi
  fi
}

add_git_tag_to_history() {
  MODULE=$1
  BUILDVERSION=$2
  PREVTAG=$3
  LASTUPDATE=`date +%Y%m%d%H%M%S`
  TNAME=`git describe 2>&1`
  if [ $? -eq 0 ]; then
    echo -e "$MODULE\t$LASTUPDATE\t$BUILDVERSION\t$TNAME\t$PREVTAG" >> $4
  else
    echo -e "$MODULE\t$LASTUPDATE\t$BUILDVERSION\tNOT_DEFINED\t$PREVTAG" >> $4
  fi
}

get_lastupdatetime_for_module() {
  RESULT=`cat "$2" | egrep -e "^$1" | cut -d $'\t' -f2 | tail -1`
  if [ $? -eq 0 ]; then
    echo "$RESULT"
  else
    echo ""
  fi
}

get_buildversion_for_module() {
  RESULT=`cat "$2" | egrep -e "^$1" | cut -d $'\t' -f3 | tail -1`
  if [ $? -eq 0 ]; then
    echo "$RESULT"
  else
    echo ""
  fi
}

get_tag_for_module() {
  RESULT=`cat "$2" | egrep -e "^$1" | cut -d $'\t' -f4 | tail -1`
  if [ $? -eq 0 ]; then
    echo "$RESULT"
  else
    echo ""
  fi
}

get_prevtag_for_module() {
  RESULT=`cat "$2" | egrep -e "^$1" | cut -d $'\t' -f5 | tail -1`
  if [ $? -eq 0 ]; then
    echo "$RESULT"
  else
    echo ""
  fi
}

add_buildlog_information() {
  buildName=$1
  buildVersion=$2
  buildLogFile=$3

  lastBuiltVersion=
  prevBuiltTag=
  lastUpdatetime=

  if [ "$buildLogFile" != "" ]; then
    if [ ! -f "$buildLogFile" ]; then
      touch "$buildLogFile"
      if [ $? -ne 0 ]; then
        echo "Failed to create build log file"
        exit 127
      fi
    fi
    
    if [ -f "$buildLogFile" ]; then
      lastUpdatetime=`get_lastupdatetime_for_module "$buildName" "$buildLogFile"`
      lastBuiltVersion=`get_buildversion_for_module "$buildName" "$buildLogFile"`
      lastBuiltTag=`get_tag_for_module "$buildName" "$buildLogFile"`
      prevBuiltTag=`get_prevtag_for_module "$buildName" "$buildLogFile"`
    fi
    
    if [ "$buildVersion" != "$lastBuiltVersion" ]; then
      add_git_tag_to_history "$buildName" "$buildVersion" "$lastBuiltTag" "$buildLogFile"
    fi
  fi
}

get_git_repo_version() {
  offset=$1
  gexpression=$2
  noextract=$3
  bump=$4
  
  TNAME=`git describe`
  VER=`echo $TNAME | sed -e "$gexpression"`
  if [ "$bump" = "" ]; then
    bump=0
  fi
  
  if [ "$VER" != "" ]; then
    NBR=`echo $VER | egrep -e "^[0-9]+\$"`
    if [ "$VER" != "$TNAME" -a "$NBR" != "" ]; then
      VER=`expr $VER - $offset + 1 + $bump`
    else
      if [ "$noextract" != "" ]; then
        VER=$noextract
      else
        VER=1
      fi
    fi
    echo "$VER"
  else
    echo ""
  fi
}

if [ "$BUILD_NUMBER" = "" ]; then
  BUILD_NUMBER=auto
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
    if [ "$BUILD_NUMBER" = "auto" ]; then
      if [ "$GIT_PKG_BUMP" != "" ]; then
        BUILD_NUMBER=`expr 1 + $GIT_PKG_BUMP`
      else
        BUILD_NUMBER=1 # Always set build number to 1 on auto when unpacking tarballs unless bump has been set
      fi
    fi  
  else
    git clone $GIT_URI $BUILD_NAME || exit 127
  fi
  cd $BUILD_NAME
  if [ "$BUILD_NUMBER" = "auto" ]; then
    TMP_NUMBER=`get_git_repo_version "$GIT_PKG_OFFSET" "$GIT_PKG_NBR" "$GIT_PKG_NO_EXTRACT" "$GIT_PKG_BUMP"`
    if [ "$TMP_NUMBER" != "" ]; then
      BUILD_NUMBER=$TMP_NUMBER
    else
      echo "Could not determine build number from repository $BUILD_NAME"
      exit 127
    fi
  fi
else
  cd build/$BUILD_NAME
  git checkout . || exit 127 # REMOVE ALL OLD STUFF
  git checkout master || exit 127
  git pull || exit 127
  if [ "$BUILD_NUMBER" = "auto" ]; then
    TMP_NUMBER=`get_git_repo_version "$GIT_PKG_OFFSET" "$GIT_PKG_NBR" "$GIT_PKG_NO_EXTRACT" "$GIT_PKG_BUMP"`
    if [ "$TMP_NUMBER" != "" ]; then
      BUILD_NUMBER=$TMP_NUMBER
    else
      echo "Could not determine build number from repository $BUILD_NAME"
      exit 127
    fi
  fi
fi

CREATE_TAR_FROM_FOLDER=false
if [ "$TAR_BALL" != "" ]; then
  CREATE_TAR_FROM_FOLDER=true
fi

ARTIFACT_REPOSITORY="../../artifacts/$OS_VARIANT/"
if [ "$ARTIFACTS" != "" ]; then
  ARTIFACT_REPOSITORY=$ARTIFACTS
fi

if [ "$OS_VARIANT" = "Ubuntu-16.04" -o "$OS_VARIANT" = "Ubuntu-18.04" -o "$OS_VARIANT" = "Ubuntu-18.10" ]; then
  prepare_and_build_debian "$PACKAGEDIR/$PACKAGE_NAME/debian" $BUILD_NAME $PACKAGE_VERSION-$BUILD_NUMBER $INSTALL_ARTIFACTS "$OS_VARIANT" "$ARTIFACT_REPOSITORY"
  add_buildlog_information "$BUILD_NAME" "$PACKAGE_VERSION-$BUILD_NUMBER" "$BUILD_LOG"
  exit 0
elif [ "$OS_VARIANT" = "CentOS-7" ]; then
  prepare_and_build_centos "$PACKAGEDIR/$PACKAGE_NAME/centos" "$PACKAGEDIR/$PACKAGE_NAME/$CENTOS7_SPECFILE" $BUILD_NAME $PACKAGE_VERSION $BUILD_NUMBER $INSTALL_ARTIFACTS $CREATE_TAR_FROM_FOLDER "$OS_VARIANT" "$ARTIFACT_REPOSITORY"
  add_buildlog_information "$BUILD_NAME" "$PACKAGE_VERSION-$BUILD_NUMBER" "$BUILD_LOG"
  exit 0
elif [ "$OS_VARIANT" = "CentOS-8" ]; then
  prepare_and_build_centos "$PACKAGEDIR/$PACKAGE_NAME/centos" "$PACKAGEDIR/$PACKAGE_NAME/$CENTOS8_SPECFILE" $BUILD_NAME $PACKAGE_VERSION $BUILD_NUMBER $INSTALL_ARTIFACTS $CREATE_TAR_FROM_FOLDER "$OS_VARIANT" "$ARTIFACT_REPOSITORY"
  add_buildlog_information "$BUILD_NAME" "$PACKAGE_VERSION-$BUILD_NUMBER" "$BUILD_LOG"
  exit 0
elif [ "$OS_VARIANT" = "Red Hat Enterprise-8.0" ]; then
  prepare_and_build_centos "$PACKAGEDIR/$PACKAGE_NAME/centos" "$PACKAGEDIR/$PACKAGE_NAME/$REDHAT8_SPECFILE" $BUILD_NAME $PACKAGE_VERSION $BUILD_NUMBER $INSTALL_ARTIFACTS $CREATE_TAR_FROM_FOLDER "$OS_VARIANT" "$ARTIFACT_REPOSITORY"
  add_buildlog_information "$BUILD_NAME" "$PACKAGE_VERSION-$BUILD_NUMBER" "$BUILD_LOG"
  exit 0
else
  echo "Unsupported build variant $OS_VARIANT"
  exit 127  
fi


