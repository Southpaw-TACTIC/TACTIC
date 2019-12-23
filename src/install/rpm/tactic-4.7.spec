# TACTIC 4.7

%define _topdir     /home/tactic/TACTIC-RPM
%define name        TACTIC
%define release     0
%define version     4.7.0.b02
%define buildroot   %{_top_dir}/%{name}-%{version}-root
%define user        tactic

#%define python3_sitelib /usr/lib/python3.7/site-packages

# To prevent binary stripping for specific rpm
%global __os_install_post %{nil}


BuildRoot:  %{buildroot}
Summary:	Workflow automation development environment TACTIC
Vendor:     Southpaw Technology Inc.
Name:		%{name}
Version:	%{version}
Release:	%{release}

Group:		Application/Productivity
License:	EPL
#URL:		

#BuildRequires:	
Requires: postgresql-server
Requires: python3
#Requires: python3-pillow
#Requires: python3-pycryptodomex
#Requires: python3-lxml
#Requires: python3-requests
#Requires: python3-pytz
Requires: httpd
Requires: chkconfig

%description
Workflow automation development environment TACTIC



Requires(pre): /usr/sbin/useradd, /usr/bin/getent
Requires(postrun): /usr/sbin/userdel

%pre
# add a user
/usr/bin/getent group %{user} > /dev/null || /usr/sbin/groupadd -r %{user}
/usr/bin/getent passwd %{user} > /dev/null || /usr/sbin/useradd -r -d /opt/tactic -s /bin/bash -g %{user} %{user}

%postun
case "$1" in
    0) # This is a yum remove.
         /usr/sbin/userdel %{user}
    ;;
    1) # This is a yum upgrade.
         # do nothing
    ;;
esac


%prep
echo "Prepare TACTIC"
rm -rf $RPM_BUILD_DIR/tactic-4.7
zcat $RPM_SOURCE_DIR/tactic-4.7.tar.gz | tar -xvf -

echo "Prepare Config"
rm -rf $RPM_BUILD_DIR/config-1.0.a01
zcat $RPM_SOURCE_DIR/config-1.0.a01.tar.gz | tar -xvf -


%build
echo "Building TACTIC"


%install

echo "Build Root: $RPM_BUILD_ROOT"

mkdir -p "$RPM_BUILD_ROOT/opt/tactic"
cp -R -f * "$RPM_BUILD_ROOT/opt/tactic"

install --directory "$RPM_BUILD_ROOT/opt/tactic"

install --directory "$RPM_BUILD_ROOT/opt/tactic/tactic_data"
install --directory "$RPM_BUILD_ROOT/opt/tactic/tactic_data/config"
install --directory "$RPM_BUILD_ROOT/opt/tactic/tactic_data/plugins"
install --directory "$RPM_BUILD_ROOT/opt/tactic/tactic_data/templates"
install --directory "$RPM_BUILD_ROOT/opt/tactic/tactic_data/dist"

install --directory "$RPM_BUILD_ROOT/opt/tactic/tactic_temp"
install --directory "$RPM_BUILD_ROOT/opt/tactic/assets"


#chmod 755 "$RPM_BUILD_ROOT/opt/tactic"
#chmod 755 "$RPM_BUILD_ROOT/opt/tactic/tactic_data"
#chown -R tactic.tactic "$RPM_BUILD_ROOT/opt/tactic"
#chown -R tactic.tactic "$RPM_BUILD_ROOT/opt/tactic/tactic_data"


# TACTIC Config (tactic-conf.xml) and TACTIC License
install -m 644 $RPM_BUILD_DIR/config/template/config/tactic-license.xml $RPM_BUILD_ROOT/opt/tactic/tactic_data/config/tactic-license.xml
install -m 644 $RPM_BUILD_DIR/config/template/config/tactic_linux-conf_python3.xml $RPM_BUILD_ROOT/opt/tactic/tactic_data/config/tactic-conf.xml


# for install, put files in Python site packages
# /lib/python3.7/site-packages
mkdir -p "$RPM_BUILD_ROOT/etc/httpd/conf.d"
install -m 644 $RPM_BUILD_DIR/config/apache/tactic.conf $RPM_BUILD_ROOT/etc/httpd/conf.d/

# TACTIC Bootstrap Python Module
#mkdir -p "$RPM_BUILD_ROOT/%{python3_sitelib}/tacticenv"
#install -m 644 $RPM_BUILD_DIR/config/data/* $RPM_BUILD_ROOT/%{python3_sitelib}/tacticenv


# TACTIC Service Script
mkdir -p "$RPM_BUILD_ROOT/etc/init.d"
install -m 755 $RPM_BUILD_DIR/config/service/tactic_python3 $RPM_BUILD_ROOT/etc/init.d/tactic


%post
if [ "$1" = "1" ]; then
 chkconfig --add tactic
 chkconfig --level 235 tactic on
fi

# Create tacticenv directory in /usr/lib/python3.x/site_packages/
# and copy tacticenv/* into the newly created directory.
# TODO: we can't cleanly remove this in the uninstall. If we remove this in the %postun section,
# it causes problems during the upgrade. At the moment, /usr/lib/python3.x/site_packages/tacticenv
# needs to be manually removed after uninstalling TACTIC.
PY3_LIB=`/usr/bin/python3 -c 'from distutils.sysconfig import get_python_lib; import sys; sys.stdout.write(get_python_lib())'`
TACTIC_ENV_DIR="$PY3_LIB/tacticenv"
if [ ! -d "$TACTIC_ENV_DIR" ]; then
    echo "Creating $TACTIC_ENV_DIR"
    mkdir "$TACTIC_ENV_DIR"
fi
cp /opt/tactic/tactic/src/install/data/* "$PY3_LIB/tacticenv/"

echo "TACTIC_INSTALL_DIR='/opt/tactic/tactic'" >> "$PY3_LIB/tacticenv/tactic_paths.py"
echo "TACTIC_SITE_DIR=''" >> "$PY3_LIB/tacticenv/tactic_paths.py"
echo "TACTIC_DATA_DIR='/opt/tactic/tactic_data'" >> "$PY3_LIB/tacticenv/tactic_paths.py"
echo "" >> "$PY3_LIB/tacticenv/tactic_paths.py"

echo "For Initial Setup, please execute:"
echo
echo "python3 src/pyasm/search/upgrade/postgresql/bootstrap_load.py"
echo
echo



%files
%defattr(-, %{user}, %{user})
/opt/tactic/
%dir %attr(0755, %{user}, %{user}) /opt/tactic/
%dir %attr(0755, %{user}, %{user}) /opt/tactic/tactic_temp
%dir %attr(0755, %{user}, %{user}) /opt/tactic/tactic_data
%dir %attr(0755, %{user}, %{user}) /opt/tactic/tactic_data/config
%attr(-, %{user}, %{user}) /opt/tactic/tactic_data/config/tactic-conf.xml
%attr(-, %{user}, %{user}) /opt/tactic/tactic_data/config/tactic-license.xml
%dir %attr(0755, %{user}, %{user}) /opt/tactic/tactic_data/plugins
%dir %attr(0755, %{user}, %{user}) /opt/tactic/tactic_data/templates
%dir %attr(0755, %{user}, %{user}) /opt/tactic/tactic_data/dist
%dir %attr(0755, %{user}, %{user}) /opt/tactic/assets
#%{python3_sitelib}/tacticenv


%config
%config(noreplace) /opt/tactic/tactic_data/*
%config(noreplace) /etc/httpd/conf.d/tactic.conf
%config(noreplace) /etc/init.d/tactic



%clean
[ "${RPM_BUILD_ROOT}" != "/" ] && rm -rf ${RPM_BUILD_ROOT}
[ "${RPM_BUILD_DIR}" != "/" ] && rm -rf ${RPM_BUILD_DIR}/*

