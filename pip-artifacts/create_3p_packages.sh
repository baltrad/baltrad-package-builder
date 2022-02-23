#!/bin/bash

SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
PROJECTPATH="$(dirname $SCRIPTPATH)"
DOCKERPATH="$PROJECTPATH/docker"

# Brief usage
usage_brief() {
  echo "Usage: `basename $0` [<options>]"
}

exit_with_error()
{
  echo "$2" 1>&2
  exit $1
}

echo_to_stderr()
{
  echo "$2" 1>&2
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

SCRIPTDIR=$SCRIPTPATH
SPECDIR=$SCRIPTDIR
INSTALLPACKAGES=no
REBUILDPACKAGES=no
ARTIFACTS="$SCRIPTDIR/artifacts"
DOCKER_BUILD=

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

run_docker_build() {
  dockerver=$1
  dockerimage=`echo $dockerver | tr A-Z a-z`-bpb-image
  artifactrepo=$2
  
  pipargs="--install"
  if [ "$REBUILDPACKAGE" = "yes" ]; then
    pipargs="$pipargs --rebuild"
  fi
  
  if [ -d "$DOCKERPATH/$dockerver" ]; then
    BUILT=$(docker image ls | grep $dockerimage)
    if [ "$BUILT" == "" ]; then
      cd "$DOCKERPATH/$1"
      docker build -t $dockerimage .
    fi
    docker container rm "$dockerimage" >> /dev/null 2>&1
    TMPSOURCES=`mktemp -d`    TMPSOURCES=`mktemp -d`
    cd "$PROJECTPATH"
    git ls-files | tar -cf "$TMPSOURCES/docker_build.tar" -T - || exit_with_error 127 "Failed to create tar-file"
    docker run --name "$dockerimage" -v "$TMPSOURCES":/projects/sources -it $dockerimage /bin/bash -c "tar -xf /projects/sources/docker_build.tar -C /projects/baltrad-package-builder/ && mkdir -p /projects/artifacts/3p_packages && \rm -f /projects/artifacts/3p_packages/*.* && \rm -f /projects/artifacts/3p_packages.tar && /projects/baltrad-package-builder/pip-artifacts/create_3p_packages.sh $pipargs --artifacts=/projects/artifacts/3p_packages && tar -cf /projects/artifacts/3p_packages.tar -C /projects/artifacts 3p_packages" || (echo_to_stderr "Failed to run build" && \rm -fr "$TMPSOURCES" && exit 127)
    #docker run --name "$dockerimage" -v "$PROJECTPATH":/projects/baltrad-package-builder -u $(id -u ${USER}):$(id -g ${USER}) -it $dockerimage /bin/bash -c "mkdir -p /projects/artifacts/3p_packages && \rm -f /projects/artifacts/3p_packages/*.* && \rm -f /projects/artifacts/3p_packages.tar && /projects/baltrad-package-builder/pip-artifacts/create_3p_packages.sh $pipargs --artifacts=/projects/artifacts/3p_packages && tar -cf /projects/artifacts/3p_packages.tar -C /projects/artifacts 3p_packages" || exit_with_error 127 "Failed to run command"
    \rm -fr "$TMPSOURCES"
    echo "Updating $dockerimage commit for $pkgname"
    LAST_COMMIT=`docker ps --all | grep $dockerimage | head -1 | cut -d' ' -f1` || exit_with_error 127 "Failed list ran commit"
    docker commit "$LAST_COMMIT" $dockerimage || exit_with_error 127 "Failed to commit build for $dockerimage"
    TMPD=`mktemp -d` || exit_with_error 127 "Could not create temporary directory"
    echo "docker container cp $dockerimage:/projects/artifacts/3p_packages.tar $TMPD"
    docker cp $dockerimage:/projects/artifacts/3p_packages.tar $TMPD
    if [ $? -ne 0 ]; then
      \rm -fr "$TMPD"
      echo "Could not perform docker cp $dockerimage:/projects/artifacts/3p_packages.tar to $TMPD"
      exit 127
    fi
    tar -xf "$TMPD/3p_packages.tar" -C "$TMPD"
    if [ $? -ne 0 ]; then
      \rm -fr "$TMPD"
      echo "Could not extract $TMPD/3p_packages.tar"
      exit 127
    fi
    echo "copy_package_to_location \"$artifactrepo\" \"$TMPD/3p_packages/*.*\""
    copy_package_to_location "$artifactrepo" "$TMPD/3p_packages/*.*"
    if [ $? -ne 0 ]; then
      \rm -fr "$TMPD"
      echo "Could not distribute files from $TMPD/3p_packages.tar"
      exit 127
    fi    
    \rm -fr "$TMPD"
  else
    echo "No docker support for OS-version: $ver"
    exit 127
  fi
}

if [ "$DOCKER_BUILD" != "" ]; then
  run_docker_build "$DOCKER_BUILD" "$ARTIFACTS"
  exit 0
fi

SOURCEDIR=`rpmbuild --eval '%_topdir'/SOURCES/`
RPMDIR=`rpmbuild --eval '%_topdir'/RPMS/x86_64/`

PYP=`which py2pack`

do_exit() {
  echo "$*"
  exit 127
}

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

OS_VARIANT=`get_os_version`

echo "Copying patch-files to sources."
cp "$SPECDIR/"*.patch "$SOURCEDIR/"

do_fetch_package_and_build jprops 2.0.2 jprops.spec python36-jprops-blt-2.0.2-0.x86_64.rpm

if [ "$OS_VARIANT" = "CentOS-7" ]; then
  do_fetch_package_and_build progressbar33 2.4 progressbar33.spec python36-progressbar33-blt-2.4-0.x86_64.rpm

  do_fetch_package_and_build pillow 5.4.1 pillow.spec python36-pillow-blt-5.4.1-1.x86_64.rpm

  do_fetch_package_and_build psycopg2 2.7.7 psycopg2.spec python36-psycopg2-blt-2.7.7-0.x86_64.rpm

  do_fetch_package_and_build pyasn1 0.4.5 pyasn1.spec python36-pyasn1-blt-0.4.5-0.x86_64.rpm
fi

do_fetch_package_and_build pycrypto 2.4 pycrypto.spec python36-pycrypto-blt-2.4-0.x86_64.rpm

if [ "$OS_VARIANT" = "Red Hat Enterprise-8.0" -o "$OS_VARIANT" = "CentOS-8" -o "$OS_VARIANT" = "CentOS Stream-8" ]; then
  do_fetch_package_and_build python3-keyczar 0.71rc0 python3-keyczar-redhat8.spec python36-keyczar-blt-0.71rc0-1.x86_64.rpm
else
  do_fetch_package_and_build python3-keyczar 0.71rc0 python3-keyczar.spec python36-keyczar-blt-0.71rc0-0.x86_64.rpm
fi


if [ "$OS_VARIANT" = "CentOS-7" ]; then
  do_fetch_package_and_build docutils 0.14 docutils.spec python36-docutils-blt-0.14-0.x86_64.rpm

  do_fetch_package_and_build "lockfile" 0.12.2 lockfile.spec python36-lockfile-blt-0.12.2-0.x86_64.rpm

  do_fetch_package_and_build python-daemon 2.2.3 python-daemon.spec python36-daemon-blt-2.2.3-0.x86_64.rpm

  do_fetch_package_and_build tempita 0.5.2 tempita.spec python36-tempita-blt-0.5.2-0.x86_64.rpm

  do_fetch_package_and_build sqlparse 0.2.4 sqlparse.spec python36-sqlparse-blt-0.2.4-0.x86_64.rpm

  do_fetch_package_and_build decorator 4.3.2 decorator.spec python36-decorator-blt-4.3.2-0.x86_64.rpm

  do_fetch_package_and_build pbr 1.10.0 pbr.spec python36-pbr-blt-1.10.0-0.x86_64.rpm

  do_fetch_package_and_build sqlalchemy 1.0.13 sqlalchemy.spec python36-sqlalchemy-blt-1.0.13-0.x86_64.rpm
fi


if [ "$OS_VARIANT" = "Red Hat Enterprise-8.0" -o "$OS_VARIANT" = "CentOS-8" -o "$OS_VARIANT" = "CentOS Stream-8" ]; then
  do_fetch_package_and_build sqlalchemy-migrate 0.10.0 sqlalchemy-migrate-redhat8.spec python36-sqlalchemy-migrate-blt-0.10.0-1.x86_64.rpm
else
  do_fetch_package_and_build sqlalchemy-migrate 0.10.0 sqlalchemy-migrate.spec python36-sqlalchemy-migrate-blt-0.10.0-1.x86_64.rpm
fi

if [ "$OS_VARIANT" = "CentOS-7" ]; then
  do_fetch_package_and_build werkzeug 1.0.1 werkzeug.spec python36-werkzeug-blt-1.0.1-0.x86_64.rpm

  do_fetch_package_and_build cherrypy 3.8.2 cherrypy.spec python36-cherrypy-blt-3.8.2-0.x86_64.rpm

  do_fetch_package_and_build pyinotify 0.9.6 pyinotify.spec python36-pyinotify-blt-0.9.6-0.x86_64.rpm
fi

