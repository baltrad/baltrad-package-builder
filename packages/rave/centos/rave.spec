%{!?__python36: %global __python36 /usr/bin/python3.6}
%{!?python36_sitelib: %global python36_sitelib %(%{__python36} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}
%define _prefix /usr/lib/rave

Name: rave
Version: %{version}
Release: %{snapshot}%{?dist}
Summary: RAVE - Product generation framework and toolbox. Injector using ODIM_H5 files
License: LGPL-3
URL: http://www.baltrad.eu/
Source0: %{name}-%{version}.tar.gz
Source1: rave.conf
Patch1: 001-raved.patch
Patch2: 002-rave_defines.patch
Patch3: 003-raved-service.patch
BuildRequires: hlhdf-devel
BuildRequires: hlhdf-python
BuildRequires: hdf5-devel
BuildRequires: zlib-devel
BuildRequires: python36-devel
BuildRequires: netcdf-devel
# Workaround for centos6
BuildRequires: atlas
BuildRequires: python36-numpy
BuildRequires: proj-devel
BuildRequires: systemd
BuildRequires: expat-devel

Requires: expat
Requires: netcdf
Requires: hlhdf
Requires: python36-numpy
Requires: python36
Requires: python36-daemon-blt
Requires: python36-jprops-blt
Requires: python36-keyczar-blt
Requires: python36-psycopg2-blt
Requires: python36-pyinotify-blt
Requires: python36-sqlalchemy-blt
Requires: python36-sqlalchemy-migrate-blt
Conflicts: rave-py27

%description
Product generation framework and toolbox. Injector using ODIM_H5 files

%package devel
Summary: RAVE development files
Group: Development/Libraries
Requires: %{name} = %{version}-%{release}
# rave development headers include headers from proj
Requires: proj-devel
# arrayobject.h and other needs
Requires: python36-numpy
Requires: hlhdf-devel
Conflicts: rave-py27-devel

# Workaround for centos6
Requires: atlas
#
Requires: bbufr

%description devel
RAVE development headers and libraries.

%prep
%setup -q
%patch1 -p1
%patch2 -p1
%patch3 -p1

%build
make distclean || true
%configure --prefix=/usr/lib/rave --with-hlhdf=/usr/lib/hlhdf --with-expat --with-bufr=/usr/lib/bbufr --with-netcdf=yes  --enable-py3support --with-py3bin=python3 --with-py3bin-config=python3.6-config --with-python-makefile=/usr/lib64/python3.6/config-3.6m-x86_64-linux-gnu/Makefile
make

%install

# FIXME: Why is this mkdir necessary?
# With full _prefix the custom installscripts think there was already an old version
# present and does some special things we may not want (migration to newer version)
rm -rf %{buildroot}
mkdir -p %{buildroot}
mkdir -p %{buildroot}/usr/lib/rave
mkdir -p %{buildroot}/etc/init.d
mkdir -p %{buildroot}/etc/ld.so.conf.d
mkdir -p %{buildroot}/etc/baltrad/rave/Lib
mkdir -p %{buildroot}/etc/baltrad/rave/etc
mkdir -p %{buildroot}/etc/baltrad/rave/config
mkdir -p %{buildroot}/var/run/baltrad
mkdir -p %{buildroot}/var/log/baltrad
mkdir -p %{buildroot}/var/lib/baltrad
mkdir -p %{buildroot}/var/lib/baltrad/MSG_CT
mkdir -p %{buildroot}%{python36_sitelib}
echo "/usr/lib/rave/Lib">> %{buildroot}/etc/ld.so.conf.d/rave.conf
make install DESTDIR=%{buildroot}
install -p -D -m 0644 %{SOURCE1} %{buildroot}%{_sysconfdir}/ld.so.conf.d/rave.conf
mkdir -p %{buildroot}/%{_unitdir}
cp etc/raved.service %{buildroot}/%{_unitdir}/raved.service
mv %{buildroot}/usr/lib/rave/Lib/rave_defines.py %{buildroot}/etc/baltrad/rave/Lib/
mv %{buildroot}/usr/lib/rave/config/*.xml %{buildroot}/etc/baltrad/rave/config/
mv %{buildroot}/usr/lib/rave/etc/rave_pgf_quality_registry.xml %{buildroot}/etc/baltrad/rave/etc/
mv %{buildroot}/usr/lib/rave/etc/rave_pgf_registry.xml %{buildroot}/etc/baltrad/rave/etc/
mv %{buildroot}/usr/lib/rave/etc/rave_tile_registry.xml %{buildroot}/etc/baltrad/rave/etc/
mv %{buildroot}/usr/lib/rave/etc/rave.pth %{buildroot}%{python36_sitelib}
mv %{buildroot}/usr/lib/rave/etc/rave_pgf_queue.xml %{buildroot}/var/lib/baltrad/
\rm -f %{buildroot}/usr/lib/python3.6/site-packages/rave.pth
ln -s ../../../../var/lib/baltrad/rave_pgf_queue.xml %{buildroot}/usr/lib/rave/etc/rave_pgf_queue.xml
ln -s ../../../../etc/baltrad/rave/etc/rave_pgf_quality_registry.xml %{buildroot}/usr/lib/rave/etc/rave_pgf_quality_registry.xml
ln -s ../../../../etc/baltrad/rave/etc/rave_pgf_registry.xml %{buildroot}/usr/lib/rave/etc/rave_pgf_registry.xml
ln -s ../../../../etc/baltrad/rave/etc/rave_tile_registry.xml %{buildroot}/usr/lib/rave/etc/rave_tile_registry.xml
ln -s ../../../../etc/baltrad/rave/config/area_registry.xml 		%{buildroot}/usr/lib/rave/config/area_registry.xml
ln -s ../../../../etc/baltrad/rave/config/baltex_areas.xml 		%{buildroot}/usr/lib/rave/config/baltex_areas.xml
ln -s ../../../../etc/baltrad/rave/config/danish_radars.xml 		%{buildroot}/usr/lib/rave/config/danish_radars.xml
ln -s ../../../../etc/baltrad/rave/config/dutch_radars.xml 		%{buildroot}/usr/lib/rave/config/dutch_radars.xml
ln -s ../../../../etc/baltrad/rave/config/estonian_radars.xml 	%{buildroot}/usr/lib/rave/config/estonian_radars.xml
ln -s ../../../../etc/baltrad/rave/config/finnish_areas.xml		%{buildroot}/usr/lib/rave/config/finnish_areas.xml
ln -s ../../../../etc/baltrad/rave/config/finnish_radars.xml		%{buildroot}/usr/lib/rave/config/finnish_radars.xml
ln -s ../../../../etc/baltrad/rave/config/german_radars.xml		%{buildroot}/usr/lib/rave/config/german_radars.xml
ln -s ../../../../etc/baltrad/rave/config/hac_options.xml		%{buildroot}/usr/lib/rave/config/hac_options.xml
ln -s ../../../../etc/baltrad/rave/config/norwegian_projections.xml	%{buildroot}/usr/lib/rave/config/norwegian_projections.xml
ln -s ../../../../etc/baltrad/rave/config/norwegian_radars.xml	%{buildroot}/usr/lib/rave/config/norwegian_radars.xml
ln -s ../../../../etc/baltrad/rave/config/odim_quantities.xml	%{buildroot}/usr/lib/rave/config/odim_quantities.xml
ln -s ../../../../etc/baltrad/rave/config/odim_source.xml		%{buildroot}/usr/lib/rave/config/odim_source.xml
ln -s ../../../../etc/baltrad/rave/config/polish_areas.xml		%{buildroot}/usr/lib/rave/config/polish_areas.xml
ln -s ../../../../etc/baltrad/rave/config/polish_radars.xml		%{buildroot}/usr/lib/rave/config/polish_radars.xml
ln -s ../../../../etc/baltrad/rave/config/projection_registry.xml	%{buildroot}/usr/lib/rave/config/projection_registry.xml
ln -s ../../../../etc/baltrad/rave/config/projections.xml		%{buildroot}/usr/lib/rave/config/projections.xml
ln -s ../../../../etc/baltrad/rave/config/qitotal_options.xml	%{buildroot}/usr/lib/rave/config/qitotal_options.xml
ln -s ../../../../etc/baltrad/rave/config/radvol_params.xml		%{buildroot}/usr/lib/rave/config/radvol_params.xml
ln -s ../../../../etc/baltrad/rave/config/rave_quality_chain_registry.xml	%{buildroot}/usr/lib/rave/config/rave_quality_chain_registry.xml
ln -s ../../../../etc/baltrad/rave/config/swedish_areas.xml		%{buildroot}/usr/lib/rave/config/swedish_areas.xml
ln -s ../../../../etc/baltrad/rave/config/swedish_radars.xml		%{buildroot}/usr/lib/rave/config/swedish_radars.xml
ln -s ../../../../etc/baltrad/rave/Lib/rave_defines.py %{buildroot}/usr/lib/rave/Lib/rave_defines.py

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
  cat %{_unitdir}/raved.service | sed -e"s/User=baltrad/User=$BALTRAD_USER/g" | sed -e"s/Group=baltrad/Group=$BALTRAD_GROUP/g" > $TMPFILE
  cat $TMPFILE > %{_unitdir}/raved.service
  chmod 644 %{_unitdir}/raved.service
  \rm -f $TMPFILE 
else
  if ! getent group $BALTRAD_GROUP > /dev/null; then
    groupadd --system $BALTRAD_GROUP
  fi

  if ! getent passwd "$BALTRAD_USER" > /dev/null; then
    adduser --system --home /var/lib/baltrad --no-create-home --shell /bin/bash -g $BALTRAD_GROUP $BALTRAD_USER
  fi
fi

/sbin/ldconfig
TMPNAME=`mktemp /tmp/XXXXXXXXXX.py`
  
cat <<EOF > $TMPNAME
from rave_pgf_registry import PGF_Registry
a=PGF_Registry(filename="/etc/baltrad/rave/etc/rave_pgf_registry.xml")
a.deregister('eu.baltrad.beast.generatesite2d')
a.register('eu.baltrad.beast.generatesite2d', 'rave_pgf_site2D_plugin', 'generate', 'Generate Site2D plugin', 'area,quantity,method,date,time,anomaly-qc,qc-mode,prodpar,applygra,ignore-malfunc,ctfilter,pcsid,algorithm_id', '', 'height,range,zrA,zrb,xscale,yscale')
a.deregister('eu.baltrad.beast.generatecomposite')
a.register('eu.baltrad.beast.generatecomposite', 'rave_pgf_composite_plugin', 'generate', 'Generate composite plugin', 'area,quantity,method,date,time,selection,anomaly-qc,qc-mode,reprocess_qfields,prodpar,applygra,ignore-malfunc,ctfilter,qitotal_field,algorithm_id,merge', '', 'height,range,zrA,zrb')
a.deregister('eu.baltrad.beast.generatevolume')
a.register('eu.baltrad.beast.generatevolume', 'rave_pgf_volume_plugin', 'generate', 'Polar volume generation from individual scans', 'source,date,time,anomaly-qc,qc-mode,algorithm_id,merge', '', 'height,range,zrA,zrb')
a.deregister('se.smhi.rave.creategmapimage')
a.register('se.smhi.rave.creategmapimage', 'googlemap_pgf_plugin', 'generate', 'Google Map Plugin', 'outfile,date,time,algorithm_id', '', '')
a.deregister('eu.baltrad.beast.applyqc')
a.register('eu.baltrad.beast.applyqc', 'rave_pgf_apply_qc_plugin', 'generate', 'Apply quality controls on a polar volume', 'date,time,anomaly-qc,algorithm_id', '', '')  
EOF
%{__python36} $TMPNAME
\rm -f $TMPNAME

mkdir -p /var/lib/baltrad
chmod 0775 /var/lib/baltrad
chown root:$BALTRAD_GROUP /var/lib/baltrad

mkdir -p /var/log/baltrad
chmod 0775 /var/log/baltrad
chown root:$BALTRAD_GROUP /var/log/baltrad

mkdir -p /var/run/baltrad
chmod 0775 /var/run/baltrad
chown root:$BALTRAD_GROUP /var/run/baltrad

mkdir -p /etc/baltrad
chmod 0775 /etc/baltrad
chown root:$BALTRAD_GROUP /etc/baltrad

mkdir -p /etc/baltrad/rave/Lib
mkdir -p /etc/baltrad/rave/config
mkdir -p /etc/baltrad/rave/etc
chmod 0775 /etc/baltrad/rave
chmod 0775 /etc/baltrad/rave/Lib
chmod 0775 /etc/baltrad/rave/config
chmod 0775 /etc/baltrad/rave/etc
chown root:$BALTRAD_GROUP /etc/baltrad/rave
chown root:$BALTRAD_GROUP /etc/baltrad/rave/Lib
chown root:$BALTRAD_GROUP /etc/baltrad/rave/config
chown root:$BALTRAD_GROUP /etc/baltrad/rave/etc

chmod 0664 /etc/baltrad/rave/Lib/*.py
chown $BALTRAD_USER:$BALTRAD_GROUP /etc/baltrad/rave/Lib/*.py
chmod 0664 /etc/baltrad/rave/config/*.xml
chown $BALTRAD_USER:$BALTRAD_GROUP /etc/baltrad/rave/config/*.xml
chmod 0664 /etc/baltrad/rave/etc/*.xml
chown $BALTRAD_USER:$BALTRAD_GROUP /etc/baltrad/rave/etc/*.xml

chown $BALTRAD_USER:$BALTRAD_GROUP /var/lib/baltrad/rave_pgf_queue.xml
chown $BALTRAD_USER:$BALTRAD_GROUP /var/lib/baltrad/MSG_CT

%postun -p /sbin/ldconfig

%files
%doc %{_prefix}/COPYING
%doc %{_prefix}/COPYING.LESSER
%doc %{_prefix}/LICENSE

# Move to a python module? But the subdir name is very bad for site-packages
%{_prefix}/Lib/*.py
%{_prefix}/Lib/*.pyc
%{_prefix}/Lib/*.pyo
%{_prefix}/Lib/_*.so
%{_prefix}/Lib/gadjust
%{_prefix}/Lib/ravemigrate
%{_prefix}/lib/*.so
%{_prefix}/bin/*
%{_prefix}/config/*.xml
%{_prefix}/mkf/def.mk
%{_prefix}/rave.xbm
%{_prefix}/etc/rave_pgf
%{_prefix}/etc/rave_pgf_*.xml
%{_prefix}/etc/rave_tile_registry.xml
%{python36_sitelib}/rave.pth
%{_unitdir}/raved.service
/etc/baltrad/rave/Lib/*.py
%exclude /etc/baltrad/rave/Lib/rave_defines.pyc
%exclude /etc/baltrad/rave/Lib/rave_defines.pyo
/etc/baltrad/rave/config/*.xml
/etc/baltrad/rave/etc/*.xml
%{_sysconfdir}/ld.so.conf.d/rave.conf
/var/lib/baltrad/rave_pgf_queue.xml
/var/lib/baltrad/MSG_CT

#%config(noreplace) %{python36_sitelib}/rave.pth
#%config(noreplace) %{_sysconfdir}/ld.so.conf.d/rave.conf

%files devel
%{_prefix}/include/python/*.h
%{_prefix}/include/*.h
