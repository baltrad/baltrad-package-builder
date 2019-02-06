%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")}
%define _prefix /usr/lib/baltrad-wrwp

Name: baltrad-wrwp-py27
Version: %{version}
Release: %{snapshot}%{?dist}
Summary: Baltrad weather radar wind products
License: GPL-3 and LGPL-3
URL: http://www.baltrad.eu/
Patch1: make-for-atlas.patch
Source0: %{name}-%{version}.tar.gz
BuildRequires: hlhdf-devel
BuildRequires: hdf5-devel
BuildRequires: python2-devel
BuildRequires: numpy
BuildRequires: proj-devel
BuildRequires: rave
BuildRequires: rave-devel
BuildRequires: atlas-sse3
BuildRequires: lapack-devel
BuildRequires: blas-devel
BuildRequires: atlas-devel
BuildRequires: gsl-devel
Requires: rave
Requires: numpy
Requires: hlhdf
Requires: python2
Requires: proj-devel
Requires: rave
Requires: atlas-sse3
Requires: atlas
Conflicts: baltrad-wrwp

%description
Baltrad weather radar wind products

%package devel
Summary: Baltrad weather radar wind products development headers and libraries.
Group: Development/Libraries
Requires: %{name} = %{version}-%{release}
Conflicts: baltrad-wrwp-devel

%description devel

%package python
Summary: Baltrad weather radar wind products Python module
Requires: %{name} = %{version}-%{release}
%description python
Baltrad weather radar wind products Python module.

%prep
%setup -q
%patch1 -p1

%build
#objdump -TC /usr/lib64/atlas/libcblas.so.3
#ls -l /etc/ld.so.conf.d/atlas*
#cat /etc/ld.so.conf.d/atlas*
%configure --prefix=/usr/lib/baltrad-wrwp --with-rave=/usr/lib/rave --with-lapack=/usr/lib64 --with-lapacke=/usr/include/lapacke,/usr/lib64 --with-cblas=/usr/include,/usr/lib64/atlas --with-blas=/usr/lib64
make

%install
# FIXME: Why is this mkdir necessary?
# With full _prefix the custom installscripts think there was already an old version
# present and does some special things we may not want (migration to newer version)
rm -rf %{buildroot}
mkdir -p %{buildroot}/usr/lib/baltrad-wrwp
mkdir -p %{buildroot}%{_sysconfdir}/ld.so.conf.d
mkdir -p %{buildroot}/usr/lib/python2.7/site-packages
make install DESTDIR=%{buildroot}
echo "/usr/lib/baltrad-wrwp/lib" >> %{buildroot}%{_sysconfdir}/ld.so.conf.d/baltrad-wrwp.conf

%post
/sbin/ldconfig

%post python
TMPNAME=`mktemp /tmp/XXXXXXXXXX.py`
  
cat <<EOF > $TMPNAME
from rave_pgf_registry import PGF_Registry
a=PGF_Registry(filename="/etc/baltrad/rave/etc/rave_pgf_registry.xml")
a.deregister('eu.baltrad.beast.generatewrwp')
a.deregister('se.smhi.baltrad-wrwp.generatewrwp')
a.register('eu.baltrad.beast.generatewrwp', 'baltrad_wrwp_pgf_plugin', 'generate', 'Baltrad WRWP Plugin', 'fields','interval,maxheight,mindistance,maxdistance','minelevationangle,velocitythreshold')
a.register('se.smhi.baltrad-wrwp.generatewrwp', 'baltrad_wrwp_pgf_plugin', 'generate', 'Baltrad WRWP Plugin', 'fields','interval,maxheight,mindistance,maxdistance','minelevationangle,velocitythreshold')
EOF
python $TMPNAME
\rm -f $TMPNAME

%postun -p /sbin/ldconfig

%files
%{_prefix}/lib/libwrwp.so
%{_prefix}/bin/wrwp

%files devel
%{_prefix}/include/wrwp.h

%files python
%{_prefix}/share/wrwp/pywrwp/
/usr/lib/python2.7/site-packages/pywrwp.pth

%config(noreplace) %{_sysconfdir}/ld.so.conf.d/baltrad-wrwp.conf
