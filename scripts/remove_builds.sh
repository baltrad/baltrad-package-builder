#!/bin/sh

if [ $# -lt 1 ]; then
  echo "Usage: $0 <package name>"
  exit 127
fi
PACKAGE_NAME=$1
SCRIPTDIR=`dirname $(python -c "import os; print(os.path.abspath(\"$0\"))")`
PACKAGEDIR=$(dirname $SCRIPTDIR)/packages

if [ -d "$PACKAGEDIR/$PACKAGE_NAME" ]; then
  cd "$PACKAGEDIR/$PACKAGE_NAME"
  \rm -fr build
fi


