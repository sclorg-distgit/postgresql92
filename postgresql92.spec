%{!?scl_name_base: %global scl_name_base postgresql}
%{!?scl_name_version: %global scl_name_version 92}
%{!?scl:%global scl %{scl_name_base}%{scl_name_version}}
%scl_package %scl

# do not produce empty debuginfo package
%global debug_package %{nil}


Summary: Package that installs %scl
Name: %scl_name
Version: 1.1
Release: 20%{?dist}
License: GPLv2+
Group: Applications/File
Source0: README
Source1: LICENSE
Requires: scl-utils
Requires: %{scl_prefix}postgresql-server
BuildRequires: scl-utils-build help2man
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

%description
This is the main package for %scl Software Collection, which installs
necessary packages to use PostgreSQL 9.2 server. Software Collections allow
to install more versions of the same package by using alternative
directory structure.
Install this package if you want to use PostgreSQL 9.2 server on your system.

%package runtime
Summary: Package that handles %scl Software Collection.
Group: Applications/File
Requires: scl-utils
Requires(post): policycoreutils-python libselinux-utils

%description runtime
Package shipping essential scripts to work with %scl Software Collection.

%package build
Summary: Package shipping basic build configuration
Group: Applications/File
Requires: scl-utils-build

%description build
Package shipping essential configuration macros to build %scl Software
Collection or packages depending on %scl Software Collection.

%package scldevel
Summary: Package shipping development files for %scl

%description scldevel
Package shipping development files, especially usefull for development of
packages depending on %scl Software Collection.

%prep
%setup -c -T

# This section generates README file from a template and creates man page
# from that file, expanding RPM macros in the template file.
cat >README <<'EOF'
%{expand:%(cat %{SOURCE0})}
EOF

# copy the license file so %%files section sees it
cp %{SOURCE1} .

%build
# generate a helper script that will be used by help2man
cat >h2m_helper <<'EOF'
#!/bin/bash
[ "$1" == "--version" ] && echo "%{scl_name} %{version} Software Collection" || cat README
EOF
chmod a+x h2m_helper

# generate the man page
help2man -N --section 7 ./h2m_helper -o %{scl_name}.7

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}%{_scl_scripts}/root

# install generated man page
mkdir -p %{buildroot}%{_mandir}/man7/
install -m 644 %{scl_name}.7 %{buildroot}%{_mandir}/man7/%{scl_name}.7

%scl_install

# During the build of this package, we don't know which architecture it is 
# going to be used on, so if we build on 64-bit system and use it on 32-bit, 
# the %{_libdir} would stay expanded to '.../lib64'. This way we determine 
# architecture everytime the 'scl enable ...' is run and set the 
# LD_LIBRARY_PATH accordingly
cat >> %{buildroot}%{_scl_scripts}/enable << EOF
export PATH=%{_bindir}\${PATH:+:\${PATH}}
export LIBRARY_PATH=%{_libdir}\${LIBRARY_PATH:+:\${LIBRARY_PATH}}
export LD_LIBRARY_PATH=%{_libdir}\${LD_LIBRARY_PATH:+:\${LD_LIBRARY_PATH}}
export MANPATH=%{_mandir}:\${MANPATH}
EOF

# generate rpm macros file for depended collections
cat >> %{buildroot}%{_root_sysconfdir}/rpm/macros.%{scl_name_base}-scldevel << EOF
%%scl_%{scl_name_base} %{scl}
%%scl_prefix_%{scl_name_base} %{scl_prefix}
EOF

# generate a configuration file for daemon
cat >> %{buildroot}%{_scl_scripts}/service-environment << EOF
# Services are started in a fresh environment without any influence of user's
# environment (like environment variable values). As a consequence,
# information of all enabled collections will be lost during service start up.
# If user needs to run a service under any software collection enabled, this
# collection has to be written into POSTGRESQL92_SCLS_ENABLED
# variable in /opt/rh/sclname/service-environment.
POSTGRESQL92_SCLS_ENABLED="%{scl}"
EOF

%post runtime
# Simple copy of context from system root to DSC root.
# In case new version needs some additional rules or context definition,
# it needs to be solved.
# Unfortunately, semanage does not have -e option in RHEL-5, so we would
# have to have its own policy for collection (inspire in mysql55 package)
semanage fcontext -a -e / %{_scl_root} >/dev/null 2>&1 || :
semanage fcontext -a -e /etc/rc.d/init.d/postgresql /etc/rc.d/init.d/%{scl_prefix}postgresql >/dev/null 2>&1 || :
restorecon -R %{_scl_root} >/dev/null 2>&1 || :
restorecon /etc/rc.d/init.d/%{scl_prefix}postgresql >/dev/null 2>&1 || :
selinuxenabled && load_policy || :

%files

%files runtime -f filesystem
%doc README LICENSE
%scl_files
%config(noreplace) %{_scl_scripts}/service-environment
%{_mandir}/man7/%{scl_name}.*

%files build
%{_root_sysconfdir}/rpm/macros.%{scl}-config

%files scldevel
%{_root_sysconfdir}/rpm/macros.%{scl_name_base}-scldevel

%changelog
* Mon Mar 31 2014 Honza Horak <hhorak@redhat.com> - 1.1-20
- Fix path typo in README
  Related: #1061456

* Thu Mar 27 2014 Jozef Mlich <jmlich@redhat.com> - 1.1-19
- Resolves: #1079968 (Leftovers after uninstallation)

* Thu Feb 13 2014 Jozef Mlich <jmlich@redhat.com> - 1.1-18
- Resolves: #1058611 (postgresql92-build needs to depend
  on scl-utils-build)
- Add LICENSE, README and postgresql92.7 man page
  Resloves: #1061456 

* Wed Feb 12 2014 Honza Horak <hhorak@redhat.com> - 1.1-17
- Add -scldevel subpackage
  Resolves: #1063359

* Wed Dec 18 2013 Jozef Mlich <jmlich@redhat.com> 1-17
- release bump 
  Resolves #1038693

* Tue Nov 26 2013 Jozef Mlich <jmlich@redhat.com> 1-16
- By default, patch(1) creates backup files when chunks apply with offsets.
  Turn that off to ensure such files don't get included in RPMs.

* Fri Nov 22 2013 Honza Horak <hhorak@redhat.com> 1-15
- Rename variable to match postgresql package

* Mon Nov 18 2013 Jozef Mlich <jmlich@redhat.com> 1-14
- release bump

* Wed Oct  9 2013 Jozef Mlich <jmlich@redhat.com> 1-13
- release bump to scl 1.1

* Wed May 22 2013 Honza Horak <hhorak@redhat.com> 1-12
- Run semanage on whole root, BZ#956981 is fixed now
- Require semanage utility to be installed for -runtime package
- Fix MANPATH definition, colon in the end is correct (it means default)
  Resolves: BZ#966382

* Fri May  3 2013 Honza Horak <hhorak@redhat.com> 1-11
- Run semanage for all directories separately, since it has
  problems with definition for whole root

* Thu May  2 2013 Honza Horak <hhorak@redhat.com> 1-10
- Handle context of the init script
- Add better descriptions for packages

* Fri Apr 26 2013 Honza Horak <hhorak@redhat.com> 1-9
- fix escaping in PATH variable definition

* Mon Apr  8 2013 Honza Horak <hhorak@redhat.com> 1-8
- Don't require policycoreutils-python in RHEL-5 or older
- Require postgresql-server from the collection as main package
- Build separately on all arches
- Fix Environment variables definition

* Wed Feb 20 2013 Honza Horak <hhorak@redhat.com> 1-7
- Use %%setup macro to create safer build environment

* Fri Nov 09 2012 Honza Horak <hhorak@redhat.com> 1-6
- rename spec file to correspond with package name

* Thu Nov 08 2012 Honza Horak <hhorak@redhat.com> 1-5
- Mark service-environment as a config file

* Thu Oct 25 2012 Honza Horak <hhorak@redhat.com> 1-5
- create service-environment file to hold information about all collections,
  that should be enabled when service is starting
- added policycoreutils-python for semanage -e

* Thu Oct 18 2012 Honza Horak <hhorak@redhat.com> 1-3
- copy SELinux context from core mysql files

* Wed Oct 03 2012 Honza Horak <hhorak@redhat.com> 1-2
- update to postgresql-9.2 and rename to postgresql92

* Mon Mar 19 2012 Honza Horak <hhorak@redhat.com> 1-1
- initial packaging

