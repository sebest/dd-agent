import simplejson as json

from tests.checks.common import AgentCheckTest, Fixtures


def _get_data_mock(url):
    with open(url, 'r') as go_output:
        res = json.loads(go_output.read())
        _get_data_mock.call += 2
        res['processors']['items'] += _get_data_mock.call
        return res
_get_data_mock.call = 0

class TestFileParser(AgentCheckTest):

    CHECK_NAME = 'fileparser'

    def __init__(self, *args, **kwargs):
        AgentCheckTest.__init__(self, *args, **kwargs)
        self._url = Fixtures.file('lumberjack.json')
        self.mock_config = {
            'instances': [{
                'url': self._url,
                'tags': ['env:prod', 'farm:proxy'],
                'prefix': 'lumberjack',
                'mapping': None,
            }],
        }
        self.mocks = {
            '_get_data': _get_data_mock,
        }

    def test_basic(self):
        self.mock_config['instances'][0]['mapping'] = {
            'processors.items': {
                'path': 'processors.items',
                'type': 'rate',
            }
        }
        self.run_check_twice(self.mock_config, mocks=self.mocks)
        self.assertMetric('lumberjack.processors.items', count=1, value=2, tags=['env:prod', 'farm:proxy'])

    def test_rewrite(self):
        self.mock_config['instances'][0]['mapping'] = {
            'processors_items': {
                'path': 'processors.items',
                'type': 'rate',
            }
        }
        self.run_check_twice(self.mock_config, mocks=self.mocks)
        self.assertMetric('lumberjack.processors_items', count=1, value=2, tags=['env:prod', 'farm:proxy'])
