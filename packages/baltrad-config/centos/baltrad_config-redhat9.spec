%global debug_package %{nil}
%{!?__python3: %global __python3 /usr/bin/python3.9}
%{!?python3_sitelib: %global python3_sitelib %(%{__python3} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}
%define _prefix /usr

Name: baltrad-config
Version: %{version}
Release: %{snapshot}%{?dist}
Summary: Baltrad Config
License: GPL-3 and LGPL-3
URL: http://www.baltrad.eu/
Source0: %{name}-%{version}.tar.gz
BuildRequires: python3-devel
Requires: python3
Requires: baltrad-crypto
Requires: SMHI-python3-radar_pyutils

Conflicts: baltrad-config-py27

%description
Provides configuration features for the baltrad system

%prep
%setup -q

%build
%{__python3} setup.py build

%install
%{__python3} setup.py install --skip-build --root $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/usr/share/doc/baltrad-config
cp README.bltcfg $RPM_BUILD_ROOT/usr/share/doc/baltrad-config/README.bltcfg

%post
BALTRAD_USER=baltrad
BALTRAD_GROUP=baltrad
CREATE_BALTRAD_USER=true

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

if [[ -L /etc/baltrad/bltnode-keys ]]; then
  echo "/etc/baltrad/bltnode-keys exists!"
elif [[ -d /etc/baltrad/bltnode-keys ]]; then
  echo "/etc/baltrad/bltnode-keys exists!"
  chmod 0775 /etc/baltrad/bltnode-keys
  chown root:$BALTRAD_GROUP /etc/baltrad/bltnode-keys
elif [[ -f /etc/baltrad/bltnode-keys ]]; then
  echo "/etc/baltrad/bltnode-keys exists!"
  chmod 0775 /etc/baltrad/bltnode-keys
  chown root:$BALTRAD_GROUP /etc/baltrad/bltnode-keys
else
  echo "/etc/baltrad/bltnode-keys does not exist, creating it!"
  mkdir -p /etc/baltrad/bltnode-keys
  chmod 0775 /etc/baltrad/bltnode-keys
  chown root:$BALTRAD_GROUP /etc/baltrad/bltnode-keys
fi

%files
/usr/bin/baltrad-config
/usr/bin/bltcfg
/usr/bin/bltgroovyroute
/usr/lib/python3.9/site-packages/baltrad/config
/usr/lib/python3.9/site-packages/baltrad.*.pth
/usr/lib/python3.9/site-packages/baltrad.*dev0-*.egg-info/*
/usr/share/doc/baltrad-config/README.bltcfg
