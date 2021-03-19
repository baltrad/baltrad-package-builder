%global debug_package %{nil}
%define _prefix /
%{?systemd_requires}

Name: baltrad-base
Version: %{version}
Release: %{snapshot}%{?dist}
Summary: The Baltrad base
License: LGPL
URL: http://www.baltrad.eu/
Source0: %{name}-%{version}.tar.gz

%description
The base package used by all baltrad nodes.

%prep
%setup -q -n baltrad-base

%build
# NOP

%install
mkdir -p $RPM_BUILD_ROOT/etc/baltrad
cp baltrad.rc $RPM_BUILD_ROOT/etc/baltrad/

%files
%config /etc/baltrad/baltrad.rc

