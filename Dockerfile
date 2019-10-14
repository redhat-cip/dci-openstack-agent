FROM centos:7

LABEL name="dci-openstack-agent"
LABEL version="1.0.0"
LABEL maintainer="DCI Team <distributed-ci@redhat.com>"

ENV LANG en_US.UTF-8

RUN yum upgrade -y && \
  yum -y install epel-release https://packages.distributed-ci.io/dci-release.el7.noarch.rpm && \
  yum -y install gcc ansible python python2-devel python2-pip chrony openssh iproute && \
  yum -y install ansible-role-dci-import-keys ansible-role-dci-retrieve-component ansible-role-dci-sync-registry dci-ansible && \
  yum clean all

ADD dci-openstack-agent /usr/share/dci-openstack-agent
RUN pip install -r /usr/share/dci-openstack-agent/requirements.txt && pip freeze

# Ansible-runner bug: https://github.com/ansible/ansible-runner/issues/219
RUN cp /usr/share/dci/callback/dci.py /usr/lib/python2.7/site-packages/ansible_runner/callbacks

WORKDIR /usr/share/dci-openstack-agent

CMD ["python", "entrypoint.py"]
