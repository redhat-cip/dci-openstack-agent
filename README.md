:warning: We are renaming the agent RPM. Please read [
the migration guide](README_migration_from_dci-ansible-agent.md).

# DCI OpenStack Agent

The "jumpbox" is the host where the agent is running. It can be a virtual
 machine.

## Requirements

- General:
  - A valid RHSM account.
  - A RHSM pool with the following channels:
    - rhel-7-server-rpms (jumpox|undercloud)
    - rhel-7-server-cert-rpms (undercloud)
    - rhel-7-server-extras-rpms (jumpox|undercloud)
    - rhel-7-server-optional-rpms (jumpbox)
    - rhel-7-server-rh-common-rpms (undercloud)
    - rhel-ha-for-rhel-7-server-rpms (undercloud)
  - Automation scripts for undercloud/overcloud deployment. The user must be
 able to automatically:
    - redeploy the undercloud machine from scratch
    - install the undercloud
    - deploy the overcloud on the node of the lab

- Jumpbox:
  - Run the latest RHEL 7 release.
  - Should be able to reach:
    - `https://api.distributed-ci.io` (443).
    - `https://packages.distributed-ci.io` (443).
    - `https://registry.distributed-ci.io` (443).
    - RedHat CDN.
    - EPEL repository.
    - The undercloud via `ssh` (22) for Ansible.
  - Have a static IPv4 address.
  - Have 160GB of the free space in `/var`.

- Undercloud/Overcloud:
  - Should be able to reach:
    - The jumpbox via `http` (80) for yum repositories.
    - The jumpbox via `http` (5000) for docker registry.
  - The Undercloud should be able to reach the floating-IP network. During
    its run, Tempest will try to reach the VM IP on this range. If you don't
    use the feature, the tests can be disabled.

## First steps

### Create your DCI account on distributed-ci.io

You need to create your user account in the system. Please connect to
 `https://www.distributed-ci.io` with your redhat.com SSO account. Your user
 account will be created in our database the first time you connect.

There is no reliable way to know your team automatically. So please contact us
 back when you reach this step, we will manually move your user in the correct
 organisation.

### Install the rpm

You be able to install the rpm of DCI Ansible Agent, you will need to activate
 some extra repositories.

If you are running RHEL7, you need to enable a couple of extra channels:

```console
# subscription-manager repos '--disable=*' --enable=rhel-7-server-rpms --enable=rhel-7-server-optional-rpms --enable=rhel-7-server-extras-rpms
```

You will also need the EPEL and DCI repositories:

```console
# yum install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
# yum install -y https://packages.distributed-ci.io/dci-release.el7.noarch.rpm
```

You can now install the `dci-openstack-agent` package:

```console
# yum install -y dci-openstack-agent
```

### Configure your time source

Having an chronized clock is important to get meaningful log files. This is
the reason why the agent ensure Chrony is running.You can valide the server
is synchronized with the following command:

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

### Create the `remoteci`

What DCI calls the `remoteci` is your platform and its jumpbox. It has a
 name and a secret key that will be used to authenticate itself.

Only the admins of the team can create the remoteci [on our interface](http://www.distributed-ci.io).

To do so, they have to:

1. Click on the `Remote CIs` entry from the left menu
2. Use the `Create new remoteci` to add the `remoteci`

Once the `remoteci` is ready, you can download its authentication file on the
 `Download rc file` column. The file is called `remotecirc.sh`, please rename it
 to `dcirc.sh` for the next step.

### Use the dcirc.sh to authenticate the lab

You start using the DCI Ansible Agent, you need to copy the `dcirc.sh` file here
`/etc/dci-openstack-agent/dcirc.sh`.

### HTTP Proxy

If you need to go through a HTTP proxy, you will need to set the
`http_proxy` environment variables.
Edit the `/etc/dci-openstack-agent/dcirc.sh` file and add the following lines:

```console
http_proxy="http://somewhere:3128/"
https_proxy="http://somewhere:3128/"
no_proxy="localhost,127.0.0.1,<jumpbox ip>"
export http_proxy
export https_proxy
export no_proxy
```
And replace <jumpbox ip> by the ip address of the jumpbox. This should be the
same value than the dci_base_ip variable used in the settings.yml file if customized (default
to ansible_default_ipv4.address fact in group_vars/all).

You will need to configure yum, so it will make use of the HTTP
proxy. For instance, add `proxy=http://somewhere:3128` in the `[main]`
section of `/etc/yum.conf`.

Finally, RHSM also needs to be able to go through the proxy. Edit `/etc/rhsm/rhsm.conf`:

```console
proxy_hostname = somewhere
proxy_port = 3128
proxy_user =
proxy_password =
```
### Test the connection between the remoteci and the DCI API server

At this point, you can validate your `dcirc.sh` with the following commands:

```console
# source /etc/dci-openstack-agent/dcirc.sh
# dcictl remoteci-list
```

You should get an output similar to this one:

```console
+--------------------------------------|-----------|--------|---------|-------|--------------+
|                  id                  |    name   | state  | country | email | notification |
+--------------------------------------|-----------|--------|---------|-------|--------------+
| a2780b4c-0cdc-4a4a-a9ed-44930562ecce | RACKSPACE | active |   None  |  None |     None     |
+--------------------------------------|-----------|--------|---------|-------|--------------+
```

If you get an error with the call above, you can validate the API server is
reachable with the following `curl` call:

```console
$ curl https://api.distributed-ci.io/api/v1
{"_status": "OK", "message": "Distributed CI."}
```

### Integration with the lab deployment scripts

The agent has two different location where you can adjust its configuration:

- `settings.yml`: The place where you can do the generic configuration.
  This file will override any variables defined in group_vars/all. You
  can take a look on the [sample file](https://github.com/redhat-cip/dci-openstack-agent/blob/master/samples/settings.yml)
- `hooks/*.yml`: Each file from this directory is a list of Ansible tasks.
  This is the place where the users can launch their deployment scripts.

First, you must edit `/etc/dci-openstack-agent/settings.yml`. You probably just have to
add the `undercloud_ip` key if you're using a static ip address. It should point to your
undercloud IP. Otherwise you could add the undercloud to the dynamic ansible inventory
during the playbook execution via the [add_host module](https://docs.ansible.com/ansible/latest/modules/add_host_module.html)

You need to adjust the following Ansible playbook to describe how you want to
 provision your OpenStack. These playbook are located in the `/etc/dci-openstack-agent/hooks`.

**pre-run.yml**: It will be called during the provisioning. This is the place
 where you describe the steps to follow to prepare your platform:
    * deployment of the `undercloud` machine
    * configuration of a network device
    * etc
This hook runs on the `localhost`.

**running.yml**: this playbook will trigger to deploy the undercloud and the
 overcloud. It should also add <http://$jumpbox_ip/dci_repo/dci_repo.repo> to the
 repository list (`/etc/yum/yum.repo.d/dci_repo.repo`).

At the end of this hook run, the Overcloud should be running.
If your undercloud has a dynamic IP, you must use a set_fact action
to set the undercloud_ip variable. The agent needs to
know its IP to run the tests.

This hook runs on the `localhost`.

**teardown.yml**: This playbook cleans the full platform.
This hook can either be called  from the `jumpbox` or the `undercloud`. If you
need to run an action on a specific host, you should use the `delegate_to` key
to be sure the task will be run on the correct machine.

### Start the service

The agent comes with a systemd configuration that simplifies its execution. You can just start the agent:

```console
# systemctl start dci-openstack-agent
```

Use journalctl to follow the agent execution:

```console
# journalctl -ef -u dci-openstack-agent
```

If you need to connect as the dci-openstack-agent user, you can do:

```console
# su - dci-openstack-agent -s /bin/bash
```

This is, for example, necessary if you want to create a ssh key:

```console
$ ssh-keygen
```

### Use the timer

The `dci-openstack-agent` rpm provides a systemd timer called `dci-openstack-agent.timer` will call automatically several times a day.

To enable them, just run:

```console
# systemctl enable dci-openstack-agent.timer
# systemctl start dci-openstack-agent.timer
```

### Keep your system up to date

Distributed-CI is a rolling release. We publish updates every with and we expect
our users to keep their jumpbox up to date.

```console
# yum install -y yum-cron
# systemctl enable yum-cron
# systemctl start yum-cron
```

