#
# spec file for package python-
#
# Copyright (c) 2019 root.
#
%global debug_package %{nil}
%{!?__python36: %global __python36 /usr/bin/python3.6}
%{!?python36_sitelib: %global python36_sitelib %(%{__python36} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}

Name:           python36-pyinotify-blt
Version:        0.9.6
Release:        0
Url:            https://github.com/seb-m/pyinotify
Summary:        Linux filesystem events monitoring
License:        MIT License
Group:          Development/Languages/Python
Source:         pyinotify-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-build
BuildRequires:  python36-devel
Requires: python36

%description
Project description
# Pyinotify

License : MIT
Project URL : [http://github.com/seb-m/pyinotify](http://github.com/seb-m/pyinotify)
Project Wiki : [http://github.com/seb-m/pyinotify/wiki](http://github.com/seb-m/pyinotify/wiki)
API Documentation: [http://seb-m.github.com/pyinotify](http://seb-m.github.com/pyinotify)
## Dependencies

Linux ≥ 2.6.13
Python ≥ 2.4 (including Python 3.x)
## Install

### Get the current stable version from PyPI and install it with pip

# To install pip follow http://www.pip-installer.org/en/latest/installing.html $ sudo pip install pyinotify
### Or install Pyinotify directly from source

# Choose your Python interpreter: either python, python2.7, python3.2,.. # Replacing XXX accordingly, type: $ sudo pythonXXX setup.py install
## Watch a directory

Install pyinotify and run this command from a shell:

$ python -m pyinotify -v /my-dir-to-watch

%prep
%setup -q -n pyinotify-%{version}

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
