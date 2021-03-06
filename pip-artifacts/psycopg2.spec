#
# spec file for package python-psycopg2
#
# Copyright (c) 2019 root.
#
%global debug_package %{nil}

%{!?__python36: %global __python36 /usr/bin/python3.6}
%{!?python36_sitelib: %global python36_sitelib %(%{__python36} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}

Name:           python36-psycopg2-blt
Version:        2.7.7
Release:        0
Url:            http://initd.org/psycopg/
Summary:        psycopg2 - Python-PostgreSQL Database Adapter
License:        LGPL with exceptions or ZPL (FIXME:No SPDX)
Group:          Development/Languages/Python
Source:         https://files.pythonhosted.org/packages/source/p/psycopg2/psycopg2-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-build
BuildRequires:  python36-devel
Requires: python36

%description
Psycopg is the most popular PostgreSQL database adapter for the Python
programming language.  Its main features are the complete implementation of
the Python DB API 2.0 specification and the thread safety (several threads can
share the same connection).  It was designed for heavily multi-threaded
applications that create and destroy lots of cursors and make a large number
of concurrent "INSERT"s or "UPDATE"s.

Psycopg 2 is mostly implemented in C as a libpq wrapper, resulting in being
both efficient and secure.  It features client-side and server-side cursors,
asynchronous communication and notifications, "COPY TO/COPY FROM" support.
Many Python types are supported out-of-the-box and adapted to matching
PostgreSQL data types; adaptation can be extended and customized thanks to a
flexible objects adaptation system.

Psycopg 2 is both Unicode and Python 3 friendly.


Documentation
-------------

Documentation is included in the ``doc`` directory and is `available online`__.

.. __: http://initd.org/psycopg/docs/

For any other resource (source code repository, bug tracker, mailing list)
please check the `project homepage`__.


Installation
------------

Building Psycopg requires a few prerequisites (a C compiler, some development
packages): please check the install_ and the faq_ documents in the ``doc`` dir
or online for the details.

If prerequisites are met, you can install psycopg like any other Python
package, using ``pip`` to download it from PyPI_::

    $ pip install psycopg2

or using ``setup.py`` if you have downloaded the source package locally::

    $ python setup.py build
    $ sudo python setup.py install

You can also obtain a stand-alone package, not requiring a compiler or
external libraries, by installing the `psycopg2-binary`_ package from PyPI::

    $ pip install psycopg2-binary

The binary package is a practical choice for development and testing but in
production it is advised to use the package built from sources.

.. _PyPI: https://pypi.org/project/psycopg2/
.. _psycopg2-binary: https://pypi.org/project/psycopg2-binary/
.. _install: http://initd.org/psycopg/docs/install.html#install-from-source
.. _faq: http://initd.org/psycopg/docs/faq.html#faq-compile

.. __: http://initd.org/psycopg/


:Linux/OSX: |travis|
:Windows: |appveyor|

.. |travis| image:: https://travis-ci.org/psycopg/psycopg2.svg?branch=master
    :target: https://travis-ci.org/psycopg/psycopg2
    :alt: Linux and OSX build status

.. |appveyor| image:: https://ci.appveyor.com/api/projects/status/github/psycopg/psycopg2?branch=master&svg=true
    :target: https://ci.appveyor.com/project/psycopg/psycopg2/branch/master
    :alt: Windows build status




%prep
%setup -q -n psycopg2-%{version}

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
