%{!?__python36: %global __python36 /usr/bin/python3.6}
%{!?python36_sitelib: %global python36_sitelib %(%{__python36} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}
%define _prefix /usr/lib/beamb

Name: beamb
Version: %{version}
Release: %{snapshot}%{?dist}
Summary: beamb
License: LGPL-3
URL: http://www.baltrad.eu/
Source0: %{name}-%{version}.tar.gz
#Dependencies 
BuildRequires: rave-devel
BuildRequires: rave
Requires: rave
Conflicts: beamb-py27

%description
Determination of, and correction for, beam blockage caused by topography

%package devel
Summary: beamb development files
Group: Development/Libraries
Requires: %{name} = %{version}-%{release}
Requires: rave-devel
Conflicts: beamb-py27-devel

%description devel
Beamb development headers and libraries.

%prep
%setup -q

%build
%configure --prefix=/usr/lib/beamb --with-rave=/usr/lib/rave --localstatedir=/var
make

%install
make install DESTDIR=%{buildroot}
%py_byte_compile %{__python36} %{buildroot}/usr/lib/beamb/share/beamb/pybeamb/ || :
mkdir -p %{buildroot}%{python36_sitelib}
#mkdir -p %{buildroot}/usr/lib/python2.7/dist-packages
mkdir -p %{buildroot}/usr/lib/beamb
mkdir -p %{buildroot}/etc/ld.so.conf.d
mkdir -p %{buildroot}/var/cache/beamb
echo "/usr/lib/beamb/lib">> %{buildroot}/etc/ld.so.conf.d/beamb.conf

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

chown -R $BALTRAD_USER:$BALTRAD_GROUP /var/cache/beamb

/sbin/ldconfig
TMPNAME=`mktemp /tmp/XXXXXXXXXX.py`
  
cat <<EOF > $TMPNAME
from rave_pgf_quality_registry_mgr import rave_pgf_quality_registry_mgr
a = rave_pgf_quality_registry_mgr("/etc/baltrad/rave/etc/rave_pgf_quality_registry.xml")
a.remove_plugin("beamb")
a.add_plugin("beamb", "beamb_quality_plugin", "beamb_quality_plugin")
a.save("/etc/baltrad/rave/etc/rave_pgf_quality_registry.xml")
EOF
%{__python36} $TMPNAME
\rm -f $TMPNAME

%postun -p /sbin/ldconfig

%files
%{_prefix}/bin/beamb
%{_prefix}/lib/libbeamb.so
%{_prefix}/share/beamb/data/gtopo30/*
# Python package?
%{_prefix}/share/beamb/pybeamb/*.so
%{_prefix}/share/beamb/pybeamb/*.py
%{_prefix}/share/beamb/pybeamb/__pycache__/*.pyc
#%{_prefix}/share/beamb/pybeamb/*.pyo
%{python36_sitelib}/pybeamb.pth
/var/cache/beamb
/etc/ld.so.conf.d/beamb.conf

%files devel
%{_prefix}/include/*.h
