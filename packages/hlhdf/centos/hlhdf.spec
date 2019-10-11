%{!?__python36: %global __python36 /usr/bin/python3.6}
%{!?python36_sitearch: %global python36_sitearch %(%{__python36} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}
%define _prefix /usr/lib/%{name}

Name: hlhdf
Version: 0.8.9
Release: %{snapshot}%{?dist}
Summary: HL-HDF
License: GPL-3 and LGPL-3
URL: http://www.baltrad.eu/
Source0: %{name}-%{version}.tar.gz
Source1: hlhdf-python.conf
BuildRequires: hdf5-devel
Requires: hdf5
BuildRequires: zlib-devel
BuildRequires: python36-devel
BuildRequires: python36-numpy
BuildRequires: atlas
Conflicts: hlhdf-py27 

%description
A High Level Interface to the HDF5 File Format

%package devel
Summary: HL-HDF development files
Group: Development/Libraries
Requires: %{name} = %{version}
Requires: hdf5-devel
Conflicts: hlhdf-py27-devel

%description devel
HL-HDF development headers and libraries.

%package python
Summary: HL-HDF Python bindings
Requires: %{name} = %{version}
Requires: python36
Conflicts: hlhdf-py27-python

%description python
HL-HDF Python bindings

%prep
%setup -q
#%patch1 -p1


%build
make distclean || true
%configure --prefix=/usr/lib/hlhdf  --enable-py3support --with-py3bin=python3
make

%install
# FIXME: Why is this mkdir necessary?
# With full _prefix the custom installscripts think there was already an old version
# present and does some special things we may not want (migration to newer version)
mkdir -p %{buildroot}/usr/lib/hlhdf

make install DESTDIR=%{buildroot}
# Fix proper bin-path
 sed -i "s/HL_INSTALL=.*/HL_INSTALL= \/usr\/lib\/hlhdf\/bin\/hlinstall.sh/g" %{buildroot}/usr/lib/hlhdf/mkf/hldef.mk
mkdir -p %{buildroot}%{python36_sitearch}
mv %{buildroot}%{_prefix}/lib/_pyhl.so %{buildroot}%{python36_sitearch}/
install -p -D -m 0644 %{SOURCE1} %{buildroot}%{_sysconfdir}/ld.so.conf.d/hlhdf-python.conf
mkdir -p %{buildroot}/usr/lib
ln -sf ../../usr/lib/hlhdf/lib/libhlhdf.so %{buildroot}/usr/lib/libhlhdf.so

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%files
%{_prefix}/bin/hldec
%{_prefix}/bin/hlenc
%{_prefix}/bin/hlinstall.sh
%{_prefix}/bin/hllist
%{_prefix}/lib/libhlhdf.so
%{_prefix}/mkf/hldef.mk
%{_prefix}/hlhdf.pth
%{_prefix}/bin
%{_prefix}/lib
%{_prefix}/mkf
/usr/lib/libhlhdf.so

%files python
%{python36_sitearch}/_pyhl.so
%config(noreplace) %{_sysconfdir}/ld.so.conf.d/hlhdf-python.conf

%files devel
%{_prefix}/include/hlhdf.h
%{_prefix}/include/hlhdf_alloc.h
%{_prefix}/include/hlhdf_arrayobject_wrap.h
%{_prefix}/include/hlhdf_compound.h
%{_prefix}/include/hlhdf_compound_utils.h
%{_prefix}/include/hlhdf_debug.h
%{_prefix}/include/hlhdf_node.h
%{_prefix}/include/hlhdf_nodelist.h
%{_prefix}/include/hlhdf_read.h
%{_prefix}/include/hlhdf_types.h
%{_prefix}/include/hlhdf_write.h
%{_prefix}/include/pyhlhdf_common.h
%{_prefix}/include/pyhlcompat.h
%{_prefix}/include
%{_prefix}/lib/libhlhdf.a
%{_prefix}/lib/libpyhlhdf.a

