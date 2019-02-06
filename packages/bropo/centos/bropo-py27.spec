%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%define _prefix /usr/lib/bropo

Name: bropo-py27
Version: %{version}
Release: %{snapshot}%{?dist}
Summary: Baltrad version of the FMI Anomaly detection and removal package ROPO
License: GPL-3 and LGPL-3
URL: http://www.baltrad.eu/
Source0: %{name}-%{version}.tar.gz
BuildRequires: rave-devel
BuildRequires: libpng-devel
# pyropo
BuildRequires: python-devel
Requires: rave
Conflicts: bropo

%description
bRopo is an adaption of the existing FMI software package ROPO.
The bRopo is adapted to integrate with the RAVE framework and also
to provide users with a Python interface.

%package devel
Summary: bRopo development files
Group: Development/Libraries
Requires: %{name} = %{version}-%{release}
Conflicts: bropo-devel

%description devel
RAVE development headers and libraries.

%prep
%setup -q

%build
%configure --with-rave=/usr/lib/rave
make

%install
make install DESTDIR=%{buildroot}
mkdir -p %{buildroot}/etc/ld.so.conf.d/
echo "/usr/lib/bropo/lib" >> %{buildroot}/etc/ld.so.conf.d/bropo.conf

%post
/sbin/ldconfig
TMPNAME=`mktemp /tmp/XXXXXXXXXX.py`
  
cat <<EOF > $TMPNAME
from rave_pgf_quality_registry_mgr import rave_pgf_quality_registry_mgr
a = rave_pgf_quality_registry_mgr("/etc/baltrad/rave/etc/rave_pgf_quality_registry.xml")
a.remove_plugin("ropo")
a.add_plugin("ropo", "ropo_quality_plugin", "ropo_quality_plugin")
a.save("/etc/baltrad/rave/etc/rave_pgf_quality_registry.xml")
EOF
python $TMPNAME
\rm -f $TMPNAME

%postun -p /sbin/ldconfig

%files
%{_prefix}/bin/ropo
%{_prefix}/lib/libbropo.so
%{_prefix}/share/bropo/config/ropo_options.xml
%{_prefix}/share/bropo/pyropo/ropo_*.py
%{_prefix}/share/bropo/pyropo/ropo_*.pyc
%{_prefix}/share/bropo/pyropo/ropo_*.pyo
%{python_sitelib}/pyropo.pth
%{_prefix}/share/bropo/pyropo/_fmiimage.so
%{_prefix}/share/bropo/pyropo/_ropogenerator.so
/etc/ld.so.conf.d/bropo.conf

%files devel
%{_prefix}/include/*.h
