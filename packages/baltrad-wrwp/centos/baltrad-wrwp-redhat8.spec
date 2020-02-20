%{!?__python36: %global __python36 /usr/bin/python3.6}
%{!?python36_sitelib: %global python36_sitelib %(%{__python36} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}
%define _prefix /usr/lib/baltrad-wrwp

Name: baltrad-wrwp
Version: %{version}
Release: %{snapshot}%{?dist}
Summary: Baltrad weather radar wind products
License: LGPL-3
URL: http://www.baltrad.eu/
Patch1: make-for-atlas.patch
Source0: %{name}-%{version}.tar.gz
BuildRequires: rave
BuildRequires: rave-devel
BuildRequires: lapack-devel
BuildRequires: blas-devel
BuildRequires: atlas-devel
BuildRequires: gsl-devel
Requires: rave
Requires: atlas
Conflicts: baltrad-wrwp-py27

%description
Baltrad weather radar wind products

%package devel
Summary: Baltrad weather radar wind products development headers and libraries.
Group: Development/Libraries
Requires: %{name} = %{version}-%{release}
Requires: rave-devel
Conflicts: baltrad-wrwp-py27-devel

%description devel

%package python
Summary: Baltrad weather radar wind products Python module
Requires: %{name} = %{version}-%{release}
Requires: rave

%description python
Baltrad weather radar wind products Python module.

%prep
%setup -q
%patch1 -p1

%build
%configure --prefix=/usr/lib/baltrad-wrwp --with-rave=/usr/lib/rave --with-lapack=/usr/lib64 --with-lapacke=/usr/include/lapacke,/usr/lib64 --with-cblas=/usr/include,/usr/lib64/atlas --with-blas=/usr/lib64
make

%install
# FIXME: Why is this mkdir necessary?
# With full _prefix the custom installscripts think there was already an old version
# present and does some special things we may not want (migration to newer version)
rm -rf %{buildroot}
mkdir -p %{buildroot}/usr/lib/baltrad-wrwp
mkdir -p %{buildroot}%{_sysconfdir}/ld.so.conf.d
mkdir -p %{buildroot}%{python36_sitelib}
make install DESTDIR=%{buildroot}
mkdir -p %{buildroot}/etc/baltrad/wrwp
mv %{buildroot}/usr/lib/baltrad-wrwp/config/wrwp_config.xml %{buildroot}/etc/baltrad/wrwp/wrwp_config.xml
rm -fr %{buildroot}/usr/lib/baltrad-wrwp/config
%py_byte_compile %{__python36} %{buildroot}/usr/lib/baltrad-wrwp/share/wrwp/pywrwp/ || :
echo "/usr/lib/baltrad-wrwp/lib" >> %{buildroot}%{_sysconfdir}/ld.so.conf.d/baltrad-wrwp.conf

%post
/sbin/ldconfig
BALTRAD_USER="baltrad"
BALTRAD_GROUP="baltrad"

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
chown $BALTRAD_USER:$BALTRAD_GROUP /etc/baltrad/wrwp/wrwp_config.xml
chmod 0664 /etc/baltrad/wrwp/wrwp_config.xml

%post python
/sbin/ldconfig
TMPNAME=`mktemp /tmp/XXXXXXXXXX.py`
  
cat <<EOF > $TMPNAME
from rave_pgf_registry import PGF_Registry
a=PGF_Registry(filename="/etc/baltrad/rave/etc/rave_pgf_registry.xml")
a.deregister('eu.baltrad.beast.generatewrwp')
a.deregister('se.smhi.baltrad-wrwp.generatewrwp')
a.register('eu.baltrad.beast.generatewrwp', 'baltrad_wrwp_pgf_plugin', 'generate', 'Baltrad WRWP Plugin', 'fields','interval,maxheight,mindistance,maxdistance','minelevationangle,velocitythreshold')
a.register('se.smhi.baltrad-wrwp.generatewrwp', 'baltrad_wrwp_pgf_plugin', 'generate', 'Baltrad WRWP Plugin', 'fields','interval,maxheight,mindistance,maxdistance','minelevationangle,velocitythreshold')
EOF
%{__python36} $TMPNAME
\rm -f $TMPNAME

%postun -p /sbin/ldconfig

%files
%{_prefix}/lib/libwrwp.so
%{_prefix}/bin/wrwp_main
%config /etc/baltrad/wrwp/wrwp_config.xml

%files devel
%{_prefix}/include/wrwp.h

%files python
%{_prefix}/share/wrwp/pywrwp/
%{python36_sitelib}/pywrwp.pth

%config(noreplace) %{_sysconfdir}/ld.so.conf.d/baltrad-wrwp.conf
