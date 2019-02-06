#!/bin/bash

# Brief usage
usage_brief() {
  echo "Usage: `basename $0` [<options>]"
}

# Usage
usage() {
  echo "Usage: `basename $0` [<options>]"
  echo "Options:"
  echo "--install   - If build packages should be installed as well."
  echo "--rebuild   - If packages should be rebuilt even if they already are in artifacts directory"
  echo "--artifacts=<loc>       - The directory where the artifacts should be placed (also support scp if "
  echo "                          the target location accepts copying without a password). In that case,"
  echo "                          the specified location should be like scp:<user>@<host>:<loc>"
  echo "                          If not specifying this the packages will be placed under "
  echo                            "packages/<package>/artifacts/<OS build>"
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

SCRIPTDIR=`dirname $(python -c "import os; print(os.path.abspath(\"$0\"))")`
SPECDIR=$SCRIPTDIR
INSTALLPACKAGES=no
REBUILDPACKAGES=no
ARTIFACTS="$SCRIPTDIR/artifacts"

for arg in $*; do
  case $arg in
    --install)
      INSTALLPACKAGES=yes
      ;;
    --rebuild)
      REBUILDPACKAGES=yes
      ;;
    --artifacts=*)
      ARTIFACTS=`echo $arg | sed 's/[-a-zA-Z0-9]*=//'`
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

SOURCEDIR=`rpmbuild --eval '%_topdir'/SOURCES/`
RPMDIR=`rpmbuild --eval '%_topdir'/RPMS/x86_64/`

PYP=`which py2pack`

do_exit() {
  echo "$*"
  exit 127
}

if [ "$PYP" = "" ]; then
  do_exit "Must install py2pack before running this script"
fi  

if [ ! -d "$SOURCEDIR" ]; then
  do_exit "Sourcedir ($SOURCEDIR) must exist"
fi

do_fetch_package_and_build() {
  if [ ! -f "$SOURCEDIR/$1-$2.tar.gz" ]; then
    py2pack fetch "$1" "$2" || do_exit "Failed to fetch package"
    FNAME=`ls -1 | grep -i "$1-$2.tar.gz"`
    if [ "$FNAME" != "" ]; then
      mv "$FNAME" "$SOURCEDIR/$1-$2.tar.gz" || do_exit "Failed to copy source to SOURCEDIR"
    else
      do_exit "Could not identify package"
    fi
  fi
  if [ ! -f "$RPMDIR/$4" -o "$REBUILDPACKAGES" = "yes" ]; then
    rpmbuild -v -ba "$SPECDIR/$3" || do_exit "Failed to build $SPECDIR/$3"
  fi
  if [ "$INSTALLPACKAGES" = "yes" ]; then
    sudo rpm --force -Uvh "$RPMDIR/$4" || do_exit "Failed to install $RPMDIR/$4"
  fi
  copy_package_to_location "$ARTIFACTS" "$RPMDIR/$4" || do_exit "Failed to copy $4 from rpm dir to $ARTIFACTS"
}

do_fetch_package_and_build jprops 2.0.2 jprops.spec python36-jprops-blt-2.0.2-0.x86_64.rpm

do_fetch_package_and_build progressbar33 2.4 progressbar33.spec python36-progressbar33-blt-2.4-0.x86_64.rpm

do_fetch_package_and_build pillow 5.4.1 pillow.spec python36-pillow-blt-5.4.1-0.x86_64.rpm

do_fetch_package_and_build psycopg2 2.7.7 psycopg2.spec python36-psycopg2-blt-2.7.7-0.x86_64.rpm

do_fetch_package_and_build pyasn1 0.4.5 pyasn1.spec python36-pyasn1-blt-0.4.5-0.x86_64.rpm

do_fetch_package_and_build pycrypto 2.4 pycrypto.spec python36-pycrypto-blt-2.4-0.x86_64.rpm

do_fetch_package_and_build python3-keyczar 0.71rc0 python3-keyczar.spec python36-keyczar-blt-0.71rc0-0.x86_64.rpm

do_fetch_package_and_build docutils 0.14 docutils.spec python36-docutils-blt-0.14-0.x86_64.rpm

do_fetch_package_and_build "lockfile" 0.12.2 lockfile.spec python36-lockfile-blt-0.12.2-0.x86_64.rpm

do_fetch_package_and_build python-daemon 2.2.3 python-daemon.spec python36-daemon-blt-2.2.3-0.x86_64.rpm

do_fetch_package_and_build tempita 0.5.2 tempita.spec python36-tempita-blt-0.5.2-0.x86_64.rpm

do_fetch_package_and_build sqlparse 0.2.4 sqlparse.spec python36-sqlparse-blt-0.2.4-0.x86_64.rpm

do_fetch_package_and_build decorator 4.3.2 decorator.spec python36-decorator-blt-4.3.2-0.x86_64.rpm

do_fetch_package_and_build pbr 1.10.0 pbr.spec python36-pbr-blt-1.10.0-0.x86_64.rpm

do_fetch_package_and_build sqlalchemy 1.0.13 sqlalchemy.spec python36-sqlalchemy-blt-1.0.13-0.x86_64.rpm

do_fetch_package_and_build sqlalchemy-migrate 0.10.0 sqlalchemy-migrate.spec python36-sqlalchemy-migrate-blt-0.10.0-0.x86_64.rpm

do_fetch_package_and_build werkzeug 0.14 werkzeug.spec python36-werkzeug-blt-0.14-0.x86_64.rpm

do_fetch_package_and_build cherrypy 3.8.2 cherrypy.spec python36-cherrypy-blt-3.8.2-0.x86_64.rpm
