%global debug_package %{nil}
%{!?__python36: %global __python36 /usr/bin/python3.6}
%{!?python36_sitelib: %global python36_sitelib %(%{__python36} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}
%{!?bdb_site_install_dir: %global bdb_site_install_dir /usr/lib/python3.6/site-packages}
%define _prefix /usr

Name: baltrad-utils
Version: %{version}
Release: %{snapshot}%{?dist}
Summary: Baltrad Utilities
License: GPL-3 and LGPL-3
URL: http://www.baltrad.eu/
Source0: %{name}-%{version}.tar.gz
BuildRequires: python3-devel
Requires: python3

%description
Provides utilities for the baltrad system

%prep
%setup -q

%build
%{__python3} setup.py build

%install
%{__python3} setup.py install --skip-build --root $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/usr/share/doc/baltrad-utils

%post

%files
%{bdb_site_install_dir}/baltradutils/
%{bdb_site_install_dir}/baltradutils-*.pth
%{bdb_site_install_dir}/baltradutils-*.egg-info/*

