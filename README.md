# DCI OpenStack Agent

## Overview

The following documentation will allow you to configure your OpenStack automated jobs with DCI.
At the end of this documentation, you should have a configured systemd service running DCI jobs with the latest versions of RHOSP or RDO.
dci-openstack-agent is an ansible-playbook executed as a systemd service. 
This service will run on a RHEL server called remoteci.
It will run Red Hat tests at the end of the process to ensure everything is working fine.

This documentation is divided into 4 parts.

- Requirements
- Integrate your automation with DCI
- Test your integation and run your first job
- Automate job's run

## Requirements

### OpenStack Automation

To be able to work with DCI you **must have** automation scripts for undercloud and overcloud deployments.
You should be able to automatically:

- clean and redeploy the undercloud machine automatically
- install the undercloud using repository and registry urls as parameters
- deploy the overcloud on the node of the lab

### Red Hat SSO

DCI is connected to the Red Hat SSO. You will need a [Red Hat account](https://access.redhat.com/).

### RHSM account

On each remoteci where the agents will run, you need a valid RHSM account.
You can type `subscription-manager identity` on your remoteci to see if it's the case.
You should also have access to the following channel with your RHSM account:

- rhel-7-server-optional-rpms (remoteci)
- rhel-7-server-rpms (remoteci|undercloud)
- rhel-7-server-extras-rpms (remoteci|undercloud)
- rhel-7-server-cert-rpms (undercloud)
- rhel-7-server-rh-common-rpms (undercloud)
- rhel-ha-for-rhel-7-server-rpms (undercloud)

### Remoteci

You should check that your remoteci:

- Is running the latest RHEL 7 release.
- Has a static IPv4 address.
- Has 160GB of free space in `/var` (components will be in /var/www/html and container images in /var/lib/docker).
- Should be able to reach:
  - `https://api.distributed-ci.io` (443).
  - `https://packages.distributed-ci.io` (443).
  - `https://registry.distributed-ci.io` (443).
  - RedHat CDN.
  - EPEL repository.
  - The undercloud via `ssh` (22) for Ansible.

## Integrate your automation with DCI

### Install dci-openstack-agent

To be able to install the rpm of DCI Ansible Agent, you will need to activate some extra repositories and add EPEL and DCI repositories.

```console
$ subscription-manager repos '--disable=*' --enable=rhel-7-server-rpms --enable=rhel-7-server-optional-rpms --enable=rhel-7-server-extras-rpms
$ yum install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
$ yum install -y https://packages.distributed-ci.io/dci-release.el7.noarch.rpm
```

You can now install the `dci-openstack-agent` package:

```console
$ yum install -y dci-openstack-agent
```

### Remoteci creation

DCI is connected to the Red Hat SSO. You need to log in `https://www.distributed-ci.io` with your redhat.com SSO account.
Your user account will be created in our database the first time you connect.

After the first connection you have to create a remoteci. Go to [https://www.distributed-ci.io/remotecis](https://www.distributed-ci.io/remotecis) and click `Create a new remoteci` button. Once your `remoteci` is created, you can retrieve the connection information in the 'Authentication' column. Edit the `/etc/dci-openstack-agent/dcirc.sh` file with the information displayed.

At this point, you can validate your credentials with the following commands:

```console
$ source /etc/dci-openstack-agent/dcirc.sh
$ dcictl remoteci-list
```

If you see your remoteci in the list, everything is working great so far.

### DCI hooks

Here is the structure of the configuration files for dci-openstack-agent

```console
/etc/dci-openstack-agent/
...
├── hooks
│   ...
│   ├── pre-run.yml
│   ├── running.yml
│   ...
└── settings.yml
```

DCI hooks are ansible tasks that will be run by the agent. You need to call your clean and provisioning script in the pre-run.yml task.

```
# /etc/dci-openstack-agent/hooks/pre-run.yml
---
- name: clean
  shell: ansible-playbook clean.yml
  args:
    chdir: /var/lib/dci-openstack-agent
- name: provision
  shell: ansible-playbook provision.yml
  args:
    chdir: /var/lib/dci-openstack-agent
```


dci-openstack-agent will start a job by downloading the lastest component based on the topic version set in `/etc/dci-openstack-agent/settings.yml`

```console
$ cat /etc/dci-openstack-agent/settings.yml
dci_topic: OSP16
```

Then the dci-openstack-agent will create a local repository (`http://<dci_mirror_location>/dci_repo/dci_repo.repo`) with the rpm downloaded and will create a local registry (`<dci_mirror_location>:5000`) for containers.


`running.yml` hooks should install undercloud and overcloud using local repository and registry.

```
# /etc/dci-openstack-agent/hooks/running.yml
---
- name: install undercloud
  shell: 'ansible-playbook -e repo="{{ dci_mirror_location }}/dci_repo/dci_repo.repo" install_undercloud.yml'
  args:
    chdir: /var/lib/dci-openstack-agent
- name: install overcloud
  shell: 'ansible-playbook -e registry="{{ dci_mirror_location }}" -e registry_port="5000" install_overcloud.yml'
  args:
    chdir: /var/lib/dci-openstack-agent
```

At the end of the running tasks, you **must** set the undercloud_ip variable using [set_fact module](https://docs.ansible.com/ansible/latest/modules/set_fact_module.html).

```
- name: Set undercloud_ip fact
  set_fact:
    undercloud_ip: "{{ undercloud_ip }}"
```

If your undercloud ip is fixed, just add `undercloud_ip: ....` in `/etc/dci-openstack-agent/settings.yml`

### Topic access

Before testing the integration, we need to check that you have access to the topic (version of OpenStack) present in `/etc/dci-openstack-agent/settings.yml`

```console
$ cat /etc/dci-openstack-agent/settings.yml
dci_topic: OSP16
```

Check with dcictl if you have access to this topic

```console
$ dcictl topic-list --where 'name:OSP16'
```

If you don't have access to this topic then **you should contact your EPM at Red Hat** which will give you access to the topic you need.


## Test your integation and run your first job

Now that everything is configured, we will run the dci-openstask-agent playbook to see if everything is fine

```console
$ su - dci-openstack-agent -s /bin/bash
$ cd /usr/share/dci-openstack-agent
$ source /etc/dci-openstack-agent/dcirc.sh
$ /usr/bin/ansible-playbook -vv /usr/share/dci-openstack-agent/dci-openstack-agent.yml -e @/etc/dci-openstack-agent/settings.yml
```

### Integration notes

When you are on the undercloud machine or the overcloud ones, you should be able to reach the remoteci via `http` port 80 and 5000.
The undercloud should be able to reach the floating-IP network. During its run, Tempest will try to reach the VM IP on this range. If you don't use it disable the tests (see advanced documentation)


## Automate job run

You are here? Good news, you have now a working automated agent running on your remoteci. Next step is to configure your jobs to be performed on a recurring schedule.

### Configure your time source

Having a synchronized clock is important to get meaningful log files. This is the reason why the agent ensures Chrony is running.
You can valide the server is synchronized with the following command:

```console
$ chronyc activity
200 OK
6 sources online
0 sources offline
0 sources doing burst (return to online)
0 sources doing burst (return to offline)
0 sources with unknown address
```

If Chrony is not running, you can follow [the official documentation](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/7/html/system_administrators_guide/sect-using_chrony) to set it up.


### Set tags

Edit your settings to set the tags for your jobs

```console
$ cat /etc/dci-openstack-agent/settings.yml
dci_topic: OSP16
dci_tags: []
# dci_tags: ['lab1', 'osp16', 'driver abc']
```

or directly in your job's hooks:

```
- name: Tag job with configuration used
  dci_job:
    id: "{{ job_id }}"
    tags:
      - "{{ configuration }}"
```

### Start the service

The agent comes with a systemd configuration that simplifies its execution. You can just start the agent:

```console
$ systemctl start dci-openstack-agent
```

You can use journalctl to follow the agent execution:

```console
$ journalctl -ef -u dci-openstack-agent
```

For debugging purposes if you need to connect as the dci-openstack-agent user, you can do:

```console
$ sudo su - dci-openstack-agent -s /bin/bash
```

### Keep your system up to date

Distributed-CI is a rolling release. 
When the agent is started with the dci-openstack-agent systemd unit or timer, the DCI related packages are upgraded before executing the Ansible playbook.

If you don't start the agent with the dci-openstack-agent systemd unit or timer, please make sure to check for DCI packages upgrades before running the Ansible playbook.

You can for example keep your system up-to-date with the following setup:

```console
$ yum install -y yum-cron
$ systemctl enable yum-cron
$ systemctl start yum-cron
$ sed -i 's,apply_updates = .*,apply_updates = yes,' /etc/yum/yum-cron.conf
```

