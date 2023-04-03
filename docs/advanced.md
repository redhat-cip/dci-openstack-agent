# DCI OpenStack Agent Advanced


## How to set HTTP Proxy for my dci-openstack-agent

If you need to go through a HTTP proxy, you will need to set the `http_proxy` environment variables.
Edit the `/etc/dci-openstack-agent/dcirc.sh` file and add the following lines:

```console
http_proxy="http://somewhere:3128/"
https_proxy="http://somewhere:3128/"
no_proxy="localhost,127.0.0.1,<remoteci_ip>"
export http_proxy
export https_proxy
export no_proxy
```

And replace <remoteci_ip> by the ip address of the remoteci. This should be the
same value as the dci_base_ip variable used in the settings.yml file if customized (default
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

## How to deal with multiple OpenStack releases

When testing multiple OpenStack releases you probably have different steps
(configuration, tasks, packages, etc...) according to the release. As an example
 you could:

- have scripts per OpenStack versions and file path based on the dci_topic
 variable (ie OSP10, OSP11, etc..):

```yaml
- shell: |
    /automation_path/{{ dci_topic }}/undercloud_installation.sh
```

- have git branch per OpenStack versions based on the dci_topic variable :

```yaml
- git:
    repo: https://repo_url/path/to/automation.git
    dest: /automation_path
    version: '{{ dci_topic }}'

- shell: /automation_path/undercloud_installation.sh
```

- use ansible condition and jinja template with the dci_topic variable :

```yaml
- shell: |
    /automation_path/build_container.sh
  when: dci_topic in ['OSP12', 'OSP13']

- shell: >
    source /home/stack/stackrc &&
    openstack overcloud deploy --templates
    {% if dci_topic in ['OSP12', 'OSP13'] %}
    -e /usr/share/openstack-tripleo-heat-templates/environments/docker.yaml
    -e /usr/share/openstack-tripleo-heat-templates/environments/docker-ha.yaml
    {% endif %}
    -e /usr/share/openstack-tripleo-heat-templates/environments/disable-telemetry.yaml
```

## How to retrieve the OpenStack yum repository

During the 'new' hook, the remoteci will create a yum repository with the latest bits
 available. This repository is located in the `/var/www/html/dci_repo` directory
 and accessible via HTTP at `http://$remoteci_ip/dci_repo/dci_repo.repo`.

There's several ways to retrieve the yum repository from the undercloud:

- Using the yum-config-manager command:

```yaml
- shell: |
    yum-config-manager --add-repo {{ dci_baseurl }}/dci_repo/dci_repo.repo
  become: true
```

- Using the http url:

```yaml
- get_url:
    url: '{{ dci_baseurl }}/dci_repo/dci_repo.repo'
    dest: /etc/yum.repos.d/dci_repo.repo
  become: true
```

- Using the ansible copy module:

```yaml
- copy:
    src: /var/www/html/dci_repo/dci_repo.repo
    dest: /etc/yum.repos.d/dci_repo.repo
  become: true
```

## How to test a specific repository for an OpenStack release

The agent's default behaviour is to fetch and test the latest available
component (repository + container images) for the configured topic.

To fetch and test another component, you must define the `dci_components`
ansible parameter when executing the agent.

This can be done either:

- in the configuration file (default: `/etc/dci-openstack-agent/settings.yml`) by adding:

```yaml:
- dci_components:
    - <component_id>
```

- or on the command-line by adding `-e dci_components=<component_id>`:

```console:
$ ansible-playbook -vv download_only.yml -e @/etc/dci-openstack-agent/settings.yml -e dci_components=<component_id>
```

The `component_id` is available:

- in the web GUI in "Components" by clicking on the notepad icon on the left of the component name ;

- using the `dcictl` cli, for OSP13 for example:

```console:
$ source /etc/dci-openstack-agent/dcirc.sh
$ TOPIC=$(dcictl topic-list | awk '/OSP13/ { print $2 }')
$ dcictl component-list --topic-id=${TOPIC}
+--------------------------------------+----------------------------+--------+---------------+…
|                  id                  |            name            | state  | display_name  |…
+--------------------------------------+----------------------------+--------+---------------+…
| 8d0885d6-8cde-433c-9053-c6aca7845920 | RH7-RHOS-13.0 2019-03-18.1 | active | RH7-RHOS-13.0 |…
| bb2de6d2-89e9-4294-bdd6-f656bea2d566 | RH7-RHOS-13.0 2019-03-08.1 | active | RH7-RHOS-13.0 |…
| 18cb361e-49b6-49eb-9150-d207250a003d | RH7-RHOS-13.0 2019-03-04.2 | active | RH7-RHOS-13.0 |…
| 1d1e0dcc-9ec5-4308-aad0-b4c8d4cbfa8d | RH7-RHOS-13.0 2019-03-01.1 | active | RH7-RHOS-13.0 |…
| 0c7e51ec-2492-4570-983e-7d620f96499f | RH7-RHOS-13.0 2019-01-22.1 | active | RH7-RHOS-13.0 |…
| 16b9f539-d3c2-42d1-bd63-d32ddbcef76b | RH7-RHOS-13.0 2019-01-21.1 | active | RH7-RHOS-13.0 |…
| d2eb5f90-807a-42f5-aae5-e0bbf0e1edba | RH7-RHOS-13.0 2019-01-10.1 | active | RH7-RHOS-13.0 |…
| 37b814ed-3423-4371-84bf-a0566ee8cfc9 | RH7-RHOS-13.0 2019-01-03.2 | active | RH7-RHOS-13.0 |…
| 487fc160-d1bc-4a43-819b-979fd8655164 | RH7-RHOS-13.0 2018-12-13.4 | active | RH7-RHOS-13.0 |…
+--------------------------------------+----------------------------+--------+---------------+…
```

## How to fetch and use the images

If you are using OSP12 and above, the DCI agent will set up an image registry and
 fetch the last OSP images on your remoteci.

Before you start the overcloud deploy with the `openstack overcloud deploy
 --templates [additional parameters]` command, you have to call the following
 command on the undercloud node:

```console
$ openstack overcloud container image prepare --namespace ${remoteci_ip}:5000/rhosp12 --output-env-file ~/docker_registry.yaml
```

:information_source: `${remoteci_ip}` is the IP address of the remoteci machine and
 in this example we assume you use OSP12.

You don't have to do any additional `openstack overcloud container` call unless
 you want to rebuild or patch an image.

The Overcloud deployment is standard, you just have to include the two following
 extra Heat template:

- `/usr/share/openstack-tripleo-heat-templates/environments/docker.yaml`
- `~/docker_registry.yaml`

See the upstream documentation if you need more details: [Deploying the containerized Overcloud](https://docs.openstack.org/tripleo-docs/latest/install/containers_deployment/overcloud.html#deploying-the-containerized-overcloud)

Starting with OSP14 (Rocky), the undercloud is now also containerized. That means
that you also need to generate the container image list before the undercloud
installation.

```console
$ openstack overcloud container image prepare --namespace ${remoteci_ip}:5000/rhosp14
                                              --roles-file /usr/share/openstack-tripleo-heat-templates/roles_data_undercloud.yaml
                                              --output-env-file ~/docker_registry.yaml

```

Finally specify the generated file path in the undercloud configuration and add
the remoteci ip in the list of the docker insecure registries:

```console
$ vim undercloud.conf
```

```ini
[DEFAULT]
container_images_file = /home/stack/docker_registry.yaml
docker_insecure_registries = ${remoteci_ip}:5000
```

## How to skip downloading some container images

Each Openstack release comes with +100 container images.
In most of the cases you don't need all the images to do the deployment because
 some are specific to extra services (barbican, manila, sahara, etc...)
If you want to skip downloading some images, you need to add the list of the
 associated openstack services in the settings.yaml file.

```yaml
skip_container_images:
  - barbican
  - manila
  - sahara
  - swift
```

## How to run the Update and Upgrade

After the deployment of the OpenStack, the agent will look for an update or an
 upgrade playbook. If the playbook exists it will run it in order to upgrade the
 installation.

The agent expects the upgrade playbook to have the following naming convention:

`/etc/dci-openstack-agent/hooks/upgrade_from_OSP9_to_OSP10.yml`

In this example, `OSP9` is the current version and `OSP10` is the version to
 upgrade to. Here is an example of an update playbook:

`/etc/dci-openstack-agent/hooks/update_OSP9.yml`

During the upgrade, you may need to use a specific version of a repository.
Each component has its own .repo. They are located in
<http://$remoteci_ip/dci_repo/>, for instance:
<http://$remoteci_ip/dci_repo/dci_repo_RH7-RHOS-11.0.repo>.

## How to run my own set of tests ?

`dci-openstack-agent` ships with a pre-defined set of tests that will be run. It
 is however possible for anyone, in addition of the pre-defined tests, to run
 their own set of tests.

In order to do so, a user needs to drop the tasks to run in `/etc/dci-openstack-agent/hooks/local_tests.yml`.

**NOTE**: Tasks run in this playbook will be run from the undercloud node. To
 have an improved user-experience in the DCI web application, the suite should
 ideally returns `JUnit` formatted results. If not in JUnit, one will be able to
 download the results but not see them in the web interface directly.

## How to adjust the timer configuration

```console
# systemctl edit --full dci-openstack-agent.timer
```

You have to edit the value of the `OnUnitActiveSec` key. According to systemd
 documentation:

```
OnUnitActiveSec= defines a timer relative to when the unit the timer is activating was last activated.
OnUnitInactiveSec= defines a timer relative to when the unit the timer is activating was last deactivated.
```

DCI comes with a default value of 1h, you can increase to 12h for example.

## Tempest: How to select the Tempest tests to execute

The agent runs by default the Tempest "smoke" tests only. This should be
 sufficient to verify that the deployment is working without taking too long to
 run or have false negatives due to deployment specifics.

In the tempest configuration you can specify a regular expression against which
 each test will be matched before being executed.

The `test_white_regex` allows to filter the tests executed. For example, set it
 to an empty string to run all of the Tempest tests:
```console
$ vim /etc/dci-openstack-agent/settings.yml
(...)
test_white_regex: ""
(...)
```

Another option is to skip some specific tests using a blacklist:
```
(...)
test_black_regex:
  - tempest.api.image.v2.test_images_metadefs_namespace_properties.MetadataNamespacePropertiesTest.test_basic_meta_def_namespace_property
(...)
```

NOTE: Both `test_white_regex` and `test_black_regex` can be used at the same time.

## Tempest: How to disable services

The agent installs by default the meta tempest package openstack-tempest-all
 which contains all the tempest plugin tests. If you run tempest with the
 default configuration, you will execute tests on services that you probably
 don't want because the service isn't install.

In the tempest configuration you can disable tests per service. Each service has
 a boolean entry under [the service_available section](https://github.com/openstack/tempest/blob/master/tempest/config.py)
 (now moved to each individual plugin).

You can use the `tempest_extra_config` variable in the settings.yml file to add
 some services to disable (the following example disables tempest tests for  all
 services which may not be deployed by default, as of OSP 16):

```console
$ vim /etc/dci-openstack-agent/settings.yml

tempest_extra_config:
(...)
  service_available.aodh: False
  service_available.ceilometer: False
  service_available.panko: False
  service_available.barbican: False
  service_available.designate: False
  service_available.gnocchi: False
  service_available.ironic: False
  service_available.kuryr: False
  service_available.load_balancer: False
  service_available.manilla: False
  service_available.mistral: False
  service_available.novajoin: False
  service_available.sahara: False
  service_available.zaqar: False
(...)
```

**WARNING**: if you want to override any of the `tempest_extra_config` dictionnary, you also need to recopy the default values
from `/usr/share/dci-openstack-agent/group_vars/all`.

## Tempest: How to customize services

Depending on the drivers (cinder, manila, neutron, etc...) you are using, you
 will probably need to adapt the tempest configuration for specific tests. You
 can enable/disable features per OpenStack services. Every service has a section
 with the suffix '-feature-enabled' that allows to enable or disable features.
 If your cinder driver doesn't support cinder backup and you don't deploy the
 service, then you can disable the feature to avoid tempest failures.

```console
$ vim /etc/dci-openstack-agent/settings.yml

tempest_extra_config:
(...)
  volume-feature-enabled.backup: False
```

You can also do specific configuration per OpenStack services.
For instance, the cinder volume type tests are using the storage_protocol
 ('iSCSI') and vendor_name ('Open Source') fields that are configured by the
 storage driver. The default values in tempest don't match those in all storage
 drivers that's why you need to adapt the tempest configuration per services if
 you don't want some false positive. As an example, if you're using Ceph as a
 cinder backend you will need to update those values like:

```console
$ vim /etc/dci-openstack-agent/settings.yml

tempest_extra_config:
(...)
  volume.storage_protocol: 'ceph'
```

You will have some k/v with the 'network' prefix for neutron, 'compute' prefix
 for nova, etc... You can find most of the tempest config items in [the tempest project config](https://github.com/openstack/tempest/blob/master/tempest/config.py)

**WARNING**: if you want to override any of the `tempest_extra_config` dictionnary, you also need to recopy the default values
from `/usr/share/dci-openstack-agent/group_vars/all`.

## Tempest: Run a given test manually

It may be useful to restart a failing test to troubleshoot the problem:

```console
$ /home/stack/tempest
$ ostestr --regex tempest.api.network.test_ports.PortsIpV6TestJSON.test_update_port_with_security_group_and_extra_attributes
```

The Certification test-suite uses it's own configuration located at `/etc/redhat-certification-openstack/tempest.conf`. Is a copy of `/home/stack/tempest/etc/tempest.conf`.

## How to test several versions of OpenStack

You can of course run different versions of OpenStack with the same remoteci.
 To do so, you need first to adjust the way systemd call the agent:

```console
# systemctl edit --full dci-openstack-agent
```

Content :

```ini
[Unit]
Description=DCI Ansible Agent

[Service]
Type=oneshot
WorkingDirectory=/usr/share/dci-openstack-agent
EnvironmentFile=/etc/dci-openstack-agent/dcirc.sh
ExecStart=-/usr/bin/ansible-playbook -vv /usr/share/dci-openstack-agent/dci-openstack-agent.yml -e @/etc/dci-openstack-agent/settings.yml -e dci_topic=OSP10
ExecStart=-/usr/bin/ansible-playbook -vv /usr/share/dci-openstack-agent/dci-openstack-agent.yml -e @/etc/dci-openstack-agent/settings.yml -e dci_topic=OSP11
ExecStart=-/usr/bin/ansible-playbook -vv /usr/share/dci-openstack-agent/dci-openstack-agent.yml -e @/etc/dci-openstack-agent/settings.yml -e dci_topic=OSP12
SuccessExitStatus=0
User=dci-openstack-agent

[Install]
WantedBy=default.target
```

In this example, we do a run of OSP10, OSP11 and OSP12 everytime we start the
 agent.

### How to manually run the hooks

You can prepare a minimal playbook like this one:

```console
# cat run_hook.yml
- hosts: localhost
  tasks:
    - include_tasks: /etc/dci-openstack-agent/hooks/success.yml
```

Then call it using the `ansible` command:

```console
# ansible-playbook run_hook.yml
```

The tasks will be run on the local machine and nothing will be sent to the DCI server.

## Updating ansible roles

DCI OpenStack agent relies on Ansible roles that are maintained externally.
When a role is updated upstream, the agent local copy in the `roles` directory
needs to be synchronized.
The `fech-roles` scripts is provided to ensure that the agents roles are refreshed.
You will find it in the top-level directory of the dci-openstack-agent repository.

```console
# fetch-roles
```

Sometimes, you will not be able to use vanilla repositories due to some patches that
can't be merged for different reasons. Rather than forking, you should open a review
in gerrit, leave it unmerged, and synchronize from the open review HEAD.
The pros are you keep the full history of your patch, and can easily rebase when
upstream role is updated.
