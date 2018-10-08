%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%define _prefix /usr

Name: baltrad-config
Version: %{version}
Release: %{snapshot}%{?dist}
Summary: Baltrad Config
License: GPL-3 and LGPL-3
URL: http://www.baltrad.eu/
Source0: %{name}-%{version}.tar.gz
BuildRequires: python2-devel
BuildRequires: python-distribute
Requires: python

%description
Provides configuration features for the baltrad system

%prep
%setup -q

%build
%{__python} setup.py build

%install
%{__python} setup.py install --skip-build --root $RPM_BUILD_ROOT

%files
/usr/bin/baltrad-config
%{python_sitelib}/baltrad/config
%{python_sitelib}/baltrad.*.pth
%{python_sitelib}/baltrad.*dev-*.egg-info/*
