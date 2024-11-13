%{!?__python3: %global __python3 /usr/bin/python3.9}
%{!?python3_sitelib: %global python3_sitelib %(%{__python3} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}
%define _prefix /usr/lib/beamb

Name: beamb
Version: %{version}
Release: %{snapshot}%{?dist}
Summary: beamb
License: LGPL-3
URL: http://www.baltrad.eu/
Source0: %{name}-%{version}.tar.gz
#Dependencies 
BuildRequires: rave-devel
BuildRequires: rave
Requires: rave
Conflicts: beamb-py27

%description
Determination of, and correction for, beam blockage caused by topography

%package devel
Summary: beamb development files
Group: Development/Libraries
Requires: %{name} = %{version}-%{release}
Requires: rave-devel
Conflicts: beamb-py27-devel

%description devel
Beamb development headers and libraries.

%prep
%setup -q

%build
%configure --prefix=/usr/lib/beamb --with-rave=/usr/lib/rave --localstatedir=/var
make

%install
make install DESTDIR=%{buildroot}
mkdir -p %{buildroot}%{python3_sitelib}
mkdir -p %{buildroot}/usr/lib/beamb
mkdir -p %{buildroot}/etc/ld.so.conf.d
mkdir -p %{buildroot}/var/cache/beamb
mkdir -p %{buildroot}/etc/baltrad/beamb
mv %{buildroot}/usr/lib/beamb/share/beamb/pybeamb/beamb_defines.py %{buildroot}/etc/baltrad/beamb/beamb_defines.py
ln -s ../../../../../../etc/baltrad/beamb/beamb_defines.py %{buildroot}/usr/lib/beamb/share/beamb/pybeamb/beamb_defines.py
mv %{buildroot}/usr/lib/beamb/share/beamb/config/beamb_options.xml %{buildroot}/etc/baltrad/beamb/beamb_options.xml
ln -s ../../../../../../etc/baltrad/beamb/beamb_options.xml %{buildroot}/usr/lib/beamb/share/beamb/config/beamb_options.xml
%py_byte_compile %{__python3} %{buildroot}/usr/lib/beamb/share/beamb/pybeamb/ || :
echo "/usr/lib/beamb/lib">> %{buildroot}/etc/ld.so.conf.d/beamb.conf
mv %{buildroot}/usr/lib64/python3.9/site-packages/pybeamb.pth %{buildroot}%{python3_sitelib}

%post
BALTRAD_USER=baltrad
BALTRAD_GROUP=baltrad

if [[ -f /etc/baltrad/baltrad.rc ]]; then
  . /etc/baltrad/baltrad.rc
fi

chown -R $BALTRAD_USER:$BALTRAD_GROUP /var/cache/beamb
chown -R $BALTRAD_USER:$BALTRAD_GROUP /etc/baltrad/beamb

/sbin/ldconfig
TMPNAME=`mktemp /tmp/XXXXXXXXXX.py`
  
cat <<EOF > $TMPNAME
from rave_pgf_quality_registry_mgr import rave_pgf_quality_registry_mgr
a = rave_pgf_quality_registry_mgr("/etc/baltrad/rave/etc/rave_pgf_quality_registry.xml")
a.remove_plugin("beamb")
a.add_plugin("beamb", "beamb_quality_plugin", "beamb_quality_plugin")
a.save("/etc/baltrad/rave/etc/rave_pgf_quality_registry.xml")
EOF
%{__python3} $TMPNAME
\rm -f $TMPNAME

%postun -p /sbin/ldconfig

%files
%{_prefix}/bin/beamb
%{_prefix}/lib/libbeamb.so
%{_prefix}/share/beamb/data/gtopo30/*
# Python package?
%{_prefix}/share/beamb/pybeamb/*.so
%{_prefix}/share/beamb/pybeamb/*.py
%{_prefix}/share/beamb/pybeamb/__pycache__/*.pyc
# %{_prefix}/share/beamb/pybeamb/*.pyo
%{python3_sitelib}/pybeamb.pth
/var/cache/beamb
/etc/ld.so.conf.d/beamb.conf
%config /etc/baltrad/beamb/beamb_defines.py
%config /etc/baltrad/beamb/beamb_options.xml

%files devel
%{_prefix}/include/*.h
