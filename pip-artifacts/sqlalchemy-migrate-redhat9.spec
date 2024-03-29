#
# spec file for package python-sqlalchemy-migrate
#
# Copyright (c) 2019 root.
#
%global debug_package %{nil}
%{!?__python3: %global __python3 /usr/bin/python3}
%{!?python3_sitelib: %global python3_sitelib %(%{__python3} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}

Name:           python3-sqlalchemy-migrate-blt
Version:        0.10.0
Release:        1
Url:            http://www.openstack.org/
Summary:        Database schema migration for SQLAlchemy
License:        Apache-2.0
Group:          Development/Languages/Python
Source:         https://files.pythonhosted.org/packages/source/s/sqlalchemy-migrate/sqlalchemy-migrate-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-build
BuildRequires:  python3-devel
Requires: python3
Requires: python3-tempita
Requires: python3-sqlparse
Requires: python3-decorator
Requires: python3-pbr
Requires: python3-six
Patch1: sqlalchemy_migrate_patch.patch

%description
SQLAlchemy Migrate
==================

Fork from http://code.google.com/p/sqlalchemy-migrate/ to get it working with
SQLAlchemy 0.8.

Inspired by Ruby on Rails' migrations, Migrate provides a way to deal with
database schema changes in `SQLAlchemy <http://sqlalchemy.org>`_ projects.

Migrate extends SQLAlchemy to have database changeset handling. It provides a
database change repository mechanism which can be used from the command line as
well as from inside python code.

Help
----

Sphinx documentation is available at the project page `readthedocs.org
<https://sqlalchemy-migrate.readthedocs.org/>`_.

Users and developers can be found at #openstack-dev on Freenode IRC
network and at the public users mailing list `migrate-users
<http://groups.google.com/group/migrate-users>`_.

New releases and major changes are announced at the public announce mailing
list `openstack-dev
<http://lists.openstack.org/cgi-bin/mailman/listinfo/openstack-dev>`_
and at the Python package index `sqlalchemy-migrate
<http://pypi.python.org/pypi/sqlalchemy-migrate>`_.

Homepage is located at `stackforge
<http://github.com/stackforge/sqlalchemy-migrate/>`_

You can also clone a current `development version
<http://github.com/stackforge/sqlalchemy-migrate>`_

Tests and Bugs
--------------

To run automated tests:

* install tox: ``pip install -U tox``
* run tox: ``tox``
* to test only a specific Python version: ``tox -e py27`` (Python 2.7)

Please report any issues with sqlalchemy-migrate to the issue tracker at
`Launchpad issues
<https://bugs.launchpad.net/sqlalchemy-migrate>`_





%prep
%setup -q -n sqlalchemy-migrate-%{version}
%patch1 -p1

%build
%{__python3} setup.py build

%install
%{__python3} setup.py install --prefix=%{_prefix} --root=%{buildroot}

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
/usr/lib/python3.9/site-packages/*
/usr/bin/migrate
/usr/bin/migrate-repository

%changelog
