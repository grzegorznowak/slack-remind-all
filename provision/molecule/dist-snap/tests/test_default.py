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
