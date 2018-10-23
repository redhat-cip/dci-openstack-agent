#!/bin/bash


function start()
{
    rm /var/lib/dci-openstack-agent/job_info.yaml
    ansible-playbook -e @/etc/dci-openstack-agent/settings.yml new.yml
}

function load_context() {
    export DCI_JOB_ID=$(python -c 'import yaml; print(yaml.load(open("/var/lib/dci-openstack-agent/job_info.yaml", "r")))["job"]["id"]')
}

function run_play()
{
    local play=$1
    load_context
    ansible-playbook -e job_informations=@/tmp/job_info.yaml -e @/etc/dci-openstack-agent/settings.yml ${play} || rescue

}

function rescue()
{
    run_play rescue.yml
    exit 1
}

start
run_play pre-run.yml
run_play deploy.yml
run_play test.yml
run_play success.yml
