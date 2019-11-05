%global debug_package %{nil}
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
Patch3: 003-baltrad-node-service.patch
Source0: %{name}-%{version}.tar.gz
Source1: hdfobject.jar
Source2: COPYING.hdfobject
Source3: baltrad-node-tomcat-tmpfiles.d.conf
BuildRequires: java-hdf5

# Server binary needed
BuildRequires: systemd
Requires: java-1.8.0-openjdk
Requires: java-hdf5

%description
The baltrad node tomcat server is the adapted tomcat server that is suitable for
the baltrad web application.

%prep
%setup -q -n baltrad-node-tomcat
%patch1 -p1
%patch2 -p0
%patch3 -p0

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
mkdir -p %{buildroot}/etc/ld.so.conf.d
install -p -D -m 0644 %{SOURCE3} %{buildroot}%{_tmpfilesdir}/baltrad-node-tomcat.conf

mkdir -p %{buildroot}/%{_unitdir}
# Need to patch hdf-java to get so files into path
cp baltrad-node.service %{buildroot}/%{_unitdir}/baltrad-node.service
chmod 664 %{buildroot}/%{_unitdir}/baltrad-node.service
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
ln -s /usr/lib/java/hdf5.jar $RPM_BUILD_ROOT/usr/share/baltrad/baltrad-node-tomcat/lib/hdf5.jar
cp %{SOURCE1} $RPM_BUILD_ROOT/usr/share/baltrad/baltrad-node-tomcat/lib/
cp %{SOURCE2} $RPM_BUILD_ROOT/usr/share/baltrad/baltrad-node-tomcat/
cp LICENSE $RPM_BUILD_ROOT/usr/share/baltrad/baltrad-node-tomcat/
cp NOTICE $RPM_BUILD_ROOT/usr/share/baltrad/baltrad-node-tomcat/
cp README.md $RPM_BUILD_ROOT/usr/share/baltrad/baltrad-node-tomcat/

%preun
systemctl stop baltrad-node || :
%systemd_preun baltrad-node.service || :

%pre
if [[ -d /var/lib/baltrad/baltrad-node-tomcat/logs ]]; then
  rm -fr /var/lib/baltrad/baltrad-node-tomcat/logs*
fi
if [[ -d /var/lib/baltrad/baltrad-node-tomcat/work ]]; then
  rm -fr /var/lib/baltrad/baltrad-node-tomcat/work*
fi

%postun
%systemd_postun baltrad-node.service || :

%post
BALTRAD_USER="baltrad"
BALTRAD_GROUP="baltrad"

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
  if [[ "$BALTRAD_USER" == *\.* ]]; then
    echo "User id $BALTRAD_USER contains a ., replacing with numerical user id."
    BALTRAD_USER=`id -u $BALTRAD_USER`
  fi
  TMPFILE=`mktemp`
  cat %{_unitdir}/baltrad-node.service | sed -e"s/User=baltrad/User=$BALTRAD_USER/g" | sed -e"s/Group=baltrad/Group=$BALTRAD_GROUP/g" > $TMPFILE
  cat $TMPFILE > %{_unitdir}/baltrad-node.service
  chmod 644 %{_unitdir}/baltrad-node.service
  \rm -f $TMPFILE
  echo "d /var/run/baltrad 0775 root $BALTRAD_GROUP -" > %{_tmpfilesdir}/baltrad-node-tomcat.conf
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

chmod 4755 /var/log/baltrad/baltrad-node-tomcat
chown $BALTRAD_USER:$BALTRAD_GROUP /var/log/baltrad/baltrad-node-tomcat
chmod 0775 /etc/baltrad/baltrad-node-tomcat
chown root:$BALTRAD_GROUP /etc/baltrad/baltrad-node-tomcat
chmod 0660 /etc/baltrad/baltrad-node-tomcat/*
chown root:$BALTRAD_GROUP /etc/baltrad/baltrad-node-tomcat/*
chmod 4775 /var/cache/baltrad-node-tomcat
chown $BALTRAD_USER:$BALTRAD_GROUP /var/cache/baltrad-node-tomcat 

if [[ ! -f /usr/lib64/libhdf5_java.so ]]; then
  ln -s /usr/lib64/hdf5/libhdf5_java.so /usr/lib64/libhdf5_java.so
fi


%files
/usr/share/baltrad/baltrad-node-tomcat/*
/var/lib/baltrad/baltrad-node-tomcat
/var/lib/baltrad/baltrad-node-tomcat/*
/var/lib/baltrad/baltrad-node-tomcat/policy/*
/var/lib/baltrad/baltrad-node-tomcat/webapps/*
/var/lib/baltrad/baltrad-node-tomcat/conf
/var/log/baltrad/baltrad-node-tomcat
/etc/baltrad/baltrad-node-tomcat
/etc/baltrad/baltrad-node-tomcat/*
%{_unitdir}/baltrad-node.service
%{_tmpfilesdir}/baltrad-node-tomcat.conf
/var/cache/baltrad-node-tomcat

