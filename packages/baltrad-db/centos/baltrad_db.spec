%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%define _prefix /usr

Name: baltrad-db
Version: %{version}
Release: %{snapshot}%{?dist}
Summary: BaltradDB
License: GPL-3 and LGPL-3
URL: http://www.baltrad.eu/
Patch1: baltrad_db_server_setup.patch
Source0: %{name}-%{version}.tar.gz
BuildRequires: python2-devel
BuildRequires: python-distribute
BuildRequires: java-1.8.0-openjdk-devel
BuildRequires: ant
BuildRequires: jpackage-utils
Requires: hlhdf
Requires: hlhdf-python
Requires: python
Requires: python-progressbar
Requires: python-psycopg2
Requires: python-migrate
Requires: python-werkzeug
Requires: python-daemon >= 1.6
Requires: python-keyczar
Requires: python-distribute
Requires: postgresql
Requires: python-sqlalchemy
Requires: python-cherrypy >= 3.0.0

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
%{__python} setup.py build
cd ../server
%{__python} setup.py build
cd ../client/python
%{__python} setup.py build
cd ../../client/java
ant
cd ../../
ls -lR

%install
cd common
mkdir -p $RPM_BUILD_ROOT/etc/init.d
mkdir -p $RPM_BUILD_ROOT/var/lib/baltrad/bdb_storage
mkdir -p $RPM_BUILD_ROOT/var/run/baltrad
%{__python} setup.py install --skip-build --root $RPM_BUILD_ROOT
cd ../server
%{__python} setup.py install --skip-build --root $RPM_BUILD_ROOT
cp etc/bdbserver $RPM_BUILD_ROOT/etc/init.d/ 
cd ../client/python
%{__python} setup.py install --skip-build --root $RPM_BUILD_ROOT
cd ../../client/java
mkdir -p $RPM_BUILD_ROOT%{_prefix}/share/baltrad/baltrad-db/java
cp -p dist/*.jar $RPM_BUILD_ROOT%{_prefix}/share/baltrad/baltrad-db/java/
mkdir -p $RPM_BUILD_ROOT%{_prefix}/share/baltrad/baltrad-db/java/libs
# FIXME: License files?
cp -p lib/commons/commons-lang3-3.1.jar $RPM_BUILD_ROOT%{_prefix}/share/baltrad/baltrad-db/java/libs
cp -p lib/joda-time/joda-time-2.0.jar $RPM_BUILD_ROOT%{_prefix}/share/baltrad/baltrad-db/java/libs

%post
if ! getent passwd baltrad > /dev/null; then
  adduser --system --home /var/lib/baltrad --no-create-home \
    --shell /bin/bash -g baltrad baltrad
fi
    
if ! getent group baltrad > /dev/null; then
  groupadd --system baltrad
fi
  
if ! id -Gn baltrad | grep -qw baltrad; then
  adduser baltrad baltrad
fi

mkdir -p /var/log/baltrad
chmod 1775 /var/log/baltrad
chown root:baltrad /var/log/baltrad

mkdir -p /var/run/baltrad
chmod 1775 /var/run/baltrad
chown root:baltrad /var/run/baltrad


%files
# Why is %{_prefix} in buildroot?
/usr/bin/baltrad-bdb-client
/usr/bin/baltrad-bdb-create
/usr/bin/baltrad-bdb-drop
/usr/bin/baltrad-bdb-server
/usr/bin/baltrad-bdb-upgrade
/usr/bin/baltrad-bdb-migrate-db
/etc/init.d/bdbserver
%{python_sitelib}/baltrad/bdbcommon/*.py
%{python_sitelib}/baltrad/bdbcommon/*.pyc
%{python_sitelib}/baltrad/bdbcommon/*.pyo
%{python_sitelib}/baltrad/bdbcommon/oh5/*.py
%{python_sitelib}/baltrad/bdbcommon/oh5/*.pyc
%{python_sitelib}/baltrad/bdbcommon/oh5/*.pyo
%{python_sitelib}/baltrad/bdbclient/*.py
%{python_sitelib}/baltrad/bdbclient/*.pyc
%{python_sitelib}/baltrad/bdbclient/*.pyo
%{python_sitelib}/baltrad/bdbserver/*.py
%{python_sitelib}/baltrad/bdbserver/*.pyc
%{python_sitelib}/baltrad/bdbserver/*.pyo
%{python_sitelib}/baltrad/bdbserver/sqla/*.py
%{python_sitelib}/baltrad/bdbserver/sqla/*.pyc
%{python_sitelib}/baltrad/bdbserver/sqla/*.pyo
%{python_sitelib}/baltrad/bdbserver/sqla/migrate/*.py
%{python_sitelib}/baltrad/bdbserver/sqla/migrate/*.pyc
%{python_sitelib}/baltrad/bdbserver/sqla/migrate/*.pyo
%{python_sitelib}/baltrad/bdbserver/sqla/migrate/migrate.cfg
%{python_sitelib}/baltrad/bdbserver/sqla/migrate/versions/*.py
%{python_sitelib}/baltrad/bdbserver/sqla/migrate/versions/*.pyc
%{python_sitelib}/baltrad/bdbserver/sqla/migrate/versions/*.pyo
%{python_sitelib}/baltrad/bdbserver/web/*.py
%{python_sitelib}/baltrad/bdbserver/web/*.pyc
%{python_sitelib}/baltrad/bdbserver/web/*.pyo
# Investigate the different paths and at least split these up amongst split packages
%{python_sitelib}/baltrad.*.pth
%{python_sitelib}/baltrad.*dev-*.egg-info/*
%attr(-,baltrad,baltrad) /var/lib/baltrad/bdb_storage

%files java
%{_prefix}/share/baltrad/baltrad-db/java/*.jar

%files external
%{_prefix}/share/baltrad/baltrad-db/java/libs/commons-lang3-3.1.jar
%{_prefix}/share/baltrad/baltrad-db/java/libs/joda-time-2.0.jar
