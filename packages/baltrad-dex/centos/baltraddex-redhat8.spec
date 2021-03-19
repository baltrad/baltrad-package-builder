%define _prefix /usr/share/baltrad/baltrad-dex
%define java_home /usr/lib/jvm/java-1.8.0-openjdk
%global debug_package %{nil}

Name: baltrad-dex
Version: %{version}
Release: %{snapshot}%{?dist}
Summary: Baltrad DEX
License: GPL-3 and LGPL-3
URL: http://www.baltrad.eu/
Source0: %{name}-%{version}.tar.gz
Source1: hdfobject.jar
Patch1: 001-dex-fc-properties.patch
Patch2: 002-hdf-java.patch
Patch3: 003-dex-hdfobject.patch
BuildRequires: java-1.8.0-openjdk-devel
BuildRequires: ant
BuildRequires: doxygen
BuildRequires: java-hdf5
BuildRequires: baltrad-db-java
BuildRequires: baltrad-db-external
BuildRequires: baltrad-beast
BuildRequires: baltrad-beast-external
%description
Baltrad Data Exchange System (BaltradDex) constitutes an integral part of baltrad-node software package.

%package tomcat
Summary: The dex node prepared to be used in the baltrad-node-tomcat
Requires: baltrad-node-tomcat, java-hdf5
Requires: baltrad-dex

%description tomcat
The dex node that should be used within the baltrad-node-tomcat.

%prep
%setup -q
%patch1 -p1
%patch2 -p1
%patch3 -p1

%build
rm -f lib/jhdf/*.jar
cp %{SOURCE1} lib/jhdf/
JAVA_HOME=%{java_home} ant -Dbeast.path=/usr/share/baltrad/baltrad-beast -Dbaltrad.db.path="/usr/share/baltrad" -Dbaltrad.db.java.path="/usr/share/baltrad/baltrad-db/java" -Djavahdf.path=/usr/lib/java

%install
mkdir -p $RPM_BUILD_ROOT/var/lib/baltrad/baltrad-node-tomcat/webapps/BaltradDex
mkdir -p $RPM_BUILD_ROOT/etc/baltrad/
JAVA_HOME=%{java_home} ant install -Dapp.dist.dir.name=baltrad-dex -Dbeast.path=/usr/share/baltrad/baltrad-beast -Dbaltrad.db.path="/usr/share/baltrad" -Dbaltrad.db.java.path="/usr/share/baltrad/baltrad-db/java" -Djavahdf.path=/usr/lib/java -Dinstall.prefix=$RPM_BUILD_ROOT/usr/share/baltrad
cd $RPM_BUILD_ROOT/var/lib/baltrad/baltrad-node-tomcat/webapps/BaltradDex && jar -xvf $RPM_BUILD_ROOT/usr/share/baltrad/baltrad-dex/bin/BaltradDex.war
echo '<?xml version="1.0" encoding="UTF-8"?>' > $RPM_BUILD_ROOT/var/lib/baltrad/baltrad-node-tomcat/webapps/BaltradDex/META-INF/context.xml
echo '<Context path="/BaltradDex"><Resources allowLinking="true"/></Context>' >> $RPM_BUILD_ROOT/var/lib/baltrad/baltrad-node-tomcat/webapps/BaltradDex/META-INF/context.xml
mv $RPM_BUILD_ROOT/var/lib/baltrad/baltrad-node-tomcat/webapps/BaltradDex/dex.properties $RPM_BUILD_ROOT/etc/baltrad/
mv $RPM_BUILD_ROOT/var/lib/baltrad/baltrad-node-tomcat/webapps/BaltradDex/dex.log4j.properties $RPM_BUILD_ROOT/etc/baltrad/
mv $RPM_BUILD_ROOT/var/lib/baltrad/baltrad-node-tomcat/webapps/BaltradDex/db.properties $RPM_BUILD_ROOT/etc/baltrad/
mv $RPM_BUILD_ROOT/var/lib/baltrad/baltrad-node-tomcat/webapps/BaltradDex/WEB-INF/classes/resources/dex.fc.properties $RPM_BUILD_ROOT/etc/baltrad/
mv $RPM_BUILD_ROOT/var/lib/baltrad/baltrad-node-tomcat/webapps/BaltradDex/WEB-INF/classes/resources/dex.beast.properties $RPM_BUILD_ROOT/etc/baltrad/
ln -s ../../../../../../etc/baltrad/dex.properties  $RPM_BUILD_ROOT/var/lib/baltrad/baltrad-node-tomcat/webapps/BaltradDex/dex.properties
ln -s ../../../../../../etc/baltrad/db.properties  $RPM_BUILD_ROOT/var/lib/baltrad/baltrad-node-tomcat/webapps/BaltradDex/db.properties
ln -s ../../../../../../etc/baltrad/dex.log4j.properties  $RPM_BUILD_ROOT/var/lib/baltrad/baltrad-node-tomcat/webapps/BaltradDex/dex.log4j.properties
ln -s ../../../../../../../../../etc/baltrad/dex.fc.properties  $RPM_BUILD_ROOT/var/lib/baltrad/baltrad-node-tomcat/webapps/BaltradDex/WEB-INF/classes/resources/dex.fc.properties
ln -s ../../../../../../../../../etc/baltrad/dex.beast.properties  $RPM_BUILD_ROOT/var/lib/baltrad/baltrad-node-tomcat/webapps/BaltradDex/WEB-INF/classes/resources/dex.beast.properties

%post tomcat
BALTRAD_USER=baltrad
BALTRAD_GROUP=baltrad
CREATE_BALTRAD_USER=true

if [[ -f /etc/baltrad/baltrad.rc ]]; then
  . /etc/baltrad/baltrad.rc
fi

#echo "BALTRAD_USER=$BALTRAD_USER, BALTRAD_GROUP=$BALTRAD_GROUP, CREATE_BALTRAD_USER=$CREATE_BALTRAD_USER"

if [[ "$CREATE_BALTRAD_USER" = "true" ]]; then
  if ! getent group $BALTRAD_GROUP > /dev/null; then
    groupadd --system $BALTRAD_GROUP
  fi

  if ! getent passwd "$BALTRAD_USER" > /dev/null; then
    adduser --system --home /var/lib/baltrad --no-create-home --shell /bin/bash -g $BALTRAD_GROUP $BALTRAD_USER
  fi
fi

chmod 0775 /etc/baltrad

chown root:$BALTRAD_GROUP /etc/baltrad
chown -R $BALTRAD_USER:$BALTRAD_GROUP /var/lib/baltrad/baltrad-node-tomcat/webapps/BaltradDex
chown $BALTRAD_USER:$BALTRAD_GROUP /etc/baltrad/dex.properties
chown $BALTRAD_USER:$BALTRAD_GROUP /etc/baltrad/db.properties
chown $BALTRAD_USER:$BALTRAD_GROUP /etc/baltrad/dex.log4j.properties
chown $BALTRAD_USER:$BALTRAD_GROUP /etc/baltrad/dex.fc.properties
chown $BALTRAD_USER:$BALTRAD_GROUP /etc/baltrad/dex.beast.properties
chmod 0660 /etc/baltrad/dex.properties
chmod 0660 /etc/baltrad/db.properties
chmod 0660 /etc/baltrad/dex.log4j.properties
chmod 0660 /etc/baltrad/dex.fc.properties
chmod 0660 /etc/baltrad/dex.beast.properties

%files
%{_prefix}/bin/BaltradDex.war
%{_prefix}/sql/*.sql

%files tomcat
/var/lib/baltrad/baltrad-node-tomcat/webapps/BaltradDex
%config /etc/baltrad/dex.properties
%config /etc/baltrad/db.properties
%config /etc/baltrad/dex.log4j.properties
%config /etc/baltrad/dex.fc.properties
%config /etc/baltrad/dex.beast.properties

