%global debug_package %{nil}
%{!?__python36: %global __python36 /usr/bin/python3.6}
%{!?python36_sitelib: %global python36_sitelib %(%{__python36} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}
%define _prefix /usr

Name: baltrad-config
Version: %{version}
Release: %{snapshot}%{?dist}
Summary: Baltrad Config
License: GPL-3 and LGPL-3
URL: http://www.baltrad.eu/
Source0: %{name}-%{version}.tar.gz
BuildRequires: python36-devel
Requires: python36
Conflicts: baltrad-config-py27

%description
Provides configuration features for the baltrad system

%prep
%setup -q

%build
%{__python36} setup.py build

%install
%{__python36} setup.py install --skip-build --root $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/etc/baltrad/bltnode-keys

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
else
  if ! getent group $BALTRAD_GROUP > /dev/null; then
    groupadd --system $BALTRAD_GROUP
  fi

  if ! getent passwd "$BALTRAD_USER" > /dev/null; then
    adduser --system --home /var/lib/baltrad --no-create-home --shell /bin/bash -g $BALTRAD_GROUP $BALTRAD_USER
  fi
fi

#mkdir -p /etc/baltrad/bltnode-keys
chmod 0775 /etc/baltrad/bltnode-keys
chown root:$BALTRAD_GROUP /etc/baltrad/bltnode-keys

#\rm -fr /etc/baltrad/bltnode-keys/*
#\rm -f /etc/baltrad/bltnode.properties


%files
/usr/bin/baltrad-config
%config /etc/baltrad/bltnode-keys
/usr/lib/python3.6/site-packages/baltrad/config
/usr/lib/python3.6/site-packages/baltrad.*.pth
/usr/lib/python3.6/site-packages/baltrad.*dev0-*.egg-info/*
