%global debug_package %{nil}
%define _prefix /usr/lib/bbufr
Name:		bbufr
Version:	%{version}
Release:	 %{snapshot}%{?dist}
Summary:	BALTRAD interface to EUMETNET OPERA's BUFR software
Group:		Development/Libraries
License:	LGPL-3
URL:		http://www.baltrad.eu/
Source0:	%{name}-%{version}.tar.gz
BuildRequires:	zlib-devel
BuildRequires:	hdf5-devel
BuildRequires:	proj-devel
BuildRequires:	libpng-devel
BuildRequires:  autoconf, automake libtool
Requires:	zlib
Requires:	proj
Requires:	libpng
Requires:	hdf5

%description
BALTRAD interface to EUMETNET OPERA's BUFR software

%prep
%setup -q -n %{name}-%{version}

%build
libtoolize
aclocal
autoconf
automake --add-missing
CFLAGS=-I/usr/include LDFLAGS=-L/usr/lib %configure --prefix=/usr/lib/bbufr --libdir=/usr/lib/bbufr/lib
make


%install
mkdir -p %{buildroot}/usr/lib
make install DESTDIR=%{buildroot}

%files
%defattr(-,root,root,-)
%{_prefix}/include/bitio.h
%{_prefix}/include/bufr.h
%{_prefix}/include/bufr_io.h
%{_prefix}/include/bufrlib.h
%{_prefix}/include/desc.h
%{_prefix}/include/rlenc.h
%{_prefix}/lib/libOperaBufr.a
%{_prefix}/share/bbufr/tables
%changelog
