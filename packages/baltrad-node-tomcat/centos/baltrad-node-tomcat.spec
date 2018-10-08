%define _prefix /opt/baltrad/%{name}

Name: baltrad-node-tomcat
Version: %{version}
Release: %{snapshot}%{?dist}
Summary: The Baltrad nodes tomcat server
License: See LICENSE information for tomcat
URL: http://www.baltrad.eu/
Source0: %{name}-%{version}.tar.gz
BuildRequires: java-1.8.0-openjdk-devel
BuildRequires: ant
BuildRequires: baltrad-db-java
# Server binary needed
Requires: openjdk-8-jre
Requires: libjhdf5-java

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
#mkdir lib/joda-time
#cp %{SOURCE1} lib/joda-time

%build
# Use %{_prefix} once known what it should be based on higher level components requirements
ant -Dbaltraddb.path=/opt/baltrad -Dbaltraddb.bin.path=/usr/bin
ls -lR

%install
# FIXME: Unstandard jar install path
ant install-files -Dapp.dist.dir.name=%{name} -Dbaltraddb.path=/opt/baltrad -Dbaltraddb.bin.path=/usr/bin -Dprefix=$RPM_BUILD_ROOT/opt/baltrad

ls -lR $RPM_BUILD_ROOT
#mkdir -p $RPM_BUILD_ROOT%{_prefix}/bin
#cp -p dist/%{name}.jar $RPM_BUILD_ROOT%{_prefix}/bin
#mkdir -p $RPM_BUILD_ROOT%{_prefix}/libs
#cp -rp lib/apache-xmlrpc/ $RPM_BUILD_ROOT%{_prefix}/libs
#cp -rp lib/groovy/ $RPM_BUILD_ROOT%{_prefix}/libs

%files
%{_prefix}/bin/beast.jar
%{_prefix}/bin/pgfwkplugin
%{_prefix}/bin/xmlrpcserver
%{_prefix}/etc/*
%{_prefix}/examples/*
%{_prefix}/sql/*

%files external
%{_prefix}/libs/*.jar
