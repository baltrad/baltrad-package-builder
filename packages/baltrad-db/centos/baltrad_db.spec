%{!?__python36: %global __python36 /usr/bin/python36}
%{!?python36_sitelib: %global python36_sitelib %(%{__python36} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}
%{!?bdb_site_install_dir: %global bdb_site_install_dir /usr/lib/python3.6/site-packages}
%define _prefix /usr

Name: baltrad-db
Version: %{version}
Release: %{snapshot}%{?dist}
Summary: BaltradDB
License: GPL-3 and LGPL-3
URL: http://www.baltrad.eu/
Patch1: baltrad_db_server_setup.patch
Source0: %{name}-%{version}.tar.gz
BuildRequires: python36-devel
BuildRequires: python-distribute
BuildRequires: java-1.8.0-openjdk-devel
BuildRequires: ant
BuildRequires: jpackage-utils
Requires: hlhdf
Requires: hlhdf-python
Requires: python36
Requires: python36-progressbar33-blt
Requires: python36-psycopg2-blt
Requires: python36-werkzeug-blt
Requires: python36-daemon-blt
Requires: python36-keyczar-blt
Requires: python36-distribute-blt
Requires: python36-sqlalchemy-blt
Requires: python36-sqlalchemy-migrate-blt
Requires: python36-cherrypy-blt
Conflicts: baltrad-db-py27

%description
Provides storage, retrieval and queries for ODIM/H5 compliant files to other parts of the Baltrad system

%package java
Summary: Java client for BaltradDB
Requires: postgresql-jdbc

%description java
Java client for BaltradDB

%package external
Summary: External JAVA jars other Baltrad components need
Group: Development/Libraries

%description external
External JAVA jars other Baltrad components (primarily BaltradDex) use, which
are provided in the baltrad-db package.

%prep
%setup -q
%patch1 -p1

%build
cd common
%{__python36} setup.py build
cd ../server
%{__python36} setup.py build
cd ../client/python
%{__python36} setup.py build
cd ../../client/java
ant
cd ../../
#ls -lR

%install
cd common
mkdir -p $RPM_BUILD_ROOT/etc/init.d
mkdir -p $RPM_BUILD_ROOT/var/lib/baltrad/bdb_storage
mkdir -p $RPM_BUILD_ROOT/var/run/baltrad
%{__python36} setup.py install --skip-build --root $RPM_BUILD_ROOT
cd ../server
%{__python36} setup.py install --skip-build --root $RPM_BUILD_ROOT
cp etc/bdbserver $RPM_BUILD_ROOT/etc/init.d/ 
cd ../client/python
%{__python36} setup.py install --skip-build --root $RPM_BUILD_ROOT
cd ../../client/java
mkdir -p $RPM_BUILD_ROOT%{_prefix}/share/baltrad/baltrad-db/java
cp -p dist/*.jar $RPM_BUILD_ROOT%{_prefix}/share/baltrad/baltrad-db/java/
mkdir -p $RPM_BUILD_ROOT%{_prefix}/share/baltrad/baltrad-db/java/libs
# FIXME: License files?
cp -p lib/commons/commons-lang3-3.1.jar $RPM_BUILD_ROOT%{_prefix}/share/baltrad/baltrad-db/java/libs
cp -p lib/joda-time/joda-time-2.0.jar $RPM_BUILD_ROOT%{_prefix}/share/baltrad/baltrad-db/java/libs

%post
BALTRAD_USER="baltrad"
BALTRAD_GROUP="baltrad"

#[ # Reading value of  SMHI_MODE. Handles enviroments: utv, test and prod where prod is default This is just for testing & development purposes
#-f /etc/profile.d/smhi.sh ] && . /etc/profile.d/smhi.sh

# This code is uniquely defined for internal use at SMHI so that we can automatically test
# and/or deploy the software. However, the default behaviour should always be that baltrad
# uses a system user.
# SMHI_MODE contains utv,test,prod.
if [[ -f /etc/profile.d/smhi.sh ]]; then
  BALTRAD_GROUP=baltradg
  . /etc/profile.d/smhi.sh
  if [[ "$SMHI_MODE" = "utv" ]];then
    BALTRAD_USER="baltra.u"
    BALTRAD_GROUP="baltragu"
  elif [[ "$SMHI_MODE" = "test" ]];then
    BALTRAD_USER="baltra.t"
    BALTRAD_GROUP="baltragt"
  fi
  TMPFILE=`mktemp`
  cat /etc/init.d/bdbserver | sed -e"s/BALTRAD_USER=baltrad/BALTRAD_USER=baltra.u/g" | sed -e"s/BALTRAD_GROUP=baltrad/BALTRAD_GROUP=baltragu/g" > $TMPFILE
  cat $TMPFILE > /etc/init.d/bdbserver
  chmod 755 /etc/init.d/bdbserver
  \rm -f $TMPFILE 
else
  if ! getent group $BALTRAD_GROUP > /dev/null; then
    groupadd --system $BALTRAD_GROUP
  fi

  if ! getent passwd "$BALTRAD_USER" > /dev/null; then
    adduser --system --home /var/lib/baltrad --no-create-home --shell /bin/bash -g $BALTRAD_GROUP $BALTRAD_USER
  fi
fi

mkdir -p /var/log/baltrad
chmod 0775 /var/log/baltrad
mkdir -p /var/run/baltrad
chmod 0775 /var/run/baltrad

chown root:$BALTRAD_GROUP /var/log/baltrad
chown root:$BALTRAD_GROUP /var/run/baltrad
chown -R $BALTRAD_USER:$BALTRAD_GROUP /var/lib/baltrad/bdb_storage

%files
# Why is %{_prefix} in buildroot?
/usr/bin/baltrad-bdb-client
/usr/bin/baltrad-bdb-create
/usr/bin/baltrad-bdb-drop
/usr/bin/baltrad-bdb-server
/usr/bin/baltrad-bdb-upgrade
/usr/bin/baltrad-bdb-migrate-db
/etc/init.d/bdbserver
%{bdb_site_install_dir}/baltrad/bdbcommon
%{bdb_site_install_dir}/baltrad/bdbclient
%{bdb_site_install_dir}/baltrad/bdbserver
#%{bdb_site_install_dir}/baltrad/bdbcommon/*.py
#%{bdb_site_install_dir}/baltrad/bdbcommon/*.pyc
#%{bdb_site_install_dir}/baltrad/bdbcommon/*.pyo
#%{bdb_site_install_dir}/baltrad/bdbcommon/oh5/*.py
#%{bdb_site_install_dir}/baltrad/bdbcommon/oh5/*.pyc
#%{bdb_site_install_dir}/baltrad/bdbcommon/oh5/*.pyo
#%{bdb_site_install_dir}/baltrad/bdbclient/*.py
#%{bdb_site_install_dir}/baltrad/bdbclient/*.pyc
#%{bdb_site_install_dir}/baltrad/bdbclient/*.pyo
#%{bdb_site_install_dir}/baltrad/bdbserver/*.py
#%{bdb_site_install_dir}/baltrad/bdbserver/*.pyc
#%{bdb_site_install_dir}/baltrad/bdbserver/*.pyo
#%{bdb_site_install_dir}/baltrad/bdbserver/sqla/*.py
#%{bdb_site_install_dir}/baltrad/bdbserver/sqla/*.pyc
#%{bdb_site_install_dir}/baltrad/bdbserver/sqla/*.pyo
#%{bdb_site_install_dir}/baltrad/bdbserver/sqla/migrate/*.py
#%{bdb_site_install_dir}/baltrad/bdbserver/sqla/migrate/*.pyc
#%{bdb_site_install_dir}/baltrad/bdbserver/sqla/migrate/*.pyo
#%{bdb_site_install_dir}/baltrad/bdbserver/sqla/migrate/migrate.cfg
#%{bdb_site_install_dir}/baltrad/bdbserver/sqla/migrate/versions/*.py
#%{bdb_site_install_dir}/baltrad/bdbserver/sqla/migrate/versions/*.pyc
#%{bdb_site_install_dir}/baltrad/bdbserver/sqla/migrate/versions/*.pyo
#%{bdb_site_install_dir}/baltrad/bdbserver/web/*.py
#%{bdb_site_install_dir}/baltrad/bdbserver/web/*.pyc
#%{bdb_site_install_dir}/baltrad/bdbserver/web/*.pyo
# Investigate the different paths and at least split these up amongst split packages
%{bdb_site_install_dir}/baltrad.*.pth
%{bdb_site_install_dir}/baltrad.*dev0-*.egg-info/*
/var/lib/baltrad/bdb_storage

%files java
%{_prefix}/share/baltrad/baltrad-db/java/*.jar

%files external
%{_prefix}/share/baltrad/baltrad-db/java/libs/commons-lang3-3.1.jar
%{_prefix}/share/baltrad/baltrad-db/java/libs/joda-time-2.0.jar
