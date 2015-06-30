from copy import deepcopy

import requests

from checks import AgentCheck


class FileParser(AgentCheck):

    def __init__(self, name, init_config, agentConfig, instances=None):
        AgentCheck.__init__(self, name, init_config, agentConfig, instances)

    def _get_data(self, url):
        r = requests.get(url)
        r.raise_for_status()
        return r.json()

    def _load(self, instance):
        prefix = instance.get('prefix')
        if not prefix:
            raise Exception('FileParser instance missing "prefix" value.')

        mapping = instance.get('mapping')
        if not mapping:
            raise Exception('FileParser instance missing "mapping" value.')

        url = instance.get('url')
        if not url:
            raise Exception('FileParser instance missing "url" value.')

        mapping_separator = instance.get('mapping_separator', '.')

        tags = instance.get('tags', [])
        data = self._get_data(url)
        return data, tags, prefix, mapping, mapping_separator, url

    def check(self, instance):
        data, tags, prefix, mapping, mapping_separator, url = self._load(instance)

        for key, info in mapping.items():
            v = deepcopy(data)
            path = info.get('path', key)
            type_ = info.get('type', 'gauge')
            for elt in path.split(mapping_separator):
                v = v[elt]
            k = '%s.%s' % (prefix, key)
            getattr(self, type_)(k, v, tags=tags)
