#
# spec file for package python-Pillow
#
# Copyright (c) 2019 root.
#
%{!?__python36: %global __python36 /usr/bin/python3.6}
%{!?python36_sitelib: %global python36_sitelib %(%{__python36} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}

Name:           python36-pillow-blt
Version:        5.4.1
Release:        1
Url:            http://python-pillow.org
Summary:        Python Imaging Library (Fork)
License:        Standard PIL License (FIXME:No SPDX)
Group:          Development/Languages/Python
Source:         https://files.pythonhosted.org/packages/source/p/pillow/pillow-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-build
BuildRequires:  python36-devel
BuildRequires:  freetype-devel
BuildRequires:  libjpeg-turbo-devel
BuildRequires:  libpng-devel
Requires: python36
Requires:  freetype
Requires:  libjpeg-turbo
Requires:  libpng

%description
Pillow
======

Python Imaging Library (Fork)
-----------------------------

Pillow is the friendly PIL fork by `Alex Clark and Contributors <https://github.com/python-pillow/Pillow/graphs/contributors>`_. PIL is the Python Imaging Library by Fredrik Lundh and Contributors.

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - |linux| |macos| |windows| |coverage|
    * - package
      - |zenodo| |tidelift| |version| |downloads|
    * - social
      - |gitter| |twitter|

.. |docs| image:: https://readthedocs.org/projects/pillow/badge/?version=latest
   :target: https://pillow.readthedocs.io/?badge=latest
   :alt: Documentation Status

.. |linux| image:: https://img.shields.io/travis/python-pillow/Pillow/master.svg?label=Linux%20build
   :target: https://travis-ci.org/python-pillow/Pillow
   :alt: Travis CI build status (Linux)

.. |macos| image:: https://img.shields.io/travis/python-pillow/pillow-wheels/master.svg?label=macOS%20build
   :target: https://travis-ci.org/python-pillow/pillow-wheels
   :alt: Travis CI build status (macOS)

.. |windows| image:: https://img.shields.io/appveyor/ci/python-pillow/Pillow/master.svg?label=Windows%20build
   :target: https://ci.appveyor.com/project/python-pillow/Pillow
   :alt: AppVeyor CI build status (Windows)

.. |coverage| image:: https://coveralls.io/repos/python-pillow/Pillow/badge.svg?branch=master&service=github
   :target: https://coveralls.io/github/python-pillow/Pillow?branch=master
   :alt: Code coverage

.. |zenodo| image:: https://zenodo.org/badge/17549/python-pillow/Pillow.svg
   :target: https://zenodo.org/badge/latestdoi/17549/python-pillow/Pillow

.. |tidelift| image:: https://tidelift.com/badges/github/python-pillow/Pillow?style=flat
   :target: https://tidelift.com/subscription/pkg/pypi-pillow?utm_source=pypi-pillow&utm_medium=referral&utm_campaign=readme

.. |version| image:: https://img.shields.io/pypi/v/pillow.svg
   :target: https://pypi.org/project/Pillow/
   :alt: Latest PyPI version

.. |downloads| image:: https://img.shields.io/pypi/dm/pillow.svg
   :target: https://pypi.org/project/Pillow/
   :alt: Number of PyPI downloads

.. |gitter| image:: https://badges.gitter.im/python-pillow/Pillow.svg
   :target: https://gitter.im/python-pillow/Pillow?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge
   :alt: Join the chat at https://gitter.im/python-pillow/Pillow

.. |twitter| image:: https://img.shields.io/badge/tweet-on%20Twitter-00aced.svg
   :target: https://twitter.com/PythonPillow
   :alt: Follow on https://twitter.com/PythonPillow

.. end-badges



More Information
----------------

- `Documentation <https://pillow.readthedocs.io/>`_

  - `Installation <https://pillow.readthedocs.io/en/latest/installation.html>`_
  - `Handbook <https://pillow.readthedocs.io/en/latest/handbook/index.html>`_

- `Contribute <https://github.com/python-pillow/Pillow/blob/master/.github/CONTRIBUTING.md>`_

  - `Issues <https://github.com/python-pillow/Pillow/issues>`_
  - `Pull requests <https://github.com/python-pillow/Pillow/pulls>`_

- `Changelog <https://github.com/python-pillow/Pillow/blob/master/CHANGES.rst>`_

  - `Pre-fork <https://github.com/python-pillow/Pillow/blob/master/CHANGES.rst#pre-fork>`_

%prep
%setup -q -n Pillow-%{version}

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
