%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%define _prefix /usr/lib/baltrad-viewer
Name:		baltrad-viewer
Version: %{version}
Release: %{snapshot}%{?dist}
Summary:	Baltrad Viewer plugin
Group:		Development/Libraries
License:	LGPL
URL:		http://www.baltrad.eu/
Source0: %{name}-%{version}.tar.gz
Patch0:		001-setup.patch
BuildArch:	noarch
BuildRequires:	python2-devel
BuildRequires:  python-distribute
BuildRequires:	hlhdf-python
Requires:	python2
Requires:	hlhdf-python
Requires:	hlhdf
Requires:	rave
Requires:   php
Requires:   php-common
%description

%clean
rm -rf %{buildroot}


%prep
%setup -q
%patch0 -p1

%build

%install
mkdir -p %{buildroot}%{_prefix}
mkdir -p %{buildroot}%{_prefix}/Lib
mkdir -p %{buildroot}%{python_sitelib}
%{__python} setup.py install --prefix=/usr/lib --root=%{buildroot}
mv %{buildroot}/usr/lib/lib/python2.7/site-packages/*.py* %{buildroot}/usr/lib/baltrad-viewer/Lib/
mv %{buildroot}/usr/lib/lib/python2.7/site-packages/*.egg-info %{buildroot}/usr/lib/baltrad-viewer/Lib/
echo "/usr/lib/baltrad-viewer/Lib" > %{buildroot}/usr/lib/python2.7/site-packages/baltrad-viewer.pth

%files
#%doc %{_prefix}/rave_gmap/COPYING
#%doc %{_prefix}/rave_gmap/COPYING.LESSER
#%doc %{_prefix}/rave_gmap/LICENSE
#%doc %{_prefix}/rave_gmap/README
#%doc %{_prefix}/rave_gmap/README.ravepgf
#%doc %{_prefix}/rave_gmap/README2
#%{python_sitelib}/rave_gmap.pth
#%{_prefix}
#%{_prefix}
%{_prefix}
/usr/lib/python2.7/site-packages/baltrad-viewer.pth

%changelog

