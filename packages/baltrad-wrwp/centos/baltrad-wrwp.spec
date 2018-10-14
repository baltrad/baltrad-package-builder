%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")}
%define _prefix /opt/baltrad/%{name}

Name: baltrad-wrwp
Version: 0.0.13
Release: 1%{?dist}
Summary: Baltrad weather radar wind products
License: GPL-3 and LGPL-3
URL: http://www.baltrad.eu/
Source0: %{name}-%{version}.tar.gz
Source1: baltrad-wrwp.conf
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

%description
Baltrad weather radar wind products

%package devel

Summary: Baltrad weather radar wind products development headers and libraries.
Group: Development/Libraries
Requires: %{name} = %{version}-%{release}
%description devel

%package python
Summary: Baltrad weather radar wind products Python module
Requires: %{name} = %{version}-%{release}
%description python
Baltrad weather radar wind products Python module.

%prep
%setup -q

%build
objdump -TC /usr/lib64/atlas/libcblas.so.3
ls -l /etc/ld.so.conf.d/atlas*
cat /etc/ld.so.conf.d/atlas*
%configure --with-rave=/opt/baltrad/rave --with-lapack=/usr/lib64 --with-cblas=/usr/lib64/atlas-sse3 --with-blas=/usr/lib64
make
%install

# FIXME: Why is this mkdir necessary?
# With full _prefix the custom installscripts think there was already an old version
# present and does some special things we may not want (migration to newer version)
rm -rf $RPM_BUILD_ROOT
mkdir -p %{buildroot}/opt/baltrad
make install DESTDIR=%{buildroot}
install -p -D -m 0644 %{SOURCE1} %{buildroot}%{_sysconfdir}/ld.so.conf.d/baltrad-wrwp.conf

%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%files
%{_prefix}/lib/libwrwp.so
%{_prefix}/bin/wrwp

%files devel
%{_prefix}/include/wrwp.h

%files python

%config(noreplace) %{_sysconfdir}/ld.so.conf.d/baltrad-wrwp.conf