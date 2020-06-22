Name:           dci-openstack-agent
Version:        0.0.VERS
Release:        2%{?dist}
Summary:        DCI OpenStack Agent for DCI control server
License:        ASL 2.0
URL:            https://github.com/redhat-cip/dci-openstack-agent
BuildArch:      noarch
Source0:        dci-openstack-agent-%{version}.tar.gz

%if 0%{?rhel} && 0%{?rhel} < 8
%global with_python2 1
%else
%global with_python3 1
%endif


BuildRequires:  dci-ansible
BuildRequires:  ansible
BuildRequires:  systemd
BuildRequires:  systemd-units
BuildRequires:  git
BuildRequires:  /usr/bin/pathfix.py
%if 0%{?with_python3}
BuildRequires:  python3-devel
%else
BuildRequires:  python2-devel
%endif
Requires:       dci-ansible
Requires:       ansible
Requires:       python-netaddr
Requires:       ansible-role-dci-import-keys
Requires:       ansible-role-dci-retrieve-component >= 0.1.1
Requires:       ansible-role-dci-sync-registry
Requires:       ansible-role-openstack-certification
Requires:       sudo
Requires:       python-docker-py
Conflicts:      python-docker > 2.0
Conflicts:      dci-ansible-agent <= 0.0.201811291905git108553f3-1
Obsoletes:      dci-ansible-agent <= 0.0.201811291905git108553f3-1

Requires(pre):    shadow-utils
Requires(post):   systemd
Requires(preun):  systemd
Requires(postun): systemd

%description
DCI OpenStack Agent for DCI control server.

%prep
%setup -qc
%if 0%{?with_python3}
pathfix.py -i "%{__python3} %{py3_shbang_opts}" -pn roles/
%else
pathfix.py -i "%{__python2} %{py2_shbang_opts}" -pn roles/
%endif

%build

%install
install -p -D -m 644 systemd/dci-openstack-agent.service %{buildroot}%{_unitdir}/dci-openstack-agent.service
install -p -D -m 644 systemd/dci-openstack-agent.timer %{buildroot}%{_unitdir}/dci-openstack-agent.timer
install -p -D -m 644 systemd/dci-openstack-agent-setup.service %{buildroot}%{_unitdir}/dci-openstack-agent-setup.service
install -p -D -m 644 ansible.cfg %{buildroot}%{_datadir}/dci-openstack-agent/ansible.cfg
cp -r files %{buildroot}/%{_datadir}/dci-openstack-agent
cp -r roles %{buildroot}/%{_datadir}/dci-openstack-agent
cp -r plays %{buildroot}/%{_datadir}/dci-openstack-agent
cp -r group_vars %{buildroot}/%{_datadir}/dci-openstack-agent
install -p -D -m 644 dci-openstack-agent.yml %{buildroot}%{_datadir}/dci-openstack-agent/dci-openstack-agent.yml
install -p -D -m 644 dcirc.sh %{buildroot}%{_sysconfdir}/dci-openstack-agent/dcirc.sh
install -p -D -m 644 hooks/pre-run.yml %{buildroot}%{_sysconfdir}/dci-openstack-agent/hooks/pre-run.yml
install -p -D -m 644 hooks/running.yml %{buildroot}%{_sysconfdir}/dci-openstack-agent/hooks/running.yml
install -p -D -m 644 hooks/teardown.yml %{buildroot}%{_sysconfdir}/dci-openstack-agent/hooks/teardown.yml
install -p -D -m 644 hooks/success.yml %{buildroot}%{_sysconfdir}/dci-openstack-agent/hooks/success.yml
install -p -D -m 644 hooks/local_tests.yml %{buildroot}%{_sysconfdir}/dci-openstack-agent/hooks/local_tests.yml
install -p -D -m 644 hooks/failure.yml %{buildroot}%{_sysconfdir}/dci-openstack-agent/hooks/failure.yml
install -p -D -m 644 settings.yml %{buildroot}%{_sysconfdir}/dci-openstack-agent/settings.yml
install -p -D -m 440 dci-openstack-agent.sudo %{buildroot}%{_sysconfdir}/sudoers.d/dci-openstack-agent
install -p -d -m 755 %{buildroot}/%{_sharedstatedir}/dci-openstack-agent


%clean

%pre
getent group dci-openstack-agent >/dev/null || groupadd -r dci-openstack-agent
getent passwd dci-openstack-agent >/dev/null || \
    useradd -r -m -g dci-openstack-agent -d %{_sharedstatedir}/dci-openstack-agent -s /bin/bash \
            -c "DCI-OpenStack-Agent service" dci-openstack-agent
exit 0

%post
%systemd_post dci-openstack-agent.service
%systemd_post dci-openstack-agent.timer
%systemd_post dci-openstack-agent-setup.service

%preun
%systemd_preun dci-openstack-agent.service
%systemd_preun dci-openstack-agent.timer
%systemd_preun dci-openstack-agent-setup.service

%postun
%systemd_postun

%files
%doc LICENSE README.md
%{_unitdir}/dci-openstack-agent.service
%{_unitdir}/dci-openstack-agent.timer
%{_unitdir}/dci-openstack-agent-setup.service
%{_datadir}/dci-openstack-agent
%config(noreplace) %{_sysconfdir}/dci-openstack-agent/dcirc.sh
%config(noreplace) %{_sysconfdir}/dci-openstack-agent/settings.yml
%config(noreplace) %{_sysconfdir}/dci-openstack-agent/hooks/pre-run.yml
%config(noreplace) %{_sysconfdir}/dci-openstack-agent/hooks/running.yml
%config(noreplace) %{_sysconfdir}/dci-openstack-agent/hooks/success.yml
%config(noreplace) %{_sysconfdir}/dci-openstack-agent/hooks/local_tests.yml
%config(noreplace) %{_sysconfdir}/dci-openstack-agent/hooks/teardown.yml
%config(noreplace) %{_sysconfdir}/dci-openstack-agent/hooks/failure.yml
%dir %{_sharedstatedir}/dci-openstack-agent
%attr(0755, dci-openstack-agent, dci-openstack-agent) %{_sharedstatedir}/dci-openstack-agent
/etc/sudoers.d/dci-openstack-agent


%changelog
* Mon Jun 22 2020 François Charlier <francois.charlier@redhat.com> - 0.0.0-3
- Fix python shebang for el8

* Fri Jan 17 2020 François Charlier <francois.charlier@redhat.com> - 0.0.0-2
- Added the "failure.yml" hook

* Tue Mar 28 2017 Gonéri Le Bouder <goneri@redhat.com> - 0.0.0-1
- Initial release
