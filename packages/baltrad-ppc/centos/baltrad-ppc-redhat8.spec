%{!?__python36: %global __python36 /usr/bin/python3.6}
%{!?python36_sitelib: %global python36_sitelib %(%{__python36} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}
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
%py_byte_compile %{__python36} %{buildroot}/usr/lib/baltrad-ppc/share/baltrad-ppc/pyppc/ || :
mkdir -p %{buildroot}/etc/ld.so.conf.d/
mkdir -p %{buildroot}%{python36_sitelib}
mkdir -p %{buildroot}/etc/baltrad/baltrad-ppc/config
mv %{buildroot}/%{_prefix}/share/baltrad-ppc/config/*.xml %{buildroot}/etc/baltrad/baltrad-ppc/config/
echo "/usr/lib/baltrad-ppc/lib" >> %{buildroot}/etc/ld.so.conf.d/baltrad-ppc.conf
#mv %{buildroot}/usr/lib64/python3.6/site-packages/pybaltradppc.pth %{buildroot}%{python36_sitelib}
ln -s ../../../../../../etc/baltrad/baltrad-ppc/config/ppc_options.xml 		%{buildroot}/%{_prefix}/share/baltrad-ppc/config/ppc_options.xml

%post
/sbin/ldconfig
TMPNAME=`mktemp /tmp/XXXXXXXXXX.py`
  
cat <<EOF > $TMPNAME
from rave_pgf_quality_registry_mgr import rave_pgf_quality_registry_mgr
a = rave_pgf_quality_registry_mgr("/etc/baltrad/rave/etc/rave_pgf_quality_registry.xml")
a.remove_plugin("ppc")
a.add_plugin("ppc", "ppc_quality_plugin", "ppc_quality_plugin")
a.save("/etc/baltrad/rave/etc/rave_pgf_quality_registry.xml")
EOF
%{__python36} $TMPNAME
\rm -f $TMPNAME

%postun -p /sbin/ldconfig

%files
#%{_prefix}/bin/ropo
%{_prefix}/lib/libbaltrad-ppc.so
%{_prefix}/share/baltrad-ppc/config/ppc_options.xml
%{_prefix}/share/baltrad-ppc/pyppc/*.py
%{_prefix}/share/baltrad-ppc/pyppc/__pycache__/*.pyc
%{python36_sitelib}/baltrad-ppc.pth
%{_prefix}/share/baltrad-ppc/pyppc/_pdpprocessor.so
%{_prefix}/share/baltrad-ppc/pyppc/_ppcoptions.so
%{_prefix}/share/baltrad-ppc/pyppc/_ppcradaroptions.so
/etc/ld.so.conf.d/baltrad-ppc.conf
/etc/baltrad/baltrad-ppc/config/ppc_options.xml

%files devel
%{_prefix}/include/*.h
