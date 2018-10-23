import dci_runner.runner


r = dci_runner.runner.Runner()

r.load_env_file('/etc/dci-openstack-agent/settings.yml')
r.start(topic='OSP10')

try:
    r.run_playbook('pre-run.yml')
    r.run_playbook('deploy.yml')
    r.run_playbook('test.yml')
    r.run_playbook('success.yml')
except dci_runner.runner.DCIRunnerPlaybookFailure:
    r.run_playbook('rescue.yml')
