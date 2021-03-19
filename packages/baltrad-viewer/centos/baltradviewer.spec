%{!?__python36: %global __python36 /usr/bin/python3.6}
%{!?python36_sitelib: %global python36_sitelib %(%{__python36} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}
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
BuildRequires: python36-devel
BuildRequires: python36
BuildRequires: rave-devel
Requires: baltrad-viewer-pgf
Requires: baltrad-viewer-web

%description
Group for baltrad-viewer-pgf and baltrad-viewer-web

%package pgf
Summary: PGF for creating PNGs from cartesian products
Group: Application
Requires: python36
Requires: rave
Requires: python36-pip
Requires: python36-setuptools
Requires: python36-pillow-blt

%description pgf
PGF for creating PNGs from cartesian products

%package web
Summary: Web interface for showing PNGs from generator
Group: WWW
Requires: php
Requires: php-common

%description web
Web interface for showing PNGs from generator

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
mkdir -p %{buildroot}%{python36_sitelib}
mkdir -p %{buildroot}/var/lib/baltrad/baltrad-viewer/data
mkdir -p %{buildroot}/etc/baltrad/baltrad-viewer
%{__python36} setup.py install --prefix=/usr/lib --root=%{buildroot}
mv %{buildroot}/usr/lib/lib/python3.6/site-packages/*.py* %{buildroot}/usr/lib/baltrad-viewer/Lib/
mv %{buildroot}/usr/lib/lib/python3.6/site-packages/*.egg-info %{buildroot}/usr/lib/baltrad-viewer/Lib/
rm -fr %{buildroot}/usr/lib/lib/python3.6/site-packages/__pycache__
mv web/products.js %{buildroot}/etc/baltrad/baltrad-viewer
cp web/smhi-areas.xml %{buildroot}/etc/baltrad/baltrad-viewer/product-areas.xml
ln -s ../../../../etc/baltrad/baltrad-viewer/products.js %{buildroot}/usr/lib/baltrad-viewer/web/products.js
ln -s ../../../../var/lib/baltrad/baltrad-viewer/data %{buildroot}/usr/lib/baltrad-viewer/web/data
echo "/usr/lib/baltrad-viewer/Lib" > %{buildroot}%{python36_sitelib}/baltrad-viewer.pth

%post pgf
BALTRAD_USER=baltrad
BALTRAD_GROUP=baltrad
CREATE_BALTRAD_USER=true

if [[ -f /etc/baltrad/baltrad.rc ]]; then
  . /etc/baltrad/baltrad.rc
fi

#echo "BALTRAD_USER=$BALTRAD_USER, BALTRAD_GROUP=$BALTRAD_GROUP, CREATE_BALTRAD_USER=$CREATE_BALTRAD_USER"

if [[ "$CREATE_BALTRAD_USER" = "true" ]]; then
  if ! getent group $BALTRAD_GROUP > /dev/null; then
    groupadd --system $BALTRAD_GROUP
  fi

  if ! getent passwd "$BALTRAD_USER" > /dev/null; then
    adduser --system --home /var/lib/baltrad --no-create-home --shell /bin/bash -g $BALTRAD_GROUP $BALTRAD_USER
  fi
fi

chown -R $BALTRAD_USER:$BALTRAD_GROUP /usr/lib/baltrad-viewer/Lib
chown  $BALTRAD_USER:$BALTRAD_GROUP /usr/lib/baltrad-viewer/COPYING
chown  $BALTRAD_USER:$BALTRAD_GROUP /usr/lib/baltrad-viewer/COPYING.LESSER
chown  $BALTRAD_USER:$BALTRAD_GROUP /usr/lib/baltrad-viewer/LICENSE
chown  $BALTRAD_USER:$BALTRAD_GROUP /usr/lib/baltrad-viewer/README.ravepgf

%post web
BALTRAD_USER=baltrad
BALTRAD_GROUP=baltrad
CREATE_BALTRAD_USER=true

if [[ -f /etc/baltrad/baltrad.rc ]]; then
  . /etc/baltrad/baltrad.rc
fi

#echo "BALTRAD_USER=$BALTRAD_USER, BALTRAD_GROUP=$BALTRAD_GROUP, CREATE_BALTRAD_USER=$CREATE_BALTRAD_USER"

if [[ "$CREATE_BALTRAD_USER" = "true" ]]; then
  if ! getent group $BALTRAD_GROUP > /dev/null; then
    groupadd --system $BALTRAD_GROUP
  fi

  if ! getent passwd "$BALTRAD_USER" > /dev/null; then
    adduser --system --home /var/lib/baltrad --no-create-home --shell /bin/bash -g $BALTRAD_GROUP $BALTRAD_USER
  fi
fi

chown -R $BALTRAD_USER:$BALTRAD_GROUP /var/lib/baltrad/baltrad-viewer
chown -R $BALTRAD_USER:$BALTRAD_GROUP /usr/lib/baltrad-viewer/web
chown  $BALTRAD_USER:$BALTRAD_GROUP /usr/lib/baltrad-viewer/README
chown  $BALTRAD_USER:$BALTRAD_GROUP /usr/lib/baltrad-viewer/README2
chown -R root:$BALTRAD_GROUP /etc/baltrad/baltrad-viewer
chmod 775 /etc/baltrad/baltrad-viewer

%postun -p /sbin/ldconfig

%files

%files pgf
%{_prefix}/Lib
%{_prefix}/README.ravepgf
%{_prefix}/COPYING
%{_prefix}/COPYING.LESSER
%{_prefix}/LICENSE
%{_prefix}/README.ravepgf
%{python36_sitelib}/baltrad-viewer.pth

%files web
%{_prefix}/web
%{_prefix}/README
%{_prefix}/README2
/var/lib/baltrad/baltrad-viewer
%config /etc/baltrad/baltrad-viewer

%changelog

