Name:           dci-ansible-agent
Version:        0.0.VERS
Release:        1%{?dist}
Summary:        DCI Ansible Agent for DCI control server
License:        ASL 2.0
URL:            https://github.com/redhat-openstack/dci-openstack-agent
BuildArch:      noarch
Source0:        dci-openstack-agent-%{version}.tar.gz

BuildRequires:  dci-ansible
BuildRequires:  ansible
BuildRequires:  systemd
BuildRequires:  systemd-units
BuildRequires:  git
Requires:       dci-ansible
Requires:       ansible
Requires:       python-netaddr
Requires:       ansible-role-openstack-certification
Requires:       sudo

Requires(pre): shadow-utils
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd

%description
DCI Ansible Agent for DCI control server.

%prep
%setup -qc

%build

%install
# dci-ansible-agent (legacy)
install -p -D -m 644 systemd/%{name}.service %{buildroot}%{_unitdir}/dci-ansible-agent.service
install -p -D -m 644 systemd/%{name}.timer %{buildroot}%{_unitdir}/dci-ansible-agent.timer
install -p -D -m 644 systemd/dci-update.service %{buildroot}%{_unitdir}/dci-update.service
install -p -D -m 644 systemd/dci-update.timer %{buildroot}%{_unitdir}/dci-update.timer
install -p -D -m 644 ansible.cfg %{buildroot}%{_datadir}/dci-ansible-agent/ansible.cfg
cp -r files %{buildroot}/%{_datadir}/dci-ansible-agent
cp -r roles %{buildroot}/%{_datadir}/dci-ansible-agent
cp -r plays %{buildroot}/%{_datadir}/dci-ansible-agent
cp -r templates %{buildroot}/%{_datadir}/dci-ansible-agent
install -p -D -m 644 dci-ansible-agent.yml %{buildroot}%{_datadir}/dci-ansible-agent/dci-ansible-agent.yml
install -p -D -m 644 dcirc.sh %{buildroot}%{_sysconfdir}/dci-ansible-agent/dcirc.sh
install -p -D -m 644 hooks/pre-run.yml %{buildroot}%{_sysconfdir}/dci-ansible-agent/hooks/pre-run.yml
install -p -D -m 644 hooks/running.yml %{buildroot}%{_sysconfdir}/dci-ansible-agent/hooks/running.yml
install -p -D -m 644 hooks/teardown.yml %{buildroot}%{_sysconfdir}/dci-ansible-agent/hooks/teardown.yml
install -p -D -m 644 hooks/success.yml %{buildroot}%{_sysconfdir}/dci-ansible-agent/hooks/success.yml
install -p -D -m 644 hooks/local_tests.yml %{buildroot}%{_sysconfdir}/dci-ansible-agent/hooks/local_tests.yml
install -p -D -m 644 settings.yml %{buildroot}%{_sysconfdir}/dci-ansible-agent/settings.yml
install -p -D -m 440 dci-ansible-agent.sudo %{buildroot}%{_sysconfdir}/sudoers.d/dci-ansible-agent
install -p -d -m 755 %{buildroot}/%{_sharedstatedir}/dci-ansible-agent
install -p -D -m 644 fetch_images.py %{buildroot}%{_datadir}/dci-ansible-agent/fetch_images.py

# dci-openstack-agent
install -p -D -m 644 systemd/%{name}.service %{buildroot}%{_unitdir}/dci-openstack-agent.service
install -p -D -m 644 systemd/%{name}.timer %{buildroot}%{_unitdir}/dci-openstack-agent.timer
install -p -D -m 644 systemd/dci-update.service %{buildroot}%{_unitdir}/dci-update.service
install -p -D -m 644 systemd/dci-update.timer %{buildroot}%{_unitdir}/dci-update.timer
install -p -D -m 644 ansible.cfg %{buildroot}%{_datadir}/dci-openstack-agent/ansible.cfg
cp -r files %{buildroot}/%{_datadir}/dci-openstack-agent
cp -r roles %{buildroot}/%{_datadir}/dci-openstack-agent
cp -r plays %{buildroot}/%{_datadir}/dci-openstack-agent
cp -r templates %{buildroot}/%{_datadir}/dci-openstack-agent
install -p -D -m 644 dci-ansible-agent.yml %{buildroot}%{_datadir}/dci-openstack-agent/dci-openstack-agent.yml
# For now we do a symlink from /etc/dci-openstack-agent to /etc/dci-ansible-agent (see the %post)
#install -p -D -m 644 dcirc.sh %{buildroot}%{_sysconfdir}/dci-openstack-agent/dcirc.sh
#install -p -D -m 644 hooks/pre-run.yml %{buildroot}%{_sysconfdir}/dci-openstack-agent/hooks/pre-run.yml
#install -p -D -m 644 hooks/running.yml %{buildroot}%{_sysconfdir}/dci-openstack-agent/hooks/running.yml
#install -p -D -m 644 hooks/teardown.yml %{buildroot}%{_sysconfdir}/dci-openstack-agent/hooks/teardown.yml
#install -p -D -m 644 hooks/success.yml %{buildroot}%{_sysconfdir}/dci-openstack-agent/hooks/success.yml
#install -p -D -m 644 hooks/local_tests.yml %{buildroot}%{_sysconfdir}/dci-openstack-agent/hooks/local_tests.yml
#install -p -D -m 644 settings.yml %{buildroot}%{_sysconfdir}/dci-openstack-agent/settings.yml
install -p -D -m 440 dci-ansible-agent.sudo %{buildroot}%{_sysconfdir}/sudoers.d/dci-openstack-agent
install -p -d -m 755 %{buildroot}/%{_sharedstatedir}/dci-openstack-agent
install -p -D -m 644 fetch_images.py %{buildroot}%{_datadir}/dci-openstack-agent/fetch_images.py


%clean

%pre
# Legacy
getent group %{name} >/dev/null || groupadd -r %{name}
getent passwd %{name} >/dev/null || \
    useradd -r -m -g %{name} -d %{_sharedstatedir}/%{name} -s /bin/bash \
            -c "DCI-Agent service" %{name}
# New
getent group dci-openstack-agent >/dev/null || groupadd -r dci-openstack-agent
getent passwd dci-openstack-agent >/dev/null || \
    useradd -r -m -g dci-openstack-agent -d %{_sharedstatedir}/dci-openstack-agent -s /bin/bash \
            -c "DCI-OpenStack-Agent service" dci-openstack-agent

exit 0

%post
%systemd_post dci-update.service
%systemd_post dci-update.timer
# Legacy
%systemd_post %{name}.service
%systemd_post %{name}.timer
# New
%systemd_post dci-openstack-agent.service
%systemd_post dci-openstack-agent.timer
test -d /etc/dci-openstack-agent || ln -s -f /etc/dci-ansible-agent /etc/dci-openstack-agent

%preun
%systemd_preun dci-update.service
%systemd_preun dci-update.timer
# Legacy
%systemd_preun %{name}.service
%systemd_preun %{name}.timer
# New
%systemd_preun dci-openstack-agent.service
%systemd_preun dci-openstack-agent.timer

%postun
%systemd_postun

%files
%{_unitdir}/*
# Legacy
%{_datadir}/dci-ansible-agent
%config(noreplace) %{_sysconfdir}/dci-ansible-agent/dcirc.sh
%config(noreplace) %{_sysconfdir}/dci-ansible-agent/settings.yml
%config(noreplace) %{_sysconfdir}/dci-ansible-agent/hooks/pre-run.yml
%config(noreplace) %{_sysconfdir}/dci-ansible-agent/hooks/running.yml
%config(noreplace) %{_sysconfdir}/dci-ansible-agent/hooks/success.yml
%config(noreplace) %{_sysconfdir}/dci-ansible-agent/hooks/local_tests.yml
%config(noreplace) %{_sysconfdir}/dci-ansible-agent/hooks/teardown.yml
%dir %{_sharedstatedir}/dci-ansible-agent
%attr(0755, %{name}, %{name}) %{_sharedstatedir}/dci-ansible-agent
/etc/sudoers.d/dci-ansible-agent
# New dci-openstack-agent
%{_datadir}/dci-openstack-agent
%dir %{_sharedstatedir}/dci-openstack-agent
%attr(0755, %{name}, %{name}) %{_sharedstatedir}/dci-openstack-agent
/etc/sudoers.d/dci-openstack-agent


%changelog
* Tue Mar 28 2017 Gonéri Le Bouder <goneri@redhat.com> - 0.0.0-1
- Initial release
