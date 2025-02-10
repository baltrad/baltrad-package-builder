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
Source2: rave-tmpfiles.d.conf
Patch1: 001-raved.patch
Patch2: 002-rave_defines.patch
Patch3: 003-raved-service.patch
Patch4: 004-odiminjectord-service.patch
Patch5: 005-odim_injector_bltroot.patch
BuildRequires: hlhdf-devel
BuildRequires: hlhdf-python
BuildRequires: hdf5-devel
BuildRequires: zlib-devel
BuildRequires: python36-devel
BuildRequires: netcdf-devel
BuildRequires: atlas
BuildRequires: python3-numpy
BuildRequires: proj49-blt
BuildRequires: systemd
BuildRequires: expat-devel
Requires: expat
Requires: netcdf
Requires: hlhdf
Requires: python3-numpy
Requires: python36
Requires: python3-daemon
Requires: python3-sqlalchemy
Requires: python36-jprops-blt
Requires: python36-keyczar-blt
Requires: python36-sqlalchemy-migrate-blt
Conflicts: rave-py27

%description
Product generation framework and toolbox. Injector using ODIM_H5 files

%package devel
Summary: RAVE development files
Group: Development/Libraries
Requires: %{name} = %{version}-%{release}
# rave development headers include headers from proj
Requires: proj49-blt
# arrayobject.h and other needs
Requires: python3-numpy
Requires: hlhdf-devel
Conflicts: rave-py27-devel
Requires: atlas
Requires: bbufr

%description devel
RAVE development headers and libraries.

%prep
%setup -q
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1

%build
make distclean || true
%configure --prefix=/usr/lib/rave --with-hlhdf=/usr/lib/hlhdf --with-legacy-proj=/usr/lib/proj49-blt/include,/usr/lib/proj49-blt/lib64 --with-expat --with-bufr=/usr/lib/bbufr --with-netcdf=yes  --enable-py3support --with-py3bin=python3.6 --with-py3bin-config=python3.6-config --with-python-makefile=/usr/lib64/python3.6/config-3.6m-x86_64-linux-gnu/Makefile
make

%install

# FIXME: Why is this mkdir necessary?
# With full _prefix the custom installscripts think there was already an old version
# present and does some special things we may not want (migration to newer version)
rm -rf %{buildroot}
mkdir -p %{buildroot}
mkdir -p %{buildroot}/usr/lib/rave
mkdir -p %{buildroot}/usr/bin
mkdir -p %{buildroot}/etc/init.d
mkdir -p %{buildroot}/etc/ld.so.conf.d
mkdir -p %{buildroot}/etc/baltrad/rave/Lib
mkdir -p %{buildroot}/etc/baltrad/rave/etc
mkdir -p %{buildroot}/etc/baltrad/rave/config
mkdir -p %{buildroot}/var/run/baltrad
mkdir -p %{buildroot}/var/log/baltrad
mkdir -p %{buildroot}/var/lib/baltrad/odim_injector/data
mkdir -p %{buildroot}/var/lib/baltrad/MSG_CT
mkdir -p %{buildroot}%{python36_sitelib}
echo "/usr/lib/rave/Lib">> %{buildroot}/etc/ld.so.conf.d/rave.conf
make install DESTDIR=%{buildroot}
cp %{buildroot}/usr/lib/rave/bin/fm12_importer %{buildroot}/usr/bin/ 
cp %{buildroot}/usr/lib/rave/bin/odim_injector %{buildroot}/usr/bin/ 
cp %{buildroot}/usr/lib/rave/bin/odim_injector.sh %{buildroot}/usr/bin/ 
cp %{buildroot}/usr/lib/rave/bin/rave_pgf %{buildroot}/usr/bin/ 
cp %{buildroot}/usr/lib/rave/bin/rave_pgf_logger %{buildroot}/usr/bin/ 
%py_byte_compile %{__python36} %{buildroot}/usr/lib/rave/Lib || :
install -p -D -m 0644 %{SOURCE1} %{buildroot}%{_sysconfdir}/ld.so.conf.d/rave.conf
install -p -D -m 0644 %{SOURCE2} %{buildroot}%{_tmpfilesdir}/rave.conf
mkdir -p %{buildroot}/%{_unitdir}
cp etc/raved.service %{buildroot}/%{_unitdir}/raved.service
cp etc/odiminjectord.service %{buildroot}/%{_unitdir}/odiminjectord.service
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

%pre
if [ "$1" = "2" ]; then
  systemctl stop raved || :
  systemctl stop odiminjectord || :
fi

%post
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

if [[ "$BALTRAD_USER" == *\.* ]]; then
  echo "User id $BALTRAD_USER contains a ., replacing with numerical user id."
  BALTRAD_USER=`id -u $BALTRAD_USER`
fi

TMPFILE=`mktemp`
cat %{_unitdir}/raved.service | sed -e"s/^User=baltrad.*/User=$BALTRAD_USER/g" | sed -e"s/^Group=baltrad.*/Group=$BALTRAD_GROUP/g" > $TMPFILE
cat $TMPFILE > %{_unitdir}/raved.service
chmod 644 %{_unitdir}/raved.service
\rm -f $TMPFILE

cat %{_unitdir}/odiminjectord.service | sed -e"s/^User=baltrad.*/User=$BALTRAD_USER/g" | sed -e"s/^Group=baltrad.*/Group=$BALTRAD_GROUP/g" > $TMPFILE
cat $TMPFILE > %{_unitdir}/odiminjectord.service
chmod 644 %{_unitdir}/odiminjectord.service
\rm -f $TMPFILE 

echo "d /var/run/baltrad 0775 root $BALTRAD_GROUP -" > %{_tmpfilesdir}/rave.conf

/sbin/ldconfig
TMPNAME=`mktemp /tmp/XXXXXXXXXX.py`
  
cat <<EOF > $TMPNAME
from rave_pgf_registry import PGF_Registry
a=PGF_Registry(filename="/etc/baltrad/rave/etc/rave_pgf_registry.xml")
a.deregister('eu.baltrad.beast.generatesite2d')
a.register('eu.baltrad.beast.generatesite2d', 'rave_pgf_site2D_plugin', 'generate', 'Generate Site2D plugin', 'area,quantity,method,date,time,anomaly-qc,qc-mode,prodpar,applygra,ignore-malfunc,ctfilter,pcsid,algorithm_id', '', 'height,range,zrA,zrb,xscale,yscale')
a.deregister('eu.baltrad.beast.generatecomposite')
a.register('eu.baltrad.beast.generatecomposite', 'rave_pgf_composite_plugin', 'generate', 'Generate composite plugin', 'area,quantity,method,date,time,selection,interpolation_method,anomaly-qc,qc-mode,reprocess_qfields,prodpar,applygra,ignore-malfunc,ctfilter,qitotal_field,algorithm_id,merge', '', 'height,range,zrA,zrb')
a.deregister('eu.baltrad.beast.generatevolume')
a.register('eu.baltrad.beast.generatevolume', 'rave_pgf_volume_plugin', 'generate', 'Polar volume generation from individual scans', 'source,date,time,anomaly-qc,qc-mode,algorithm_id,merge', '', 'height,range,zrA,zrb')
a.deregister('se.smhi.rave.creategmapimage')
a.register('se.smhi.rave.creategmapimage', 'googlemap_pgf_plugin', 'generate', 'Google Map Plugin', 'outfile,date,time,algorithm_id', '', '')
a.deregister('eu.baltrad.beast.applyqc')
a.register('eu.baltrad.beast.applyqc', 'rave_pgf_apply_qc_plugin', 'generate', 'Apply quality controls on a polar volume', 'date,time,anomaly-qc,qc-mode,algorithm_id,remove-malfunc', '', '')  
a.deregister('eu.baltrad.beast.generateacrr')
a.register('eu.baltrad.beast.generateacrr', 'rave_pgf_acrr_plugin', 'generate', 'Generate ACRR plugin', 'date,time,quantity,distancefield,applygra,productid', 'hours,N,accept', 'zra,zrb')  
EOF
%{__python36} $TMPNAME
\rm -f $TMPNAME

cat <<EOF > $TMPNAME
from rave_pgf_quality_registry_mgr import rave_pgf_quality_registry_mgr
a = rave_pgf_quality_registry_mgr("/etc/baltrad/rave/etc/rave_pgf_quality_registry.xml")
a.remove_plugin("qi-total:minimum")
a.remove_plugin("qi-total:additive")
a.remove_plugin("qi-total:multiplicative")
a.add_plugin("qi-total:minimum", "rave_qitotal_quality_plugin", "rave_qitotal_quality_minimum")
a.add_plugin("qi-total:additive", "rave_qitotal_quality_plugin", "rave_qitotal_quality_additive")
a.add_plugin("qi-total:multiplicative", "rave_qitotal_quality_plugin", "rave_qitotal_quality_multiplicative")
a.save("/etc/baltrad/rave/etc/rave_pgf_quality_registry.xml")
EOF
%{__python3} $TMPNAME
\rm -f $TMPNAME

mkdir -p /var/lib/baltrad
chmod 0775 /var/lib/baltrad
chown root:$BALTRAD_GROUP /var/lib/baltrad

mkdir -p /var/lib/baltrad/odim_injector/data
chmod 0775 /var/lib/baltrad/odim_injector
chown root:$BALTRAD_GROUP /var/lib/baltrad/odim_injector
chmod 0775 /var/lib/baltrad/odim_injector/data
chown root:$BALTRAD_GROUP /var/lib/baltrad/odim_injector/data

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

%preun
systemctl stop raved || :
systemctl stop odiminjectord || :
%systemd_preun raved.service || :
%systemd_preun odiminjectord.service || :

%postun 
/sbin/ldconfig
%systemd_postun raved.service || :
%systemd_postun odiminjectord.service || :

%files
%doc %{_prefix}/COPYING
%doc %{_prefix}/COPYING.LESSER
%doc %{_prefix}/LICENSE

# Move to a python module? But the subdir name is very bad for site-packages
%{_prefix}/Lib/*.py
%{_prefix}/Lib/__pycache__/*.pyc
%{_prefix}/Lib/_*.so
%{_prefix}/Lib/gadjust
%{_prefix}/Lib/ravemigrate
%{_prefix}/lib/*.so
%{_prefix}/bin/*
/usr/bin/*
%{_prefix}/config/*.xml
%{_prefix}/mkf/def.mk
%{_prefix}/rave.xbm
%{_prefix}/etc/rave_pgf
%{_prefix}/etc/rave_pgf_*.xml
%{_prefix}/etc/rave_tile_registry.xml
%{python36_sitelib}/rave.pth
%{_unitdir}/raved.service
%{_unitdir}/odiminjectord.service
%config /etc/baltrad/rave/Lib/*.py
%config /etc/baltrad/rave/config/*.xml
%config(noreplace) /etc/baltrad/rave/etc/*.xml

%{_sysconfdir}/ld.so.conf.d/rave.conf
%{_tmpfilesdir}/rave.conf
/var/lib/baltrad/rave_pgf_queue.xml
/var/lib/baltrad/MSG_CT

%files devel
%{_prefix}/include/python/*.h
%{_prefix}/include/*.h
