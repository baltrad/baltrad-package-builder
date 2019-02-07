#
# spec file for package python-python3-keyczar
#
# Copyright (c) 2019 root.
#
%{!?__python36: %global __python36 /usr/bin/python36}
%{!?python36_sitelib: %global python36_sitelib %(%{__python36} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}

Name:           python36-keyczar-blt
Version:        0.71rc0
Release:        0
Url:            http://www.keyczar.org/
Summary:        Toolkit for safe and simple cryptography
License:        http://www.apache.org/licenses/LICENSE-2.0 (FIXME:No SPDX)
Group:          Development/Languages/Python
Source:         https://files.pythonhosted.org/packages/source/p/python3-keyczar/python3-keyczar-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-build
BuildRequires:  python36-devel
Requires: python36
Requires: python36-pyasn1-blt
Requires: python36-pycrypto-blt

%description
Keyczar is an open source cryptographic toolkit designed to make it easier and safer for developers to use cryptography in their applications. Keyczar supports authentication and encryption with both symmetric and asymmetric keys. Some features of Keyczar include:

A simple API
Key rotation and versioning
Safe default algorithms, modes, and key lengths
Automated generation of initialization vectors and ciphertext signatures
Java and Python implementations (C++ coming soon)
International support in Java (Python coming soon)
Keyczar was originally developed by members of the Google Security Team and is released under an Apache 2.0 license.


%prep
%setup -q -n python3-keyczar-%{version}

%build
%{__python36} setup.py build

%install
%{__python36} setup.py install --prefix=%{_prefix} --root=%{buildroot}

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
/usr/lib/python3.6/site-packages/*
/usr/bin/keyczart

%changelog

