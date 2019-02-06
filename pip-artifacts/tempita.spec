#
# spec file for package python-Tempita
#
# Copyright (c) 2019 root.
#
%{!?__python36: %global __python36 /usr/bin/python36}
%{!?python36_sitelib: %global python36_sitelib %(%{__python36} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}

Name:           python36-tempita-blt
Version:        0.5.2
Release:        0
Url:            http://pythonpaste.org/tempita/
Summary:        A very small text templating language
License:        MIT
Group:          Development/Languages/Python
Source:         https://files.pythonhosted.org/packages/source/t/tempita/tempita-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-build
BuildRequires:  python36-devel
Requires: python36

%description
Tempita is a small templating language for text substitution.

This isn't meant to be the Next Big Thing in templating; it's just a
handy little templating language for when your project outgrows
``string.Template`` or ``%`` substitution.  It's small, it embeds
Python in strings, and it doesn't do much else.

You can read about the `language
<http://pythonpaste.org/tempita/#the-language>`_, the `interface
<http://pythonpaste.org/tempita/#the-interface>`_, and there's nothing
more to learn about it.

You can install from the `svn repository
<http://svn.pythonpaste.org/Tempita/trunk#Tempita-dev>`__ with
``easy_install Tempita==dev``.

%prep
%setup -q -n Tempita-%{version}

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
