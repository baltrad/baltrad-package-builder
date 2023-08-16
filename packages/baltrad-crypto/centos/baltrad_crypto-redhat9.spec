%global debug_package %{nil}
%{!?__python3: %global __python3 /usr/bin/python3.9}
%{!?python3_sitelib: %global python3_sitelib %(%{__python3} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}
%define _prefix /usr

Name: baltrad-crypto
Version: %{version}
Release: %{snapshot}%{?dist}
Summary: Baltrad Crypto
License: GPL-3 and LGPL-3
URL: http://www.baltrad.eu/
Source0: %{name}-%{version}.tar.gz
BuildRequires: python3-devel
Requires: python3
Requires: python3-pycryptodomex

%description
Provides key generation features for the baltrad system

%prep
%setup -q

%build
%{__python3} setup.py build

%install
%{__python3} setup.py install --skip-build --root $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/usr/share/doc/baltrad-crypto

%post

%files
/usr/lib/python3.9/site-packages/baltradcrypto/crypto
/usr/lib/python3.9/site-packages/baltradcrypto.*.pth
/usr/lib/python3.9/site-packages/baltradcrypto.*dev0-*.egg-info/*
