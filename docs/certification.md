## Red Hat Certification:  Manually restart the certification test-suite

DCI runs the Red Hat Certification test-suite at the end of a deployment. It's
 configuration is stored in the `/etc/redhat-certification-openstack` directory.
`/etc/redhat-certification-openstack/tempest.conf` is the configuration file of
 tempest. You can manually re-run a certification test with the following
 command:

```console
$ ssh stack@undercloud
# rhcert-ci run --test cinder_volumes
```

In this example, `cinder_volumes` is the name of the test to re-run.

`rhcert` stores the log of the run in a directory in `/var/log/rhcert/runs`.
For instance `/var/log/rhcert/runs/1/openstack/` is the result of the first run.

```console
# cd /var/log/rhcert/runs
# ls
1  2
```

Here we have two directories, each of them are the results of a `rhcert` run.
The first one was probably triggered by the agent automatically.

```console
# cd 1
# ls
openstack  rhcert

# cd openstack/
# ls
cinder_volumes  director  sosreport  supportable

# ls cinder_volumes/
boot-tempest.log clone-tempest.log encryption-tempest.log migrate-tempest.log output.log quota-validation_report.json snapshot-validation_report.json volume-validation_report.json boot-validation_report.json clone-validation_report.json encryption-validation_report.json migrate-validation_report.json quota-tempest.log snapshot-tempest.log volume-tempest.log
```

Here we have the results of different sub-test run by `rhcert`. The most important file is output.log, it will give you a global overview of what have been run and the status of the different test.

## Red Hat Certification: How to skip its execution

Some users might want to skip the certification tests suite. This can be done via the settings file by adding `skip_certification: true` to `settings.yml` file.

## Red Hat Certification: How to add certification tests

By default, the agent will only run three rhcert tests: 'self_check',
 'supportable' and 'director'.
If you want to test a cinder/manila/neutron driver you will have to update the
 tests list and add the associated tests. For instance, if you want to run the
 cinder volumes certification tests:

```console
$ vim /etc/dci-openstack-agent/settings.yml
(...)
openstack_certification_tests:
  - self_check
  - supportable
  - director
  - cinder_volumes
```

You can find the list of the OpenStack tests available on the
 [Openstack Certification ansible role page](https://github.com/redhat-cip/ansible-role-openstack-certification/blob/master/defaults/main.yml#L35-L79)

## How to install the Red Hat Certification UI on the remoteci (and anywhere else)

You cannot install the redhat-certification interface on the remoteci. This is because of
dependency conflict. However, you can use the docker image:

```console
# docker pull registry.access.redhat.com/rhcertification/redhat-certification-management
# docker run -d  -p 8080:8080 --restart always --name rhcert registry.access.redhat.com/rhcertification/redhat-certification-management
```

Please visite the [redhat-certification-management image reference page](https://access.redhat.com/containers/?tab=tech-details&platform=openshift#/registry.access.redhat.com/rhcertification/redhat-certification-management) if you need more details.
