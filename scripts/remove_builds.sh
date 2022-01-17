#!/bin/bash

SCRIPTDIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
PACKAGEDIR=$(dirname $SCRIPTDIR)/packages

remove_package() {
  if [ -d "$1/build" ]; then
    cd "$1"
    echo "Removing build in "`pwd`
    \rm -fr "build"
  fi
}

if [ $# -lt 1 ]; then
  cd $PACKAGEDIR
  PACKAGES=`ls -1`
  for pkg in $PACKAGES; do
    remove_package "$PACKAGEDIR/$pkg"
  done
else
  remove_package "$PACKAGEDIR/$1"  
fi



