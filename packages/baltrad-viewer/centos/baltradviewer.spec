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
Requires: python36
Requires: rave
Requires: php
Requires: php-common
Requires: python36-pip
Requires: python36-setuptools
Requires: python36-pillow-blt
Conflicts: baltrad-viewer-py27

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

%post
BALTRAD_USER="baltrad"
BALTRAD_GROUP="baltrad"

#[ # Reading value of  SMHI_MODE. Handles enviroments: utv, test and prod where prod is default This is just for testing & development purposes
#-f /etc/profile.d/smhi.sh ] && . /etc/profile.d/smhi.sh

# This code is uniquely defined for internal use at SMHI so that we can automatically test
# and/or deploy the software. However, the default behaviour should always be that baltrad
# uses a system user.
# SMHI_MODE contains utv,test,prod.
if [[ -f /etc/profile.d/smhi.sh ]]; then
  BALTRAD_GROUP=baltradg
  . /etc/profile.d/smhi.sh
  if [[ "$SMHI_MODE" = "utv" ]];then
    BALTRAD_USER="baltra.u"
    BALTRAD_GROUP="baltragu"
  elif [[ "$SMHI_MODE" = "test" ]];then
    BALTRAD_USER="baltra.t"
    BALTRAD_GROUP="baltragt"
  fi
else
  if ! getent group $BALTRAD_GROUP > /dev/null; then
    groupadd --system $BALTRAD_GROUP
  fi

  if ! getent passwd "$BALTRAD_USER" > /dev/null; then
    adduser --system --home /var/lib/baltrad --no-create-home --shell /bin/bash -g $BALTRAD_GROUP $BALTRAD_USER
  fi
fi

chown -R $BALTRAD_USER:$BALTRAD_GROUP /var/lib/baltrad/baltrad-viewer
chown -R root:$BALTRAD_GROUP /etc/baltrad/baltrad-viewer
chmod 775 /etc/baltrad/baltrad-viewer

TMPNAME=`mktemp /tmp/XXXXXXXXXX.py`
  
cat <<EOF > $TMPNAME
from rave_pgf_registry import PGF_Registry
a=PGF_Registry(filename="/etc/baltrad/rave/etc/rave_pgf_registry.xml")
a.deregister('se.smhi.rave.creategmapimage')
a.deregister('eu.baltrad.beast.creategmap')
a.register('se.smhi.rave.creategmapimage', 'googlemap_pgf_plugin', 'generate', 'Google Map Plugin', 'outfile')
a.register('eu.baltrad.beast.creategmap', 'googlemap_pgf_plugin', 'generate', 'Google Map Plugin', 'outfile')
EOF
%{__python36} $TMPNAME
\rm -f $TMPNAME

pip3.6 install -q "pillow==5.4.1" || true  # To get PIL (pillow) installed

%postun -p /sbin/ldconfig

%files
%{_prefix}
%{python36_sitelib}/baltrad-viewer.pth
/var/lib/baltrad/baltrad-viewer
/etc/baltrad/baltrad-viewer

%changelog

