%define _prefix /usr/share/baltrad/baltrad-dex

Name: baltrad-dex
Version: %{version}
Release: %{snapshot}%{?dist}
Summary: Baltrad DEX
License: GPL-3 and LGPL-3
URL: http://www.baltrad.eu/
Source0: %{name}-%{version}.tar.gz
Patch1: 001-dex-fc-properties.patch
BuildRequires: java-1.8.0-openjdk-devel
BuildRequires: ant
BuildRequires: doxygen
BuildRequires: jhdf5
BuildRequires: baltrad-db-java
BuildRequires: baltrad-db-external
BuildRequires: baltrad-beast
BuildRequires: baltrad-beast-external
%description
Baltrad Data Exchange System (BaltradDex) constitutes an integral part of baltrad-node software package.

%package tomcat
Summary: The dex node prepared to be used in the baltrad-node-tomcat
Requires: baltrad-node-tomcat, jhdf5

%description tomcat
The dex node that should be used within the baltrad-node-tomcat.

%prep
%setup -q
%patch1 -p1
#%patch2 -p1

%build
ant -Dbeast.path=/usr/share/baltrad/baltrad-beast -Dbaltrad.db.path="/usr/share/baltrad" -Dbaltrad.db.java.path="/usr/share/baltrad/baltrad-db/java" -Djavahdf.path=/usr/share/java

%install
mkdir -p $RPM_BUILD_ROOT/var/lib/baltrad/baltrad-node-tomcat/webapps/BaltradDex
mkdir -p $RPM_BUILD_ROOT/var/lib/baltrad/bdb_storage
mkdir -p $RPM_BUILD_ROOT/etc/baltrad/bltnode-keys
ant install -Dapp.dist.dir.name=baltrad-dex -Dbeast.path=/usr/share/baltrad/baltrad-beast -Dbaltrad.db.path="/usr/share/baltrad" -Dbaltrad.db.java.path="/usr/share/baltrad/baltrad-db/java" -Djavahdf.path=/usr/share/java -Dinstall.prefix=$RPM_BUILD_ROOT/usr/share/baltrad
cd $RPM_BUILD_ROOT/var/lib/baltrad/baltrad-node-tomcat/webapps/BaltradDex && jar -xvf $RPM_BUILD_ROOT/usr/share/baltrad/baltrad-dex/bin/BaltradDex.war
echo '<?xml version="1.0" encoding="UTF-8"?>' > $RPM_BUILD_ROOT/var/lib/baltrad/baltrad-node-tomcat/webapps/BaltradDex/META-INF/context.xml
echo '<Context path="/BaltradDex"><Resources allowLinking="true"/></Context>' >> $RPM_BUILD_ROOT/var/lib/baltrad/baltrad-node-tomcat/webapps/BaltradDex/META-INF/context.xml
mv $RPM_BUILD_ROOT/var/lib/baltrad/baltrad-node-tomcat/webapps/BaltradDex/dex.properties $RPM_BUILD_ROOT/etc/baltrad/
mv $RPM_BUILD_ROOT/var/lib/baltrad/baltrad-node-tomcat/webapps/BaltradDex/dex.log4j.properties $RPM_BUILD_ROOT/etc/baltrad/
mv $RPM_BUILD_ROOT/var/lib/baltrad/baltrad-node-tomcat/webapps/BaltradDex/db.properties $RPM_BUILD_ROOT/etc/baltrad/
mv $RPM_BUILD_ROOT/var/lib/baltrad/baltrad-node-tomcat/webapps/BaltradDex/WEB-INF/classes/resources/dex.fc.properties $RPM_BUILD_ROOT/etc/baltrad/
ln -s ../../../../../../etc/baltrad/dex.properties  $RPM_BUILD_ROOT/var/lib/baltrad/baltrad-node-tomcat/webapps/BaltradDex/dex.properties
ln -s ../../../../../../etc/baltrad/db.properties  $RPM_BUILD_ROOT/var/lib/baltrad/baltrad-node-tomcat/webapps/BaltradDex/db.properties
ln -s ../../../../../../etc/baltrad/dex.log4j.properties  $RPM_BUILD_ROOT/var/lib/baltrad/baltrad-node-tomcat/webapps/BaltradDex/dex.log4j.properties
ln -s ../../../../../../../../../etc/baltrad/dex.fc.properties  $RPM_BUILD_ROOT/var/lib/baltrad/baltrad-node-tomcat/webapps/BaltradDex/WEB-INF/classes/resources/dex.fc.properties

%files
%{_prefix}/bin/BaltradDex.war
%{_prefix}/sql/*.sql

%files tomcat
%attr(-,baltrad,baltrad) /var/lib/baltrad/baltrad-node-tomcat/webapps/BaltradDex
%attr(0660,root,baltrad) /etc/baltrad/dex.properties
%attr(0660,root,baltrad) /etc/baltrad/db.properties
%attr(0660,root,baltrad) /etc/baltrad/dex.log4j.properties
%attr(0660,root,baltrad) /etc/baltrad/dex.fc.properties
%attr(-,baltrad,baltrad) /var/lib/baltrad/bdb_storage

