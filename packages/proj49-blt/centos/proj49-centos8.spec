%define _prefix /usr/lib/proj49-blt

Name: proj49-blt
Version: 4.9.3
Release: %{snapshot}%{?dist}
Summary: PROJ 4.9
License: MIT style license
Source0: %{name}-%{version}.tar.gz
Source1: proj49-blt.conf

%description
Proj 4.9 package

%prep
%setup -q -n proj49-blt

%build
make distclean || true
%configure --prefix=/usr/lib/proj49-blt
make

%install
mkdir -p %{buildroot}/usr/lib/proj49-blt

make install DESTDIR=%{buildroot}

install -p -D -m 0644 %{SOURCE1} %{buildroot}%{_sysconfdir}/ld.so.conf.d/proj49-blt.conf

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%files
%{_prefix}
%{_sysconfdir}/ld.so.conf.d/proj49-blt.conf


