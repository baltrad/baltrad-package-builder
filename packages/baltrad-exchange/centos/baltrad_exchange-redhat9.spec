%global debug_package %{nil}
%{!?__python3: %global __python3 /usr/bin/python3.9}
%{!?python3_sitelib: %global python3_sitelib %(%{__python3} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}
%{!?bdb_site_install_dir: %global bdb_site_install_dir /usr/lib/python3.9/site-packages}
%define _prefix /usr

Name: baltrad-exchange
Version: %{version}
Release: %{snapshot}%{?dist}
Summary: Baltrad Exchange
License: GPL-3 and LGPL-3
URL: http://www.baltrad.eu/
Patch1: baltrad-exchange_service.patch
Patch2: baltrad_setup_redhat95_cherrypy.patch
Source0: %{name}-%{version}.tar.gz
Source1: baltrad-exchange-tmpfiles.d.conf
BuildRequires: python3-devel
BuildRequires: systemd
Requires: baltrad-db
Requires: hlhdf-python
Requires: python3
Requires: python3-daemon
Requires: python3-pyasn1
Requires: python3-setuptools
Requires: python3-sqlalchemy
Requires: python3-cherrypy
Requires: python3-paramiko
Requires: python3-scp
Requires: python3-inotify
Requires: baltrad-crypto
Requires: baltrad-utils

%description
Provides exchange functionality for the baltrad network.

%prep
%setup -q
%patch1 -p1
%patch2 -p1

%build
%{__python3} -v setup.py build

%install
mkdir -p $RPM_BUILD_ROOT/var/cache/baltrad/exchange
mkdir -p $RPM_BUILD_ROOT/run/baltrad
mkdir -p $RPM_BUILD_ROOT/var/lib/baltrad/exchange
mkdir -p $RPM_BUILD_ROOT/etc/baltrad/exchange
mkdir -p $RPM_BUILD_ROOT/etc/baltrad/exchange/etc
mkdir -p $RPM_BUILD_ROOT/etc/baltrad/exchange/config/examples

install -p -D -m 0644 %{SOURCE1} %{buildroot}%{_tmpfilesdir}/baltrad-exchange.conf
%{__python3} -v setup.py install --skip-build --root $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/%{_unitdir}
cp etc/baltrad-exchange.service $RPM_BUILD_ROOT/%{_unitdir}
cp etc/*.json $RPM_BUILD_ROOT/etc/baltrad/exchange/config/examples/
cp etc/baltrad-exchange.properties $RPM_BUILD_ROOT/etc/baltrad/exchange/etc/

%pre
if [ "$1" = "2" ]; then
  systemctl stop baltrad-exchange || :
fi

%post
BALTRAD_USER=baltrad
BALTRAD_GROUP=baltrad
CREATE_BALTRAD_USER=false

if [[ -f /etc/baltrad/baltrad.rc ]]; then
  . /etc/baltrad/baltrad.rc
fi

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
cat %{_unitdir}/baltrad-exchange.service | sed -e"s/^User=baltrad.*/User=$BALTRAD_USER/g" | sed -e"s/^Group=baltrad.*/Group=$BALTRAD_GROUP/g" > $TMPFILE
cat $TMPFILE > %{_unitdir}/baltrad-exchange.service
chmod 644 %{_unitdir}/baltrad-exchange.service
\rm -f $TMPFILE
echo "d /run/baltrad 0775 $BALTRAD_USER $BALTRAD_GROUP -" > %{_tmpfilesdir}/baltrad-exchange.conf

chmod 0775 /run/baltrad
chown $BALTRAD_USER:$BALTRAD_GROUP /run/baltrad
#chown root:$BALTRAD_GROUP /run/baltrad

chmod 0775 /var/log/baltrad
chown $BALTRAD_USER:$BALTRAD_GROUP /var/log/baltrad
#chown root:$BALTRAD_GROUP /var/log/baltrad

chmod 0775 /var/lib/baltrad
chown $BALTRAD_USER:$BALTRAD_GROUP /var/lib/baltrad
chmod 0775 /var/lib/baltrad/exchange
chown $BALTRAD_USER:$BALTRAD_GROUP /var/lib/baltrad/exchange

chmod 0775 /var/cache/baltrad/exchange
chmod 0775 /var/cache/baltrad
chown $BALTRAD_USER:$BALTRAD_GROUP /var/cache/baltrad
#chown root:$BALTRAD_GROUP /var/cache/baltrad
chown $BALTRAD_USER:$BALTRAD_GROUP /var/cache/baltrad/exchange

chmod 0775 /etc/baltrad/exchange
chown $BALTRAD_USER:$BALTRAD_GROUP /etc/baltrad/exchange
#chown root:$BALTRAD_GROUP /etc/baltrad/exchange

chmod 0775 /etc/baltrad/exchange/config
chown $BALTRAD_USER:$BALTRAD_GROUP /etc/baltrad/exchange/config
#chown root:$BALTRAD_GROUP /etc/baltrad/exchange/config

chmod 0775 /etc/baltrad/exchange/etc
chown $BALTRAD_USER:$BALTRAD_GROUP /etc/baltrad/exchange/etc
#chown root:$BALTRAD_GROUP /etc/baltrad/exchange/etc
chmod 0660 /etc/baltrad/exchange/etc/baltrad-exchange.properties
chown $BALTRAD_USER:$BALTRAD_GROUP /etc/baltrad/exchange/etc/baltrad-exchange.properties
#chown root:$BALTRAD_GROUP /etc/baltrad/exchange/etc/baltrad-exchange.properties

chmod 0775 /etc/baltrad/exchange/etc
chown $BALTRAD_USER:$BALTRAD_GROUP /etc/baltrad/exchange/config/examples
#chown root:$BALTRAD_GROUP /etc/baltrad/exchange/config/examples


if [ "$1" = "2" ] ; then  # upgrade
  #restart app on upgrade
  /usr/bin/systemctl daemon-reload
fi

if [[ -f /usr/bin/baltrad-exchange-server ]]; then
  echo "Found file /usr/bin/baltrad-exchange-server changing permission"
  chown $BALTRAD_USER:$BALTRAD_GROUP /usr/bin/baltrad-exchange-server
fi

if [[ -f /usr/lib/python3.9/site-packages/bexchange/server_main.py ]]; then
  echo "Found file /usr/lib/python3.9/site-packages/bexchange/server_main.py changing permission"
  chown $BALTRAD_USER:$BALTRAD_GROUP /usr/lib/python3.9/site-packages/bexchange/server_main.py
fi

%preun
systemctl stop baltrad-exchange || :
%systemd_preun baltrad-exchange.service || :

%postun
%systemd_postun baltrad-exchange.service || :

%files
/usr/bin/baltrad-exchange-client
/usr/bin/baltrad-exchange-server
/usr/bin/baltrad-exchange-config
/usr/bin/baltrad-exchange-zmq
%{_unitdir}/baltrad-exchange.service
%{_tmpfilesdir}/baltrad-exchange.conf
%{bdb_site_install_dir}/bexchange
# Investigate the different paths and at least split these up amongst split packages
%{bdb_site_install_dir}/bexchange-*.pth
%{bdb_site_install_dir}/bexchange-*.egg-info/*
/var/cache/baltrad/exchange
/var/lib/baltrad/exchange
%config(noreplace) /etc/baltrad/exchange


