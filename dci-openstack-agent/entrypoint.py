#! /usr/bin/env python

"""


cat /etc/dci-openstack-agent/settings.yml

dci_topic: OSP15
dci_tags: []
# dci_tags: ['lab1', 'osp15', 'driver abc']

"""
import os
import signal
import sys

import ansible_runner
from dciclient.v1.api import job, topic
from dciclient.v1.api.context import build_signature_context
import yaml


TOPIC='OSP15'
DEFAULT_SETTINGS_FILE='/etc/dci-openstack-agent/settings.yml'


def sigterm_handler(signal, frame):
    # This does NOT work with ansible_runner.run_async().
    print('Handle podman stop here !')


signal.signal(signal.SIGTERM, sigterm_handler)


def load_settings(settings_file=DEFAULT_SETTINGS_FILE):
    with open(settings_file, 'r') as settings:
        try:
            return yaml.load(settings, Loader=yaml.SafeLoader)
        except yaml.YAMLError as err:
            print("Error: failed to load config file ({})".format(err))
            sys.exit(1)

def main():
    client_id = os.environ.get('DCI_CLIENT_ID')
    if client_id:
        remoteci_id = client_id.split('/')[1]
    else:
        print("Error: DCI_CLIENT_ID variable is not set.")
        sys.exit(1)

    # Path is static in the container
    local_repo = '/var/www/html'
    settings = load_settings()

    if 'dci_topic' in settings.keys():
        print ("Topic is %s." % settings['dci_topic'])
    else:
        print ("Error ! No topic found in settings.")
        sys.exit(1)

    r = ansible_runner.run(
        private_data_dir="/usr/share/dci-openstack-agent/",
        inventory="/etc/dci-openstack-gant/hosts",
        verbosity=1,
        playbook="dci-openstack-agent.yml",
        extravars=settings,
        quiet=False)


if __name__ == '__main__':
    main()
