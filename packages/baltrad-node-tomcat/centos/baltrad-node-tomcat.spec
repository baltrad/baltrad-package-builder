%define _prefix /

Name: baltrad-node-tomcat
Version: %{version}
Release: %{snapshot}%{?dist}
Summary: The Baltrad nodes tomcat server
License: See LICENSE information for tomcat
URL: http://www.baltrad.eu/
Patch1: 001-baltrad-node.patch
Patch2: 002-server-xml.patch
Source0: %{name}-%{version}.tar.gz
# Server binary needed
Requires: java-1.8.0-openjdk
Requires: jhdf5
Requires: jhdf
Requires: jhdfobj

%description
The baltrad node tomcat server is the adapted tomcat server that is suitable for
the baltrad web application.

%prep
%setup -q -n baltrad-node-tomcat
%patch1 -p1
%patch2 -p0

%build
# NOP

%install
mkdir -p $RPM_BUILD_ROOT/usr/share/baltrad/baltrad-node-tomcat
mkdir -p $RPM_BUILD_ROOT/var/lib/baltrad/baltrad-node-tomcat
mkdir -p $RPM_BUILD_ROOT/var/lib/baltrad/baltrad-node-tomcat/policy
mkdir -p $RPM_BUILD_ROOT/var/lib/baltrad/baltrad-node-tomcat/webapps
mkdir -p $RPM_BUILD_ROOT/var/log/baltrad/baltrad-node-tomcat
mkdir -p $RPM_BUILD_ROOT/var/cache/baltrad-node-tomcat
mkdir -p $RPM_BUILD_ROOT/var/run/baltrad
mkdir -p $RPM_BUILD_ROOT/etc/baltrad/baltrad-node-tomcat
mkdir -p $RPM_BUILD_ROOT/etc/init.d
cp baltrad-node $RPM_BUILD_ROOT/etc/init.d/
chmod a+x $RPM_BUILD_ROOT/etc/init.d/baltrad-node
cp -r bin $RPM_BUILD_ROOT/usr/share/baltrad/baltrad-node-tomcat/
cp -r lib $RPM_BUILD_ROOT/usr/share/baltrad/baltrad-node-tomcat/
cp conf/catalina.policy $RPM_BUILD_ROOT/var/lib/baltrad/baltrad-node-tomcat/policy/
cp conf/*.xml $RPM_BUILD_ROOT/etc/baltrad/baltrad-node-tomcat/
cp conf/*.xsd $RPM_BUILD_ROOT/etc/baltrad/baltrad-node-tomcat/
cp conf/*.properties $RPM_BUILD_ROOT/etc/baltrad/baltrad-node-tomcat/
cp -r webapps/host-manager $RPM_BUILD_ROOT/var/lib/baltrad/baltrad-node-tomcat/webapps/
cp -r webapps/manager $RPM_BUILD_ROOT/var/lib/baltrad/baltrad-node-tomcat/webapps/
cp -r webapps/ROOT $RPM_BUILD_ROOT/var/lib/baltrad/baltrad-node-tomcat/webapps/
cp -r webapps/docs $RPM_BUILD_ROOT/var/lib/baltrad/baltrad-node-tomcat/webapps/
ln -s  ../../../log/baltrad/baltrad-node-tomcat $RPM_BUILD_ROOT/var/lib/baltrad/baltrad-node-tomcat/logs
ln -s ../../../../etc/baltrad/baltrad-node-tomcat $RPM_BUILD_ROOT/var/lib/baltrad/baltrad-node-tomcat/conf
ln -s ../../../cache/baltrad-node-tomcat $RPM_BUILD_ROOT/var/lib/baltrad/baltrad-node-tomcat/work
ln -s /usr/share/java/jhdf5.jar $RPM_BUILD_ROOT/usr/share/baltrad/baltrad-node-tomcat/lib/jhdf5.jar
ln -s /usr/share/java/jhdf5obj.jar $RPM_BUILD_ROOT/usr/share/baltrad/baltrad-node-tomcat/lib/jhdf5obj.jar
ln -s /usr/share/java/jhdf.jar $RPM_BUILD_ROOT/usr/share/baltrad/baltrad-node-tomcat/lib/jhdf.jar
ln -s /usr/share/java/jhdfobj.jar $RPM_BUILD_ROOT/usr/share/baltrad/baltrad-node-tomcat/lib/jhdfobj.jar
cp LICENSE $RPM_BUILD_ROOT/usr/share/baltrad/baltrad-node-tomcat/
cp NOTICE $RPM_BUILD_ROOT/usr/share/baltrad/baltrad-node-tomcat/
cp README.md $RPM_BUILD_ROOT/usr/share/baltrad/baltrad-node-tomcat/

#/usr/share/java/jhdf4obj.jar /usr/share/baltrad/baltrad-node-tomcat/lib/jhdf4obj.jar
#/usr/share/java/jhdf5.jar /usr/share/baltrad/baltrad-node-tomcat/lib/jhdf5.jar
#/usr/share/java/jhdf5obj.jar /usr/share/baltrad/baltrad-node-tomcat/lib/jhdf5obj.jar
#/usr/share/java/jhdf.jar /usr/share/baltrad/baltrad-node-tomcat/lib/jhdf.jar
#/usr/share/java/jhdfobj.jar /usr/share/baltrad/baltrad-node-tomcat/lib/jhdfobj.jar


# FIXME: Unstandard jar install path
#mkdir -p $RPM_BUILD_ROOT%{_prefix}/bin
#cp -p dist/%{name}.jar $RPM_BUILD_ROOT%{_prefix}/bin
#mkdir -p $RPM_BUILD_ROOT%{_prefix}/libs
#cp -rp lib/apache-xmlrpc/ $RPM_BUILD_ROOT%{_prefix}/libs
#cp -rp lib/groovy/ $RPM_BUILD_ROOT%{_prefix}/libs

%post
if ! getent passwd baltrad > /dev/null; then
  adduser --system --home /var/lib/baltrad --no-create-home \
    --shell /bin/bash -g baltrad baltrad
fi
    
if ! getent group baltrad > /dev/null; then
  groupadd --system baltrad
fi
  
if ! id -Gn baltrad | grep -qw baltrad; then
  adduser baltrad baltrad
fi

#mkdir -p /var/lib/baltrad
#chmod 1775 /var/lib/baltrad
#chown root:baltrad /var/lib/baltrad

mkdir -p /var/log/baltrad
chmod 1775 /var/log/baltrad
chown root:baltrad /var/log/baltrad

mkdir -p /var/run/baltrad
chmod 1775 /var/run/baltrad
chown root:baltrad /var/run/baltrad

%files
/usr/share/baltrad/baltrad-node-tomcat/*
%attr(-,baltrad,baltrad) /var/lib/baltrad/baltrad-node-tomcat/*
%attr(-,baltrad,baltrad) /var/lib/baltrad/baltrad-node-tomcat/policy/*
%attr(-,baltrad,baltrad) /var/lib/baltrad/baltrad-node-tomcat/webapps/*
%attr(4755,baltrad,baltrad) /var/log/baltrad/baltrad-node-tomcat
%attr(4640,root,baltrad) /etc/baltrad/baltrad-node-tomcat/*
%attr(4755,root,baltrad) /etc/baltrad/baltrad-node-tomcat
#%attr(4755,baltrad,baltrad) /var/run/baltrad
#-rw-r----- 1 root baltrad   7746 okt  7 11:45 catalina.properties
#-rw-r----- 1 root baltrad   1338 okt  7 11:45 context.xml
#-rw-r----- 1 root baltrad   1149 okt  7 11:45 jaspic-providers.xml
#-rw-r----- 1 root baltrad   2313 okt  7 11:45 jaspic-providers.xsd
#-rw-r----- 1 root baltrad   3622 okt  7 11:45 logging.properties
#-rw-r----- 1 root baltrad   7869 okt  7 11:45 server.xml
#-rw-r----- 1 root baltrad   2164 okt  7 11:45 tomcat-users.xml
#-rw-r----- 1 root baltrad   2633 okt  7 11:45 tomcat-users.xsd
#-rw-r----- 1 root baltrad 169322 okt  7 11:45 web.xml
/etc/init.d/baltrad-node
/var/lib/baltrad/baltrad-node-tomcat/logs
/var/lib/baltrad/baltrad-node-tomcat/conf
/var/lib/baltrad/baltrad-node-tomcat/work
%attr(4775,baltrad,baltrad) /var/cache/baltrad-node-tomcat


#%{_prefix}/bin/beast.jar
#%{_prefix}/bin/pgfwkplugin
#%{_prefix}/bin/xmlrpcserver
#%{_prefix}/etc/*
#%{_prefix}/examples/*
#%{_prefix}/sql/*

