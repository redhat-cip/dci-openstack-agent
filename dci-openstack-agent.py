# pylint: skip-file
import os
import os.path
import yaml

import ansible_runner

from dciclient.v1.api import context as dci_context
from dciclient.v1.api import job as dci_job
from dciclient.v1.api import topic as dci_topic
from dciclient.v1.api import jobstate as dci_jobstate
from dciclient.v1.api import file as dci_file

job_info_file = '/var/lib/dci-openstack-agent/job_info.yaml'
settings_file = '/etc/dci-openstack-agent/settings.yml'
share_dir = '/usr/share/dci-openstack-agent'
work_dir = '/var/lib/dci-openstack-agent'

dci_jobstate_id = None
dci_job_id = None
context = None

def schedule(context, topic='OSP12'):
    topic_res = dci_topic.list(context, where='name:' + topic)
    if topic_res.status_code == 200:
        topics = topic_res.json()['topics']
        if not len(topics):
            raise DciResourceNotFoundException(
                'Topic: %s resource not found' % self.topic
            )

        topic_id = topics[0]['id']
        res = dci_job.schedule(context, topic_id=topic_id)
        if res.status_code == 201:
            return dci_job.get(
                context, context.last_job_id,
                embed='topic,remoteci,components,rconfiguration')
        else:
            print(res.text)
    else:
        print(topic_res.text)


def load_extravars():
    extravars = {}
    for f in [job_info_file, settings_file]:
        with open(f, 'r') as stream:
            data = yaml.load(stream)
            for k, v in data.items():
                extravars[k] = v
    return extravars


def post_message(result, output='foo'):
    print('post_message')
    kwargs = {
        'name': result,
        'content': output and output.encode('UTF-8'),
        'mime': 'text/plain',
        'job_id': dci_job_id,
        'jobstate_id': dci_jobstate_id
    }

    r = dci_file.create(
        context,
        **kwargs)


def create_jobstate(comment, status='running'):
    global dci_jobstate_id
    r = dci_jobstate.create(
        context,
        status=status,
        comment=comment,
        job_id=dci_job_id)
    ns = r.json()
    dci_jobstate_id = ns['jobstate']['id']



def run_play(play_name):
    print('Calling %s!' % play_name)

    def lolilol(foo):
        if foo['event'] == 'playbook_on_task_start':
            return
        has_failed = bool(len(foo['event_data'].get('failures', {})))
        output = foo.get('stdout', '')
        if output:
            output += '\n'
        if has_failed:
            create_jobstate('failure', 'failure')
            post_message('failure', foo['stdout'])
        elif foo['event_data'].get('task_action'):
            output += '%s - %s - %s' % (foo['event_data'].get('task_action'), foo['event_data']['task_args'], foo['event_data'].get('task_path'))
            post_message(foo['event_data']['task'], output)
        elif foo['event_data'].get('task'):
            output += '%s - %s - %s' % (foo['event_data'].get('task'), foo['event_data']['task_args'], foo['event_data'].get('task_path'))
            post_message(foo['event_data']['task'], output)
        else:
            print("  > NON TASK: %s" % foo['event_data'])

    envvars = {k: os.environ[k] for k in os.environ if k.startswith('DCI_')}
    result = ansible_runner.run(
        playbook=os.path.join(share_dir, play_name),
        inventory='localhost ansible_user=root ansible_connection=local',
        envvars=envvars,
        extravars=load_extravars(),
        private_data_dir=work_dir,
        event_handler=lolilol)
    print(result.stats)
    print(result.stats['failures'])
    if result.stats['failures']:
        raise Exception


if os.path.isfile(job_info_file):
    os.unlink(job_info_file)
context = dci_context.build_signature_context()
job = schedule(context)
with open(job_info_file, 'w') as fd:
    fd.write(yaml.dump({'job_info': job.json()['job']}))
dci_job_id = job.json()['job']['id']
create_jobstate('foo', status='pre-run')

####################################################
####################################################
####################################################

try:
    run_play('pre-run.yml')
    run_play('deploy.yml')
    run_play('test.yml')
    run_play('success.yml')
except Exception:
    run_play('rescue.yml')
