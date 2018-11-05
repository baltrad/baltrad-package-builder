%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(0)")}
%define _prefix /usr/lib/rave

Name: rave
Version: %{version}
Release: %{snapshot}%{?dist}
Summary: RAVE - Product generation framework and toolbox. Injector using ODIM_H5 files
License: GPL-3 and LGPL-3
URL: http://www.baltrad.eu/
Source0: %{name}-%{version}.tar.gz
Source1: rave.conf
Patch1: 001-raved.patch
Patch2: 002-rave_defines.patch
BuildRequires: hlhdf-devel
BuildRequires: hlhdf-python
BuildRequires: hdf5-devel
BuildRequires: zlib-devel
BuildRequires: python2-devel
BuildRequires: netcdf-devel
# Workaround for centos6
BuildRequires: atlas
BuildRequires: numpy
BuildRequires: proj-devel
#expat requires
Requires: expat
Requires: netcdf
Requires: hlhdf
BuildRequires: expat-devel
# Don't see any actual imports, just mentioned in README
#BuildRequires: python-pycurl

%description
Product generation framework and toolbox. Injector using ODIM_H5 files

%package devel
Summary: RAVE development files
Group: Development/Libraries
Requires: %{name} = %{version}-%{release}
# rave development headers include headers from proj
Requires: proj-devel
# arrayobject.h and other needs
Requires: numpy
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

%build
%configure --prefix=/usr/lib/rave --with-hlhdf=/usr/lib/hlhdf --with-expat --with-bufr=/usr/lib/bbufr --with-netcdf=yes
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
mkdir -p %{buildroot}%{python_sitearch}
echo "/usr/lib/rave/lib">> %{buildroot}/etc/ld.so.conf.d/rave.conf
echo "/usr/lib/rave/Lib">> %{buildroot}/etc/ld.so.conf.d/rave.conf
make install DESTDIR=%{buildroot}
install -p -D -m 0644 %{SOURCE1} %{buildroot}%{_sysconfdir}/ld.so.conf.d/rave.conf
cp etc/raved %{buildroot}/etc/init.d/
mv %{buildroot}/usr/lib/rave/Lib/rave_defines.py %{buildroot}/etc/baltrad/rave/Lib/
mv %{buildroot}/usr/lib/rave/config/*.xml %{buildroot}/etc/baltrad/rave/config/
mv %{buildroot}/usr/lib/rave/etc/rave_pgf_quality_registry.xml %{buildroot}/etc/baltrad/rave/etc/
mv %{buildroot}/usr/lib/rave/etc/rave_pgf_registry.xml %{buildroot}/etc/baltrad/rave/etc/
mv %{buildroot}/usr/lib/rave/etc/rave_tile_registry.xml %{buildroot}/etc/baltrad/rave/etc/
mv %{buildroot}/usr/lib/rave/etc/rave.pth %{buildroot}%{python_sitearch}
mv %{buildroot}/usr/lib/rave/etc/rave_pgf_queue.xml %{buildroot}/var/lib/baltrad/
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
python $TMPNAME
\rm -f $TMPNAME

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
%{python_sitearch}/rave.pth
/etc/init.d/raved
%attr(0664, root, baltrad) /etc/baltrad/rave/Lib/*.py
%exclude /etc/baltrad/rave/Lib/rave_defines.pyc
%exclude /etc/baltrad/rave/Lib/rave_defines.pyo
%attr(0664, root, baltrad) /etc/baltrad/rave/config/*.xml
%attr(0664, root, baltrad) /etc/baltrad/rave/etc/*.xml
/etc/ld.so.conf.d/rave.conf
%attr(775,root,baltrad) /var/run/baltrad
%attr(-,root,baltrad) /var/log/baltrad
%attr(-,baltrad,baltrad) /var/lib/baltrad/rave_pgf_queue.xml
%attr(-,baltrad,baltrad) /var/lib/baltrad/MSG_CT

%config(noreplace) %{python_sitelib}/rave.pth
%config(noreplace) %{_sysconfdir}/ld.so.conf.d/rave.conf

%files devel
%{_prefix}/include/python/*.h
%{_prefix}/include/*.h
