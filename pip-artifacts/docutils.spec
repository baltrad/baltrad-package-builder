#
# spec file for package python-docutils
#
# Copyright (c) 2019 root.
#
%{!?__python36: %global __python36 /usr/bin/python36}
%{!?python36_sitelib: %global python36_sitelib %(%{__python36} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}

Name:           python36-docutils-blt
Version:        0.14
Release:        0
Url:            http://docutils.sourceforge.net/
Summary:        Docutils -- Python Documentation Utilities
License:        public domain, Python, 2-Clause BSD, GPL 3 (see COPYING.txt) (FIXME:No SPDX)
Group:          Development/Languages/Python
Source:         https://files.pythonhosted.org/packages/source/d/docutils/docutils-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-build
BuildRequires:  python36-devel
Requires: python36

%description
Docutils -- Python Documentation Utilities

%prep
%setup -q -n docutils-%{version}

%build
%{__python36} setup.py build

%install
%{__python36} setup.py install --prefix=%{_prefix} --root=%{buildroot}
mkdir -p %{buildroot}/%{_prefix}/bin/tools
mv %{buildroot}/%{_prefix}/bin/rst*.py %{buildroot}/%{_prefix}/bin/tools/

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%doc README.txt
%{_bindir}/tools/rst2html.py
%{_bindir}/tools/rst2html4.py
%{_bindir}/tools/rst2html5.py
%{_bindir}/tools/rst2latex.py
%{_bindir}/tools/rst2man.py
%{_bindir}/tools/rst2odt.py
%{_bindir}/tools/rst2odt_prepstyles.py
%{_bindir}/tools/rst2pseudoxml.py
%{_bindir}/tools/rst2s5.py
%{_bindir}/tools/rst2xetex.py
%{_bindir}/tools/rst2xml.py
%{_bindir}/tools/rstpep2html.py
/usr/lib/python3.6/site-packages/*


%changelog
