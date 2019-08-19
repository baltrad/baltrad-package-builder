#
# spec file for package python-pbr
#
# Copyright (c) 2019 root.
#
%global debug_package %{nil}
%{!?__python36: %global __python36 /usr/bin/python3.6}
%{!?python36_sitelib: %global python36_sitelib %(%{__python36} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}

Name:           python36-pbr-blt
Version:        1.10.0
Release:        0
Url:            https://docs.openstack.org/pbr/latest/
Summary:        Python Build Reasonableness
License:        Apache-2.0
Group:          Development/Languages/Python
Source:         https://files.pythonhosted.org/packages/source/p/pbr/pbr-%{version}.tar.gz
Patch1:		pbr-python36.patch
BuildRoot:      %{_tmppath}/%{name}-%{version}-build
BuildRequires:  python36-devel
Requires: python36

%description
Introduction
============

.. image:: https://img.shields.io/pypi/v/pbr.svg
    :target: https://pypi.python.org/pypi/pbr/
    :alt: Latest Version

.. image:: https://img.shields.io/pypi/dm/pbr.svg
    :target: https://pypi.python.org/pypi/pbr/
    :alt: Downloads

PBR is a library that injects some useful and sensible default behaviors
into your setuptools run. It started off life as the chunks of code that
were copied between all of the `OpenStack`_ projects. Around the time that
OpenStack hit 18 different projects each with at least 3 active branches,
it seemed like a good time to make that code into a proper reusable library.

PBR is only mildly configurable. The basic idea is that there's a decent
way to run things and if you do, you should reap the rewards, because then
it's simple and repeatable. If you want to do things differently, cool! But
you've already got the power of Python at your fingertips, so you don't
really need PBR.

PBR builds on top of the work that `d2to1`_ started to provide for declarative
configuration. `d2to1`_ is itself an implementation of the ideas behind
`distutils2`_. Although `distutils2`_ is now abandoned in favor of work towards
`PEP 426`_ and Metadata 2.0, declarative config is still a great idea and
specifically important in trying to distribute setup code as a library
when that library itself will alter how the setup is processed. As Metadata
2.0 and other modern Python packaging PEPs come out, PBR aims to support
them as quickly as possible.

* License: Apache License, Version 2.0
* Documentation: https://docs.openstack.org/pbr/latest/
* Source: https://git.openstack.org/cgit/openstack-dev/pbr
* Bugs: https://bugs.launchpad.net/pbr
* Change Log: https://docs.openstack.org/pbr/latest/user/history.html

.. _d2to1: https://pypi.python.org/pypi/d2to1
.. _distutils2: https://pypi.python.org/pypi/Distutils2
.. _PEP 426: http://legacy.python.org/dev/peps/pep-0426/
.. _OpenStack: https://www.openstack.org/





%prep
%setup -q -n pbr-%{version}
%patch1 -p1 


%build
%{__python36} setup.py build

%install
%{__python36} setup.py install --prefix=%{_prefix} --root=%{buildroot}
mv %{buildroot}/%{_prefix}/bin/pbr %{buildroot}/%{_prefix}/bin/pbr36

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
/usr/lib/python3.6/site-packages/*
/usr/bin/pbr36

%changelog
