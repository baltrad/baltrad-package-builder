%{!?__python3: %global __python3 /usr/bin/python3.9}
%{!?python3_sitelib: %global python3_sitelib %(%{__python3} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}
%define _prefix /usr/lib/baltrad-ppc

Name: baltrad-ppc
Version: %{version}
Release: %{snapshot}%{?dist}
Summary: Baltrad version of the polar processing chain
License: LGPL-3
URL: http://www.baltrad.eu/
Source0: %{name}-%{version}.tar.gz
# Dependencies to python follows from rave-devel and rave
BuildRequires: rave-devel
Requires: rave


# Turn off strip of binaries
%define debug_package %{nil}
%global __os_install_post %{nil}
%global __spec_install_post %{nil}
%global __os_install_post_scriptlets %{nil}
%global __spec_install_post_scriptlets %{nil}

%description
baltrad-ppc defines a polar processing chain originally developed by ...

%package devel
Summary: baltrad-ppc development files
Group: Development/Libraries
Requires: %{name} = %{version}-%{release}

%description devel
RAVE development headers and libraries.

%prep
%setup -q

%build
%configure --with-rave=/usr/lib/rave
make

%install
make install DESTDIR=%{buildroot}
%py_byte_compile %{__python3} %{buildroot}/usr/lib/baltrad-ppc/share/baltrad-ppc/pyppc/ || :
mkdir -p %{buildroot}/etc/ld.so.conf.d/
mkdir -p %{buildroot}%{python3_sitelib}
mkdir -p %{buildroot}/etc/baltrad/baltrad-ppc/config
mv %{buildroot}/%{_prefix}/share/baltrad-ppc/config/*.xml %{buildroot}/etc/baltrad/baltrad-ppc/config/
echo "/usr/lib/baltrad-ppc/lib" >> %{buildroot}/etc/ld.so.conf.d/baltrad-ppc.conf
mv %{buildroot}/usr/lib64/python3.9/site-packages/baltrad-ppc.pth %{buildroot}%{python3_sitelib}
ln -s ../../../../../../etc/baltrad/baltrad-ppc/config/ppc_options.xml 		%{buildroot}/%{_prefix}/share/baltrad-ppc/config/ppc_options.xml

%post
BALTRAD_USER=baltrad
BALTRAD_GROUP=baltrad

if [[ -f /etc/baltrad/baltrad.rc ]]; then
  . /etc/baltrad/baltrad.rc
fi

/sbin/ldconfig

TMPNAME=`mktemp /tmp/XXXXXXXXXX.py`
  
cat <<EOF > $TMPNAME
from rave_pgf_quality_registry_mgr import rave_pgf_quality_registry_mgr
a = rave_pgf_quality_registry_mgr("/etc/baltrad/rave/etc/rave_pgf_quality_registry.xml")
a.remove_plugin("ppc")
a.add_plugin("ppc", "ppc_quality_plugin", "ppc_quality_plugin")
a.save("/etc/baltrad/rave/etc/rave_pgf_quality_registry.xml")
EOF
%{__python3} $TMPNAME
\rm -f $TMPNAME

chown root:$BALTRAD_GROUP /etc/baltrad/baltrad-ppc
chown root:$BALTRAD_GROUP /etc/baltrad/baltrad-ppc/config
chown $BALTRAD_USER:$BALTRAD_GROUP /etc/baltrad/baltrad-ppc/config/ppc_options.xml

%postun -p /sbin/ldconfig

%files
#%{_prefix}/bin/ropo
%{_prefix}/lib/libbaltrad-ppc.so
%{_prefix}/share/baltrad-ppc/config/ppc_options.xml
%{_prefix}/share/baltrad-ppc/pyppc/*.py
%{_prefix}/share/baltrad-ppc/pyppc/__pycache__/*.pyc
%{python3_sitelib}/baltrad-ppc.pth
%{_prefix}/share/baltrad-ppc/pyppc/_pdpprocessor.so
%{_prefix}/share/baltrad-ppc/pyppc/_ppcoptions.so
%{_prefix}/share/baltrad-ppc/pyppc/_ppcradaroptions.so
/etc/ld.so.conf.d/baltrad-ppc.conf
%config /etc/baltrad/baltrad-ppc/config/ppc_options.xml

%files devel
%{_prefix}/include/*.h
