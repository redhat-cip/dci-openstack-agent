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
