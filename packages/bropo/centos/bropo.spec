%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%define _prefix /opt/baltrad/%{name}

Name: bropo
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

%description
bRopo is an adaption of the existing FMI software package ROPO.
The bRopo is adapted to integrate with the RAVE framework and also
to provide users with a Python interface.

%package devel
Summary: bRopo development files
Group: Development/Libraries
Requires: %{name} = %{version}-%{release}

%description devel
RAVE development headers and libraries.


%prep
%setup -q

%build
%configure --with-rave=/opt/baltrad/rave
make

%install
make install DESTDIR=%{buildroot}

%files
%{_prefix}/bin/ropo
%{_prefix}/lib/libbropo.so
%{_prefix}/share/bropo/config/ropo_options.xml
# FIXME: Separate pyropo into its own package?
%{_prefix}/share/bropo/pyropo/ropo_*.py
%{_prefix}/share/bropo/pyropo/ropo_*.pyc
%{_prefix}/share/bropo/pyropo/ropo_*.pyo
%{python_sitelib}/pyropo.pth
%{_prefix}/share/bropo/pyropo/_fmiimage.so
%{_prefix}/share/bropo/pyropo/_ropogenerator.so

%files devel
%{_prefix}/include/*.h
