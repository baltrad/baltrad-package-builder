%{!?__python3: %global __python3 /usr/bin/python3.9}
%define _sitelib  /usr/lib/python3.9/site-packages/
%define _prefix /usr/lib/bropo

Name: bropo
Version: %{version}
Release: %{snapshot}%{?dist}
Summary: Baltrad version of the FMI Anomaly detection and removal package ROPO
License: LGPL-3
URL: http://www.baltrad.eu/
Source0: %{name}-%{version}.tar.gz
# Dependencies to python follows from rave-devel and rave
BuildRequires: rave-devel
BuildRequires: libpng-devel
Requires: rave
Conflicts: bropo-py27

%description
bRopo is an adaption of the existing FMI software package ROPO.
The bRopo is adapted to integrate with the RAVE framework and also
to provide users with a Python interface.

%package devel
Summary: bRopo development files
Group: Development/Libraries
Requires: %{name} = %{version}-%{release}
Conflicts: bropo-py27-devel

%description devel
RAVE development headers and libraries.


%prep
%setup -q

%build
%configure --with-rave=/usr/lib/rave
make

%install
make install DESTDIR=%{buildroot}
%py_byte_compile %{__python3} %{buildroot}/usr/lib/bropo/share/bropo/pyropo/ || :
mkdir -p %{buildroot}/etc/baltrad/ropo
mv %{buildroot}/usr/lib/bropo/share/bropo/config/ropo_options.xml %{buildroot}/etc/baltrad/ropo/ropo_options.xml
ln -s ../../../../../../etc/baltrad/ropo/ropo_options.xml %{buildroot}/usr/lib/bropo/share/bropo/config/ropo_options.xml

mkdir -p %{buildroot}/etc/ld.so.conf.d/
mkdir -p %{buildroot}%{_sitelib}

echo "/usr/lib/bropo/lib" >> %{buildroot}/etc/ld.so.conf.d/bropo.conf
mv %{buildroot}/usr/lib64/python3.9/site-packages/pyropo.pth %{buildroot}%{_sitelib}

%post
BALTRAD_USER=baltrad
BALTRAD_GROUP=baltrad

if [[ -f /etc/baltrad/baltrad.rc ]]; then
  . /etc/baltrad/baltrad.rc
fi

chown root:$BALTRAD_GROUP /etc/baltrad/ropo
chown $BALTRAD_USER:$BALTRAD_GROUP /etc/baltrad/ropo/ropo_options.xml

/sbin/ldconfig
TMPNAME=`mktemp /tmp/XXXXXXXXXX.py`
  
cat <<EOF > $TMPNAME
from rave_pgf_quality_registry_mgr import rave_pgf_quality_registry_mgr
a = rave_pgf_quality_registry_mgr("/etc/baltrad/rave/etc/rave_pgf_quality_registry.xml")
a.remove_plugin("ropo")
a.add_plugin("ropo", "ropo_quality_plugin", "ropo_quality_plugin")
a.save("/etc/baltrad/rave/etc/rave_pgf_quality_registry.xml")
EOF
%{__python3} $TMPNAME
\rm -f $TMPNAME

%postun -p /sbin/ldconfig

%files
%{_prefix}/bin/ropo
%{_prefix}/lib/libbropo.so
%{_prefix}/share/bropo/config/ropo_options.xml
%{_prefix}/share/bropo/pyropo/ropo_*.py
%{_prefix}/share/bropo/pyropo/__pycache__/*.pyc
%{_sitelib}/pyropo.pth
%{_prefix}/share/bropo/pyropo/_fmiimage.so
%{_prefix}/share/bropo/pyropo/_ropogenerator.so
/etc/ld.so.conf.d/bropo.conf
%config /etc/baltrad/ropo/ropo_options.xml

%files devel
%{_prefix}/include/*.h
