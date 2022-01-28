# RHOSP support in DCI

RHOSP is being made available as both RPMs and containers. DCI allows you to access
pre-release bits in an automated way.

## Supported versions

Starting from OSP16, components are shipped as Red Hat build system composes rather than puddles.
Both composes and puddles are sets of RPM repositories, puddles have flatter hierarchy and cannot be filtered
through dci-downloader.

| topic   | type    | Architecture |
| ------- | ------- | ------------ |
| OSP13   | puddle  | x86_64       |
| OSP15   | puddle  | x86_64       |
| OSP16   | compose | x86_64       |
| OSP16.1 | compose | x86_64       |
| OSP16.2 | compose | x86_64       |

Contact your EPM if you would like a specific version or architecture not listed here.

## FAQ

### Where can some documentation about the Red Hat OpenStack Platform Life Cycle?

[Red Hat OpenStack Platform Life Cycle official document](https://access.redhat.com/support/policy/updates/openstack/platform/)
