#
# spec file for package python-Tempita
#
# Copyright (c) 2019 root.
#
%global debug_package %{nil}
%{!?__python36: %global __python36 /usr/bin/python3.6}
%{!?python36_sitelib: %global python36_sitelib %(%{__python36} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}

Name:           python36-decorator-blt
Version:        4.3.2
Release:        0
Url:            https://github.com/micheles/decorator
Summary:        A very small text templating language
License:        BSD License (new BSD License)
Group:          Development/Languages/Python
Source:         https://files.pythonhosted.org/packages/source/d/decorator/decorator-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-build
BuildRequires:  python36-devel
Requires: python36

%description
The goal of the decorator module is to make it easy to define
signature-preserving function decorators.

%prep
%setup -q -n decorator-%{version}

%build
%{__python36} setup.py build

%install
%{__python36} setup.py install --prefix=%{_prefix} --root=%{buildroot}

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
/usr/lib/python3.6/site-packages/*

%changelog
