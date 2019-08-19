#
# spec file for package python-python-daemon
#
# Copyright (c) 2019 root.
#
%global debug_package %{nil}
%{!?__python36: %global __python36 /usr/bin/python3.6}
%{!?python36_sitelib: %global python36_sitelib %(%{__python36} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}

Name:           python36-daemon-blt
Version:        2.2.3
Release:        0
Url:            https://alioth.debian.org/projects/python-daemon/
Summary:        Library to implement a well-behaved Unix daemon process.
License:        Apache-2 (FIXME:No SPDX)
Group:          Development/Languages/Python
Source:         https://files.pythonhosted.org/packages/source/p/python-daemon/python-daemon-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-build
BuildRequires:  python36-devel
Requires: python36
Requires: python36-docutils-blt
Requires: python36-lockfile-blt

%description
This library implements the well-behaved daemon specification of
:pep:`3143`, &#8220;Standard daemon process library&#8221;.

A well-behaved Unix daemon process is tricky to get right, but the
required steps are much the same for every daemon program. A
`DaemonContext` instance holds the behaviour and configured
process environment for the program; use the instance as a context
manager to enter a daemon state.

Simple example of usage::

    import daemon

    from spam import do_main_program

    with daemon.DaemonContext():
        do_main_program()

Customisation of the steps to become a daemon is available by
setting options on the `DaemonContext` instance; see the
documentation for that class for each option.

%prep
%setup -q -n python-daemon-%{version}

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
