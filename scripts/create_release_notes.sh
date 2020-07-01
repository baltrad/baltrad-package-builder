#!/bin/bash

# Brief usage
usage_brief() {
  echo "Usage: `basename $0` [options|--help] <build log>"
}

# Usage
usage() {
  echo "Usage: `basename $0` <build-log>"
  echo "  <build-log>           - The file where information about build status for the different modules can be found."
  echo "                          If not specified, no changelog can be created"
  echo "Options:"
  echo "--artifact=<loc>        - Name of the release notes file to be generated. (also support scp if "
  echo "                          the target location accepts copying without a password). In that case,"
  echo "                          the specified location should be like scp:<user>@<host>:<loc>"
  echo "--modules=<modules>     - Comma-separated list of modules for which change log should be generated. Defaults to everything."
  echo ""
  echo "--distr=<distr>         - Distribution"
  echo "--build-version=<version> - The build version. Defaults to ---"
  echo ""
  echo "--help                    Prints this information."
}

if [ $# -lt 1 ]; then
  usage_brief
  exit 127
fi

BUILD_LOG=
BUILD_VERSION=---
DISTR=
ARTIFACT=

MODULES="hlhdf rave baltrad-beast baltrad-config baltrad-db baltrad-dex baltrad-node-tomcat baltrad-ppc baltrad-viewer baltrad-wrwp bbufr beamb bropo hdf-java"

for arg in $*; do
  case $arg in
    --artifact=*)
      ARTIFACT=`echo $arg | sed 's/[-a-zA-Z0-9]*=//'`
      ;;
    --modules=*)
      MODULES=`echo $arg | sed 's/[-a-zA-Z0-9]*=//' | sed 's/,/ /'`
      ;;
    --build-version=*)
      BUILD_VERSION=`echo $arg | sed 's/[-a-zA-Z0-9]*=//'`
      ;;
    --distr=*)
      DISTR=`echo $arg | sed 's/[-a-zA-Z0-9]*=//'`
      ;;
    --help)
      usage $0
      exit 0
      ;;
    *)
      if [ "$BUILD_LOG" != "" ]; then
        echo "Unknown option or command: $arg"
        usage_brief $0
        exit 127
      else
        BUILD_LOG="$arg"
      fi
      ;;      
  esac
done

if [ "$BUILD_LOG" = "" ]; then
  usage_brief
  exit 127
fi

if [ ! -f "$BUILD_LOG" ]; then
  echo "No build log exists at $BUILD_LOG"
  exit 127
fi

SCRIPTDIR=`dirname $(python3 -c "import os; print(os.path.abspath(\"$0\"))")`

PACKAGEDIR=$(dirname $SCRIPTDIR)/packages

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

generate_changelog() {
  module=$1
  pkgname=$1
  buildfile=$2
  if [ -f "$PACKAGEDIR/$module/package.ini" ]; then
    full_name=`cat "$PACKAGEDIR/$module/package.ini" | egrep -e "^pkg_full_name" | sed -e"s/pkg_full_name=//g"`
    build_name=`cat "$PACKAGEDIR/$module/package.ini" | egrep -e "^pkg_name" | sed -e"s/pkg_name=//g"`
    if [ "$full_name" = "" ]; then
      full_name=$1
    fi
    if [ "$build_name" != "" ]; then
      pkgname=$build_name
    fi
    buildVersion=`get_buildversion_for_module "$module" "$buildfile"`
    fromTag=`get_prevtag_for_module "$module" "$buildfile"`
    toTag=`get_tag_for_module "$module" "$buildfile"`
    if [ "$fromTag" = "" ]; then
      fromTag=$toTag
    fi
    echo "$full_name - $buildVersion"
    if [ "$fromTag" != "NOT_DEFINED" -a "$toTag" != "NOT_DEFINED" ]; then
      echo "Versions: $fromTag to $toTag"
      echo ""
      CDIR=`pwd`
      cd "$PACKAGEDIR/$module/build/$pkgname"
      if [ "$fromTag" = "$toTag" ]; then
        git log -n 1 --pretty="%s%n" | egrep -e "^Ticket\s+[0-9]+:" | sort | uniq -w 12
      else
        git log "$fromTag".."$toTag" --pretty="%s%n" | egrep -e "^Ticket\s+[0-9]+:" | sort | uniq -w 12
      fi
      cd "$CDIR"
    else
      echo "No information available"
      echo ""
    fi
  fi
}

create_release_note() {
  echo "RELEASE NOTES `date -u +%Y-%m-%dT%H:%M:%SZ` $DISTR $BUILD_VERSION"
  echo "================================================================"
  echo "Versions:"
  header="%-20s %15s\n"
  format="%-20s  %15s\n"
    
  printf "$header" "Module" "Version"
  for m in $MODULES; do
    BV=`get_buildversion_for_module "$m" "$BUILD_LOG"`
    if [ "$BV" != "" ]; then
      printf "$format" "$m" "$BV"
    fi
  done
  echo "================================================================"

  for m in $MODULES; do
    BV=`get_buildversion_for_module "$m" "$BUILD_LOG"`
    if [ "$BV" != "" ]; then
      generate_changelog "$m" "$BUILD_LOG"
      echo "================================================================"
    fi
  done
}

copy_package_to_location() {
  XSTR=$1
  if [ "${XSTR:0:4}" = "scp:" ]; then
    TARGET=${XSTR:4}
    REMOTE_FILE=`echo "$TARGET" | sed -e "s/.*://g"`
    REMOTE_DIR=`dirname $REMOTE_FILE`
    REMOTE_USER=`echo "$TARGET" | sed -e "s/:.*//g"`
    echo "REMOTEDIR: $REMOTE_DIR"
    echo "REMOTEFILE: $REMOTE_FILE"
    
    echo "$REMOTE_DIR, $REMOTE_USER"
    if [ "$REMOTE_DIR" != "" -a "$REMOTE_USER" != "" ]; then
      if [ "$REMOTE_DIR" != "." ]; then
        echo "Creating remote directory $REMOTE_DIR on $REMOTE_USER"
        ssh $REMOTE_USER <<EOFSSH
if [ ! -d "$REMOTE_DIR" ]; then
  mkdir -p "$REMOTE_DIR"
fi
EOFSSH
      fi
      #ssh $REMOTE_USER "mkdir -p $REMOTE_DIR"
      echo "scp $2 $TARGET"
      scp $2 "$TARGET" 2>/dev/null
    else
      echo "Failed to identify scp. Format should be scp:<user>@<host>:<dir>, e.g. scp:baltrad@192.168.2.1:~/artifacts/2018-11-21"
      exit 127
    fi
  else
    XSTR=${XSTR/#\~/$HOME}
    DIRNAME=`dirname "$XSTR"`
    echo "DIRNAME=$DIRNAME"
    if [ ! -d "$DIRNAME" ]; then
      mkdir -p "$DIRNAME" || exit 127
    fi
    cp $2 "$XSTR" 2>/dev/null
    chmod ag+r "$XSTR"    
  fi
}

if [ "$ARTIFACT" = "" ]; then
  create_release_note
else
  TMPFILE=`mktemp`
  if [ $? -ne 0 ]; then
    echo "Failed to create tempfile"
    exit 127
  fi 
  create_release_note > "$TMPFILE"
  chmod ag+r "$TMPFILE"
  copy_package_to_location "$ARTIFACT" "$TMPFILE"
  \rm -f "$TMPFILE" 
fi


