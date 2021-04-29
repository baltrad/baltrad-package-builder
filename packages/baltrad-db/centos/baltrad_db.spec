%{!?__python36: %global __python36 /usr/bin/python3.6}
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
Patch2: bdbserver_service.patch
Source0: %{name}-%{version}.tar.gz
Source1: baltrad-db-tmpfiles.d.conf
BuildRequires: python36-devel
BuildRequires: python-distribute
BuildRequires: java-1.8.0-openjdk-devel
BuildRequires: ant
BuildRequires: jpackage-utils
BuildRequires: systemd
Requires: hlhdf
Requires: hlhdf-python
Requires: python36
Requires: python36-progressbar33-blt
Requires: python36-psycopg2-blt
Requires: python36-werkzeug-blt
Requires: python36-daemon-blt
Requires: python36-pyasn1-blt
Requires: python36-keyczar-blt
Requires: python36-setuptools
Requires: python36-sqlalchemy-blt
Requires: python36-sqlalchemy-migrate-blt
Requires: python36-cherrypy-blt
Requires: python36-jprops-blt
Requires: python36-pycrypto-blt
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
%patch2 -p1

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
install -p -D -m 0644 %{SOURCE1} %{buildroot}%{_tmpfilesdir}/baltrad-db.conf
%{__python36} setup.py install --skip-build --root $RPM_BUILD_ROOT
cd ../server
%{__python36} setup.py install --skip-build --root $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/%{_unitdir}
cp etc/bdbserver.service $RPM_BUILD_ROOT/%{_unitdir}
cd ../client/python
%{__python36} setup.py install --skip-build --root $RPM_BUILD_ROOT
cd ../../client/java
mkdir -p $RPM_BUILD_ROOT%{_prefix}/share/baltrad/baltrad-db/java
cp -p dist/*.jar $RPM_BUILD_ROOT%{_prefix}/share/baltrad/baltrad-db/java/
mkdir -p $RPM_BUILD_ROOT%{_prefix}/share/baltrad/baltrad-db/java/libs
# FIXME: License files?
cp -p lib/commons/commons-lang3-3.1.jar $RPM_BUILD_ROOT%{_prefix}/share/baltrad/baltrad-db/java/libs
cp -p lib/joda-time/joda-time-2.0.jar $RPM_BUILD_ROOT%{_prefix}/share/baltrad/baltrad-db/java/libs

%pre
if [ "$1" = "2" ]; then
  systemctl stop bdbserver || :
fi

%post
BALTRAD_USER=baltrad
BALTRAD_GROUP=baltrad
CREATE_BALTRAD_USER=true

if [[ -f /etc/baltrad/baltrad.rc ]]; then
  . /etc/baltrad/baltrad.rc
fi

#echo "BALTRAD_USER=$BALTRAD_USER, BALTRAD_GROUP=$BALTRAD_GROUP, CREATE_BALTRAD_USER=$CREATE_BALTRAD_USER"

if [[ "$CREATE_BALTRAD_USER" = "true" ]]; then
  if ! getent group $BALTRAD_GROUP > /dev/null; then
    groupadd --system $BALTRAD_GROUP
  fi

  if ! getent passwd "$BALTRAD_USER" > /dev/null; then
    adduser --system --home /var/lib/baltrad --no-create-home --shell /bin/bash -g $BALTRAD_GROUP $BALTRAD_USER
  fi
fi

if [[ "$BALTRAD_USER" == *\.* ]]; then
  echo "User id $BALTRAD_USER contains a ., replacing with numerical user id."
  BALTRAD_USER=`id -u $BALTRAD_USER`
fi

TMPFILE=`mktemp`
cat %{_unitdir}/bdbserver.service | sed -e"s/^User=baltrad.*/User=$BALTRAD_USER/g" | sed -e"s/^Group=baltrad.*/Group=$BALTRAD_GROUP/g" > $TMPFILE
cat $TMPFILE > %{_unitdir}/bdbserver.service
chmod 644 %{_unitdir}/bdbserver.service
\rm -f $TMPFILE
echo "d /var/run/baltrad 0775 root $BALTRAD_GROUP -" > %{_tmpfilesdir}/baltrad-db.conf

mkdir -p /var/log/baltrad
chmod 0775 /var/log/baltrad
mkdir -p /var/run/baltrad
chmod 0775 /var/run/baltrad

chown root:$BALTRAD_GROUP /var/log/baltrad
chown root:$BALTRAD_GROUP /var/run/baltrad
chown -R $BALTRAD_USER:$BALTRAD_GROUP /var/lib/baltrad/bdb_storage

%preun
systemctl stop bdbserver || :
%systemd_preun bdbserver.service || :

%postun
%systemd_postun bdbserver.service || :

%files
# Why is %{_prefix} in buildroot?
/usr/bin/baltrad-bdb-client
/usr/bin/baltrad-bdb-create
/usr/bin/baltrad-bdb-drop
/usr/bin/baltrad-bdb-server
/usr/bin/baltrad-bdb-upgrade
/usr/bin/baltrad-bdb-migrate-db
%{_unitdir}/bdbserver.service
%{_tmpfilesdir}/baltrad-db.conf
%{bdb_site_install_dir}/baltrad/bdbcommon
%{bdb_site_install_dir}/baltrad/bdbclient
%{bdb_site_install_dir}/baltrad/bdbserver
# Investigate the different paths and at least split these up amongst split packages
%{bdb_site_install_dir}/baltrad.*.pth
%{bdb_site_install_dir}/baltrad.*dev0-*.egg-info/*
/var/lib/baltrad/bdb_storage

%files java
%{_prefix}/share/baltrad/baltrad-db/java/*.jar

%files external
%{_prefix}/share/baltrad/baltrad-db/java/libs/commons-lang3-3.1.jar
%{_prefix}/share/baltrad/baltrad-db/java/libs/joda-time-2.0.jar
