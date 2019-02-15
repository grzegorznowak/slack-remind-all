import os
import pytest

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


@pytest.mark.parametrize('port', [
    '3000'
])
def test_ports(host, port):
    assert host.socket("tcp://0.0.0.0:{}".format(port)).is_listening


@pytest.mark.parametrize('port', [
    '3000'
])
def test_up(host, port):

    cmd = host.run(
        'curl --write-out %{http_code} --silent ' +
        '--output /dev/null http://{}:{}/slack/slash'.format('0.0.0.0', port))

    assert cmd.stdout == '405'


def test_units(host):

    cmd = host.run('. /var/lib/slack_remind_all/pyenv/bin/activate && py.test /var/lib/slack_remind_all/tests')
    print(cmd.stdout)
    assert cmd.stdout == '405'
