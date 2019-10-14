#! /bin/bash


function build() {
    podman build -f Dockerfile -t dci-openstack-agent --no-cache
}

function run() {
	podman pull quay.io/distributedci/dci-openstack-agent:stable && source /etc/dci-openstack-agent/dcirc.sh && podman run --rm -ti --network host \
	-e DCI_CLIENT_ID \
	-e DCI_API_SECRET \
	-e DCI_CS_URL \
        -e DCI_LOCAL_REPO \
	-e PS1='\[\e[32m\][container]#\[\e[m\] ' \
	-v /etc/dci-openstack-agent/hooks/:/etc/dci-openstack-agent/hooks/ \
	-v /etc/dci-openstack-agent/settings.yml:/etc/dci-openstack-agent/settings.yml \
	-v /etc/dci-openstack-agent/hosts:/etc/dci-openstack-agent/hosts  \
	-v $DCI_LOCAL_REPO:/var/www/html \
	quay.io/distributedci/dci-openstack-agent:stable
}

function stop() {
    podman stop $(podman ps -a -q  --filter ancestor=dci-openstack-agent)
}

function kill() {
    podman kill $(podman ps -a -q  --filter ancestor=dci-openstack-agent)
}


function clean() {
    podman rmi quay.io/distributedci/dci-openstack-agent:stable
}

function shell() {
	podman pull quay.io/distributedci/dci-openstack-agent:stable && source /etc/dci-openstack-agent/dcirc.sh && podman run --rm -ti --network host \
	-e DCI_CLIENT_ID \
	-e DCI_API_SECRET \
	-e DCI_CS_URL \
        -e DCI_LOCAL_REPO \
	-e PS1='\[\e[32m\][container]#\[\e[m\] ' \
	-v /etc/dci-openstack-agent/hooks/:/etc/dci-openstack-agent/hooks/ \
	-v /etc/dci-openstack-agent/settings.yml:/etc/dci-openstack-agent/settings.yml \
	-v /etc/dci-openstack-agent/hosts:/etc/dci-openstack-agent/hosts  \
	-v $$DCI_LOCAL_REPO:/var/www/html \
	quay.io/distributedci/dci-openstack-agent:stable bash
}

$1
