# Migration from DCI Ansible Agent

The DCI OpenStack Agent used to be named `dci-ansible-agent`. The name was
confusing we we decided to rename it `dci-openstack-agent`. To transition to
the new package you have to follow a couple of manual steps.

First, you must disable the `dci-ansible-agent`:

    # systemctl stop dci-ansible-agent.timer
    # systemctl stop dci-ansible-agent

Now you can rename the configuration files:

    # cp -R /etc/dci-ansible-agent /etc/dci-openstack-agent
    # cp -Rv /var/lib/dci-ansible-agent/ssh /var/lib/dci-openstack-agent/ssh
    # cp -Rv /var/lib/dci-ansible-agent/*.tar /var/lib/dci-openstack-agent/
    # restorecon /var/lib/dci-openstack-agent/
    # chown -R dci-openstack-agent:dci-openstack-agent /var/lib/dci-openstack-agent/

Finally you can restart the agent:

    # systemctl start dci-openstack-agent.timer
    # systemctl start dci-openstack-agent

Do not try to manually remove the `dci-openstack-agent` rpm. It will be
automatically remove by an update in the future.
