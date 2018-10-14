%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%define _prefix /usr/lib/beamb

Name: beamb
Version: %{version}
Release: %{snapshot}%{?dist}
Summary: beamb
License: GPL-3 and LGPL-3
URL: http://www.baltrad.eu/
Source0: %{name}-%{version}.tar.gz
BuildRequires: rave-devel
BuildRequires: hlhdf-devel
BuildRequires: python2-devel
Requires: rave

%description
Determination of, and correction for, beam blockage caused by topography

%package devel
Summary: beamb development files
Group: Development/Libraries
Requires: %{name} = %{version}-%{release}

%description devel
Beamb development headers and libraries.

%prep
%setup -q

%build
%configure --prefix=/usr/lib/beamb --with-rave=/usr/lib/rave --localstatedir=/var
make

%install
make install DESTDIR=%{buildroot}
mkdir -p %{buildroot}/usr/lib/python2.7/dist-packages
mkdir -p %{buildroot}/usr/lib/beamb
mkdir -p %{buildroot}/etc/ld.so.conf.d
echo "/usr/lib/beamb/lib">> %{buildroot}/etc/ld.so.conf.d/beamb.conf
cp %{buildroot}/usr/lib/python2.7/site-packages/pybeamb.pth %{buildroot}/usr/lib/python2.7/dist-packages

%post
/sbin/ldconfig
TMPNAME=`mktemp /tmp/XXXXXXXXXX.py`
  
cat <<EOF > $TMPNAME
from rave_pgf_quality_registry_mgr import rave_pgf_quality_registry_mgr
a = rave_pgf_quality_registry_mgr("/etc/baltrad/rave/etc/rave_pgf_quality_registry.xml")
a.remove_plugin("beamb")
a.add_plugin("beamb", "beamb_quality_plugin", "beamb_quality_plugin")
a.save("/etc/baltrad/rave/etc/rave_pgf_quality_registry.xml")
EOF
python $TMPNAME
\rm -f $TMPNAME

%postun -p /sbin/ldconfig

%files
%{_prefix}/bin/beamb
%{_prefix}/lib/libbeamb.so
%{_prefix}/share/beamb/data/gtopo30/*
# Python package?
%{_prefix}/share/beamb/pybeamb/*.so
%{_prefix}/share/beamb/pybeamb/*.py
%{_prefix}/share/beamb/pybeamb/*.pyc
%{_prefix}/share/beamb/pybeamb/*.pyo
%{python_sitelib}/pybeamb.pth
%attr(-, baltrad, baltrad) /var/cache/beamb
/usr/lib/python2.7/dist-packages
/etc/ld.so.conf.d/beamb.conf

%files devel
%{_prefix}/include/*.h
