#
# spec file for package python-sqlparse
#
# Copyright (c) 2019 root.
#
%{!?__python36: %global __python36 /usr/bin/python36}
%{!?python36_sitelib: %global python36_sitelib %(%{__python36} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}

Name:           python36-sqlparse-blt
Version:        0.2.4
Release:        0
Url:            https://github.com/andialbrecht/sqlparse
Summary:        Non-validating SQL parser
License:        BSD License (BSD)
Group:          Development/Languages/Python
Source:         https://files.pythonhosted.org/packages/source/S/sqlparse/sqlparse-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-build
BuildRequires:  python36-devel
Requires: python36

%description
sqlparse is a non-validating SQL parser module. It provides support for parsing, splitting and formatting SQL statements.

Visit the project page for additional information and documentation.

%prep
%setup -q -n sqlparse-%{version}

%build
%{__python36} setup.py build

%install
%{__python36} setup.py install --prefix=%{_prefix} --root=%{buildroot}
mv %{buildroot}/%{_prefix}/bin/sqlformat %{buildroot}/%{_prefix}/bin/sqlformat36

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
/usr/lib/python3.6/site-packages/*
/usr/bin/sqlformat36

%changelog
