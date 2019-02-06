#
# spec file for package python-lockfile
#
# Copyright (c) 2019 root.
#
%{!?__python36: %global __python36 /usr/bin/python36}
%{!?python36_sitelib: %global python36_sitelib %(%{__python36} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}

Name:           python36-lockfile-blt
Version:        0.12.2
Release:        0
Url:            http://launchpad.net/pylockfile
Summary:        Platform-independent file locking module
License:        MIT
Group:          Development/Languages/Python
Source:         https://files.pythonhosted.org/packages/source/l/lockfile/lockfile-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-build
BuildRequires:  python36-devel
Requires: python36

%description
Note: This package is **deprecated**. It is highly preferred that instead of
using this code base that instead `fasteners`_ or `oslo.concurrency`_ is
used instead. For any questions or comments or further help needed
please email `openstack-dev`_ and prefix your email subject
with ``[oslo][pylockfile]`` (for a faster response).

.. _fasteners: https://pypi.python.org/pypi/fasteners
.. _oslo.concurrency: http://docs.openstack.org/developer/oslo.concurrency/
.. _openstack-dev: http://lists.openstack.org/cgi-bin/mailman/listinfo/openstack-dev

The lockfile package exports a LockFile class which provides a simple API for
locking files.  Unlike the Windows msvcrt.locking function, the fcntl.lockf
and flock functions, and the deprecated posixfile module, the API is
identical across both Unix (including Linux and Mac) and Windows platforms.
The lock mechanism relies on the atomic nature of the link (on Unix) and
mkdir (on Windows) system calls.  An implementation based on SQLite is also
provided, more as a demonstration of the possibilities it provides than as
production-quality code.

Note: In version 0.9 the API changed in two significant ways:

 * It changed from a module defining several classes to a package containing
   several modules, each defining a single class.

 * Where classes had been named SomethingFileLock before the last two words
   have been reversed, so that class is now SomethingLockFile.

The previous module-level definitions of LinkFileLock, MkdirFileLock and
SQLiteFileLock will be retained until the 1.0 release.

To install:

    python setup.py install

* Documentation: http://docs.openstack.org/developer/pylockfile
* Source: http://git.openstack.org/cgit/openstack/pylockfile
* Bugs: http://bugs.launchpad.net/pylockfile

%prep
%setup -q -n lockfile-%{version}

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
