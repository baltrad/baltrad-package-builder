#
# spec file for package python-pycrypto
#
# Copyright (c) 2019 root.
#
%{!?__python36: %global __python36 /usr/bin/python36}
%{!?python36_sitelib: %global python36_sitelib %(%{__python36} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}

Name:           python36-pycrypto-blt
Version:        2.4
Release:        0
Url:            http://www.pycrypto.org/
Summary:        Cryptographic modules for Python.
License:        UNKNOWN (FIXME:No SPDX)
Group:          Development/Languages/Python
Source:         https://files.pythonhosted.org/packages/source/p/pycrypto/pycrypto-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-build
BuildRequires:  python36-devel
Requires: python36

%description
UNKNOWN

%prep
%setup -q -n pycrypto-%{version}

%build
%{__python36} setup.py build

%install
%{__python36} setup.py install --prefix=%{_prefix} --root=%{buildroot}

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%{python36_sitelib}/*

%changelog
