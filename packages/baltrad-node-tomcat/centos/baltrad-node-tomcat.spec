%define _prefix /
%{?systemd_requires}

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

%preun
sudo /etc/init.d/baltrad-node stop || :
%systemd_postun baltrad-node.service || :

%post
BALTRAD_USER="baltrad"
BALTRAD_GROUP="baltrad"

#[ # Reading value of  SMHI_MODE. Handles enviroments: utv, test and prod where prod is default This is just for testing & development purposes
#-f /etc/profile.d/smhi.sh ] && . /etc/profile.d/smhi.sh

# This code is uniquely defined for internal use at SMHI so that we can automatically test
# and/or deploy the software. However, the default behaviour should always be that baltrad
# uses a system user.
# SMHI_MODE contains utv,test,prod.
if [[ -f /etc/profile.d/smhi.sh ]]; then
  BALTRAD_GROUP=baltradg
  . /etc/profile.d/smhi.sh
  if [[ "$SMHI_MODE" = "utv" ]];then
    BALTRAD_USER="baltra.u"
    BALTRAD_GROUP="baltragu"
  elif [[ "$SMHI_MODE" = "test" ]];then
    BALTRAD_USER="baltra.t"
    BALTRAD_GROUP="baltragt"
  fi
  TMPFILE=`mktemp`
  cat /etc/init.d/baltrad-node | sed -e"s/BALTRAD_USER=baltrad/BALTRAD_USER=baltra.u/g" | sed -e"s/BALTRAD_GROUP=baltrad/BALTRAD_GROUP=baltragu/g" > $TMPFILE
  cat $TMPFILE > /etc/init.d/baltrad-node
  chmod 755 /etc/init.d/baltrad-node
  \rm -f $TMPFILE
else
  if ! getent group $BALTRAD_GROUP > /dev/null; then
    groupadd --system $BALTRAD_GROUP
  fi

  if ! getent passwd "$BALTRAD_USER" > /dev/null; then
    adduser --system --home /var/lib/baltrad --no-create-home --shell /bin/bash -g $BALTRAD_GROUP $BALTRAD_USER
  fi
fi

mkdir -p /var/run/baltrad

chmod 0775 /etc/baltrad
chmod 0775 /var/lib/baltrad
chmod 0775 /var/log/baltrad
chmod 0775 /var/run/baltrad

chown root:$BALTRAD_GROUP /var/lib/baltrad
chown root:$BALTRAD_GROUP /var/log/baltrad
chown root:$BALTRAD_GROUP /var/run/baltrad
chown root:$BALTRAD_GROUP /etc/baltrad

chown $BALTRAD_USER:$BALTRAD_GROUP /var/lib/baltrad/baltrad-node-tomcat
chown $BALTRAD_USER:$BALTRAD_GROUP /var/lib/baltrad/baltrad-node-tomcat/*
chown $BALTRAD_USER:$BALTRAD_GROUP /var/lib/baltrad/baltrad-node-tomcat/policy/*
chown $BALTRAD_USER:$BALTRAD_GROUP /var/lib/baltrad/baltrad-node-tomcat/webapps/*
chown $BALTRAD_USER:$BALTRAD_GROUP /var/lib/baltrad/baltrad-node-tomcat/logs
chown $BALTRAD_USER:$BALTRAD_GROUP /var/lib/baltrad/baltrad-node-tomcat/conf
chown $BALTRAD_USER:$BALTRAD_GROUP /var/lib/baltrad/baltrad-node-tomcat/work

chmod 4755 /var/log/baltrad/baltrad-node-tomcat
chown $BALTRAD_USER:$BALTRAD_GROUP /var/log/baltrad/baltrad-node-tomcat
chmod 0775 /etc/baltrad/baltrad-node-tomcat
chown root:$BALTRAD_GROUP /etc/baltrad/baltrad-node-tomcat
chmod 0660 /etc/baltrad/baltrad-node-tomcat/*
chown root:$BALTRAD_GROUP /etc/baltrad/baltrad-node-tomcat/*
chmod 4775 /var/cache/baltrad-node-tomcat
chown $BALTRAD_USER:$BALTRAD_GROUP /var/cache/baltrad-node-tomcat 

%files
/usr/share/baltrad/baltrad-node-tomcat/*
/var/lib/baltrad/baltrad-node-tomcat
/var/lib/baltrad/baltrad-node-tomcat/*
/var/lib/baltrad/baltrad-node-tomcat/policy/*
/var/lib/baltrad/baltrad-node-tomcat/webapps/*
/var/lib/baltrad/baltrad-node-tomcat/logs
/var/lib/baltrad/baltrad-node-tomcat/conf
/var/lib/baltrad/baltrad-node-tomcat/work
/var/log/baltrad/baltrad-node-tomcat
/etc/baltrad/baltrad-node-tomcat
/etc/baltrad/baltrad-node-tomcat/*
/etc/init.d/baltrad-node
/var/cache/baltrad-node-tomcat

