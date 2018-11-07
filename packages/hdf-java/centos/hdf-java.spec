Name:           jhdf5
Version:        2.8
Release:        %{snapshot}%{?dist}
Summary:        Java HDF5 Package

Group:          Development/Libraries
License:        BSD with advertising
URL:            http://www.hdfgroup.org/hdf-java-html/
Source0:        hdf-java-%{version}.tar.gz
Source1:        hdfview
Source2:        hdfview.xml
Source3:        hdfview.desktop

Patch1:         0001-add-a-generic-linux-host.patch
Patch2:         0002-add-H4_-prefix-to-constants.patch
Patch3:         0003-use-system-linker-for-shared-library.patch
Patch4:         0004-remove-writable-prefix-check.patch
Patch5:         0005-update-config.sub-and-config.guess.patch
Patch7:         0007-update-configure.patch

BuildRequires:  jpackage-utils
BuildRequires:  java-devel
BuildRequires:  hdf5-devel

Requires:       jpackage-utils
Requires:       java
# hdf5 does not bump soname but check at runtime
Requires:       hdf5 >= 1.8.5

%description
HDF is a versatile data model that can represent very complex data objects
and a wide variety of meta-data. It is a completely portable file format
with no limit on the number or size of data objects in the collection.

This Java package wrap the native HDF5 library.

%package devel
Summary: JHDF5 development files
Group: Development/Libraries
Requires: %{name} = %{version}-%{release}
Requires: hdf5-devel

%description devel
JHDF5 development headers and libraries.

%package -n jhdf
Summary:        Java HDF Package
Group:          Development/Libraries

BuildRequires:  jpackage-utils
BuildRequires:  java-1.8.0-openjdk-devel
BuildRequires:  hdf-devel

Requires:       jpackage-utils
Requires:       java

%description -n jhdf
HDF is a versatile data model that can represent very complex data objects
and a wide variety of meta-data. It is a completely portable file format
with no limit on the number or size of data objects in the collection.

This Java package wrap the native HDF4 library.

%package -n jhdfobj
Summary:        Java HDF/HDF5 Object Package
Group:          Development/Libraries

BuildRequires:  jpackage-utils
BuildRequires:  java-devel
BuildRequires:  hdf5-devel
BuildRequires:  hdf-devel

Requires:       jpackage-utils
Requires:       java
Requires:       hdf
# hdf5 does not bump soname but check at runtime
Requires:       hdf5 >= 1.8.5
Requires:       jhdf = %{version}-%{release}
Requires:       jhdf5 = %{version}-%{release}

BuildArch:      noarch

%description -n jhdfobj
HDF is a versatile data model that can represent very complex data objects
and a wide variety of meta-data. It is a completely portable file format
with no limit on the number or size of data objects in the collection.

This Java package implements HDF4/HDF5 data objects in an 
object-oriented form. It provides a common Java API for accessing HDF files.


%package -n hdfview
Summary:        Java HDF Object viewer
Group:          Applications/File

BuildRequires:  jpackage-utils
BuildRequires:  java-devel

# for convert
BuildRequires:  ImageMagick
# for desktop-file-install
BuildRequires:  desktop-file-utils

Requires:       jpackage-utils
Requires:       java
Requires:       jhdfobj = %{version}-%{release}

Requires(post): desktop-file-utils
Requires(postun): desktop-file-utils

BuildArch:      noarch

%description -n hdfview
HDF is a versatile data model that can represent very complex data objects
and a wide variety of meta-data. It is a completely portable file format
with no limit on the number or size of data objects in the collection.

This package provides a HDF4/HDF5 viewer.


%prep
%setup -q -n hdf-java
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1
%patch7 -p1

# remove shipped jars
rm $(find -name \*.jar)

# fix spurious-executable-perm
chmod -x $(find docs -type f)
chmod -x $(find native -type f)
chmod -x COPYING

# fix wrong-file-end-of-line-encoding 
sed -i 's/\r//' docs/hdfview/UsersGuide/RELEASE.txt

%build
%configure --with-jdk=%{java_home}/include,%{java_home}/lib \
        --with-hdf5=%{_includedir},%{_libdir} \
        --with-hdf4=%{_includedir}/hdf,%{_libdir}/hdf \
        --without-h4toh5 \
        --without-libsz \
        --with-libz=%{_includedir},%{_libdir} \
        --with-libjpeg=%{_includedir},%{_libdir}

# Make JNI (libjhdf.so libjhdf5.so) and
# make only required jars (not netcdf nor fits related packages)
pushd .
cd ncsa; \
make
popd

make natives jhdf-packages jhdf5-packages \
     jhdfobj-packages jhdfview-packages

%install

# jhdf5 jars
install -dm 755 %{buildroot}%{_javadir}
install -pm 0644 lib/jhdf5.jar %{buildroot}%{_javadir}/jhdf5.jar

# jhdf5 lib
install -dm 755 %{buildroot}%{_jnidir}
install -m 744 lib/linux/libjhdf5.so %{buildroot}%{_jnidir}

# jhdf jars
install -dm 755 %{buildroot}%{_javadir}
install -pm 0644 lib/jhdf.jar %{buildroot}%{_javadir}/jhdf.jar

# jhdf lib
install -dm 755 %{buildroot}%{_jnidir}
install -m 744 lib/linux/libjhdf.so %{buildroot}%{_jnidir}

# jhdfobj jars
install -dm 755 %{buildroot}%{_javadir}
install -pm 0644 lib/jhdfobj.jar %{buildroot}%{_javadir}/jhdfobj.jar
install -pm 0644 lib/jhdf4obj.jar %{buildroot}%{_javadir}/jhdf4obj.jar
install -pm 0644 lib/jhdf5obj.jar %{buildroot}%{_javadir}/jhdf5obj.jar

# hdfview
install -dm 755 %{buildroot}%{_javadir}
install -pm 0644 lib/jhdfview.jar %{buildroot}%{_javadir}/jhdfview.jar

install -dm 755 %{buildroot}%{_bindir}
install -m 755 %{SOURCE1} %{buildroot}%{_bindir}/hdfview

# Create and install hicolor icons.
for i in 16 22 32 48 ; do
  mkdir -p icons/${i}x${i}/apps

  mkdir -p %{buildroot}%{_datadir}/icons/hicolor/${i}x${i}/apps
  mkdir -p %{buildroot}%{_datadir}/icons/hicolor/${i}x${i}/mimetypes

  convert -resize ${i}x${i} ncsa/hdf/view/icons/hdf_large.gif \
    icons/${i}x${i}/apps/hdfview.png

  install -pm 0644 icons/${i}x${i}/apps/hdfview.png \
    %{buildroot}%{_datadir}/icons/hicolor/${i}x${i}/apps/hdfview.png

  install -pm 0644 icons/${i}x${i}/apps/hdfview.png \
    %{buildroot}%{_datadir}/icons/hicolor/${i}x${i}/mimetypes/application-x-hdf.png

done

# .desktop file
mkdir -p %{buildroot}%{_datadir}/applications
desktop-file-install                                    \
        --dir %{buildroot}%{_datadir}/applications      \
        %{SOURCE3}

# mime types
mkdir -p %{buildroot}%{_datadir}/mime/packages
install -p -D -m 644 %{SOURCE2} \
        %{buildroot}%{_datadir}/mime/packages/hdfview.xml

%clean
rm -rf %{buildroot}

%post -n hdfview
update-desktop-database &> /dev/null || :
update-mime-database %{_datadir}/mime &> /dev/null || :
touch --no-create %{_datadir}/icons/hicolor &>/dev/null || :
gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :

%postun -n hdfview
update-desktop-database &> /dev/null || :
update-mime-database %{_datadir}/mime &> /dev/null || :
if [ $1 -eq 0 ] ; then
    /bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null || :
    gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :
fi

%posttrans -n hdfview
gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :

%files
%{_javadir}/jhdf5.jar
%attr(755,root,root) %{_jnidir}/libjhdf5.so
%doc COPYING Readme.txt

%files -n jhdf
%{_javadir}/jhdf.jar
%attr(755,root,root) %{_jnidir}/libjhdf.so
%doc COPYING Readme.txt

%files -n jhdfobj
%{_javadir}/jhdfobj.jar
%{_javadir}/jhdf4obj.jar
%{_javadir}/jhdf5obj.jar
%doc COPYING Readme.txt

%files -n hdfview
%{_bindir}/hdfview
%{_datadir}/applications/hdfview.desktop
%{_datadir}/icons/hicolor/*/*/*
%{_datadir}/mime/packages/hdfview.xml
%{_javadir}/jhdfview.jar
%doc COPYING Readme.txt
%doc docs 
