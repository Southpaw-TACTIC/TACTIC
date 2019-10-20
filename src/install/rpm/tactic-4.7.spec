# TACTIC 4.7

%define _topdir     /home/tactic/TACTIC-RPM
%define name        TACTIC
%define release     0
%define version     4.7.0.a11
%define buildroot   %{_top_dir}/%{name}-%{version}-root
%define user        tactic


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
Requires: python3-pillow
Requires: python3-pycryptodomex
Requires: python3-lxml
Requires: python3-requests
Requires: python3-pytz
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
mkdir -p "$RPM_BUILD_ROOT/usr/lib/python3.7/site-packages/tacticenv"
install -m 644 $RPM_BUILD_DIR/config/data/* $RPM_BUILD_ROOT/usr/lib/python3.7/site-packages/tacticenv

# TACTIC Service Script
mkdir -p "$RPM_BUILD_ROOT/etc/init.d"
install -m 755 $RPM_BUILD_DIR/config/service/tactic_python3 $RPM_BUILD_ROOT/etc/init.d/tactic


%post
if [ "$1" = "1" ]; then
 chkconfig --add tactic
 chkconfig --level 235 tactic on
fi

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
/usr/lib/python3.7/site-packages/tacticenv


%config
%config(noreplace) /opt/tactic/tactic_data/*
%config(noreplace) /etc/httpd/conf.d/tactic.conf
%config(noreplace) /etc/init.d/tactic



%clean
[ "${RPM_BUILD_ROOT}" != "/" ] && rm -rf ${RPM_BUILD_ROOT}
[ "${RPM_BUILD_DIR}" != "/" ] && rm -rf ${RPM_BUILD_DIR}/*

