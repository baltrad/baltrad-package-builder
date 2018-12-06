%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%define _prefix /usr/lib/baltrad-viewer
Name:		baltrad-viewer
Version: %{version}
Release: %{snapshot}%{?dist}
Summary:	Baltrad Viewer plugin
Group:		Development/Libraries
License:	LGPL
URL:		http://www.baltrad.eu/
Source0: %{name}-%{version}.tar.gz
Patch0:		001-setup.patch
Patch1:		002-add-products.patch
BuildArch:	noarch
BuildRequires:	python2-devel
BuildRequires:  python-distribute
BuildRequires:	hlhdf-python
Requires: python2
Requires: hlhdf-python
Requires: hlhdf
Requires: rave
Requires: php
Requires: php-common
Requires: python-pillow

%description

%clean
rm -rf %{buildroot}

%prep
%setup -q
%patch0 -p1
%patch1 -p1

%build

%install
mkdir -p %{buildroot}%{_prefix}
mkdir -p %{buildroot}%{_prefix}/Lib
mkdir -p %{buildroot}%{python_sitelib}
mkdir -p %{buildroot}/var/lib/baltrad/baltrad-viewer/data
mkdir -p %{buildroot}/etc/baltrad/baltrad-viewer
%{__python} setup.py install --prefix=/usr/lib --root=%{buildroot}
mv %{buildroot}/usr/lib/lib/python2.7/site-packages/*.py* %{buildroot}/usr/lib/baltrad-viewer/Lib/
mv %{buildroot}/usr/lib/lib/python2.7/site-packages/*.egg-info %{buildroot}/usr/lib/baltrad-viewer/Lib/
mv web/products.js %{buildroot}/etc/baltrad/baltrad-viewer
cp web/smhi-areas.xml %{buildroot}/etc/baltrad/baltrad-viewer/product-areas.xml
ln -s ../../../../etc/baltrad/baltrad-viewer/products.js %{buildroot}/usr/lib/baltrad-viewer/web/products.js
ln -s ../../../../var/lib/baltrad/baltrad-viewer/data %{buildroot}/usr/lib/baltrad-viewer/web/data
echo "/usr/lib/baltrad-viewer/Lib" > %{buildroot}/usr/lib/python2.7/site-packages/baltrad-viewer.pth

%post
/sbin/ldconfig
TMPNAME=`mktemp /tmp/XXXXXXXXXX.py`
  
cat <<EOF > $TMPNAME
from rave_pgf_registry import PGF_Registry
a=PGF_Registry(filename="/etc/baltrad/rave/etc/rave_pgf_registry.xml")
a.deregister('se.smhi.rave.creategmapimage')
a.deregister('eu.baltrad.beast.creategmap')
a.register('se.smhi.rave.creategmapimage', 'googlemap_pgf_plugin', 'generate', 'Google Map Plugin', 'outfile')
a.register('eu.baltrad.beast.creategmap', 'googlemap_pgf_plugin', 'generate', 'Google Map Plugin', 'outfile')
EOF
python $TMPNAME
\rm -f $TMPNAME

%postun -p /sbin/ldconfig

%files
%{_prefix}
/usr/lib/python2.7/site-packages/baltrad-viewer.pth
#/usr/lib/baltrad-viewer/web/*
#/usr/lib/baltrad-viewer/Lib/*
%attr(-,baltrad,baltrad) /var/lib/baltrad/baltrad-viewer
%attr(-,root,baltrad) /etc/baltrad/baltrad-viewer

%changelog

