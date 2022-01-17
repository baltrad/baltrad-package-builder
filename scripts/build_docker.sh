#!/bin/bash

SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
PROJECTPATH="$(dirname $SCRIPTPATH)"
DOCKERPATH="$PROJECTPATH/docker"

# Brief usage
usage_brief() {
  echo "Usage: `basename $0`  [--docker=<version>] list|build|rebuild"
}

# Usage
usage() {
  echo "Usage: `basename $0`  [--docker=<version>] list|build|rebuild"
  echo "Options:"
  echo "--docker=<version>   - Docker version as defined when running list"
  echo ""
  echo "Commands:"
  echo " list      - Lists all available docker versions"
  echo " build     - Builds the docker container. Requires --docker=<version>."
  echo " rebuild   - Rebuilds the docker container. Requires --docker=<version>."
}

DOCKER_BUILD=
DO_LIST=no
DO_BUILD=no
DO_REBUILD=no
NR_CMD=0

for arg in $*; do
  case $arg in
    --docker=*)
      DOCKER_BUILD=`echo $arg | sed 's/--docker=//'`
      ;;
    --help)
      usage $0
      exit 0
      ;;    
    list)
      DO_LIST=yes
      NR_CMD=$(($NR_CMD+1))
      ;;      
    build)
      DO_BUILD=yes
      NR_CMD=$(($NR_CMD+1))
      ;;      
    rebuild)
      DO_REBUILD=yes
      NR_CMD=$(($NR_CMD+1))
      ;;      
    *)
      echo "Unknown option or command: $arg"
      usage_brief $0
      exit 127
      ;;      
  esac
done

if [ $NR_CMD -ne 1 ]; then
  usage_brief $0
  exit 127
fi

if [ "$DO_BUILD" = "yes" -o "$DO_REBUILD" = "yes" ]; then
  if [ "$DOCKER_BUILD" = "" ]; then
    echo "Must specify --docker=<> when running build or rebuild"
    exit 127
  fi
fi

if [ "$DO_LIST" = "yes" ]; then
  ls -1 "$DOCKERPATH/"
  exit 0
fi

if [ "$DO_BUILD" = "yes" ]; then
  ls -1 "$DOCKERPATH/"
  exit 0
fi

