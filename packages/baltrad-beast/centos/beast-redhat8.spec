%global debug_package %{nil}
%define _prefix /usr/share/baltrad/%{name}

Name: baltrad-beast
Version: %{version}
Release: %{snapshot}%{?dist}
Summary: The Baltrad exchange and scheduling tools
License: GPL-3 and LGPL-3
URL: http://www.baltrad.eu/
Source0: %{name}-%{version}.tar.gz
#Source1: joda-time-2.0.jar
BuildRequires: java-1.8.0-openjdk-devel
BuildRequires: ant
BuildRequires: baltrad-db-java
# Server binary needed
BuildRequires: baltrad-db

%description
The beast library provides the internal mechanisms for managing
messages and data that are transfered by the Baltrad Data Exchange engine.
In it's own, it does not do much except providing some mechanisms
for determining what to do with certain messages as well as passing
on the messages to different adaptors.

%package external
Summary: External JAVA jars other Baltrad components need
Group: Development/Libraries

%description external
External JAVA jars other Baltrad components (primarily BaltradDex) use, which
are provided in the beast package.

%prep
%setup -q
# Copy joda-time in our sources until baltrad-db installs it and we find it from there
# Why does it work either way on Fedora17? java-sdk includes it already or what..?
# Use copy from baltrad-db-external instead

%build
# Use %{_prefix} once known what it should be based on higher level components requirements
JAVA_HOME=/usr/lib/jvm/java-1.8.0-openjdk ant -Dbaltraddb.path=/usr/share/baltrad -Dbaltraddb.java.path=/usr/share/baltrad/baltrad-db/java -Dbaltraddb.bin.path=/usr/bin

%install
JAVA_HOME=/usr/lib/jvm/java-1.8.0-openjdk ant install-files -Dapp.dist.dir.name=%{name} -Dbaltraddb.path=/usr/share/baltrad -Dbaltraddb.java.path=/usr/share/baltrad/baltrad-db/java -Dbaltraddb.bin.path=/usr/bin -Dprefix=$RPM_BUILD_ROOT/usr/share/baltrad

%files
%{_prefix}/bin/beast.jar
%{_prefix}/bin/pgfwkplugin
%{_prefix}/bin/xmlrpcserver
%{_prefix}/etc/*
%{_prefix}/examples/*
%{_prefix}/sql/*

%files external
%{_prefix}/libs/*.jar
