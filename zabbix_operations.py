# zabbix_operations.py

from utils import zabbix_api_request

class ZabbixOperations:
    def __init__(self, url, auth_token):
        self.url = url
        self.auth_token = auth_token

    def get_hosts(self, tags):
        """Obtiene la lista de hosts con los tags especificados"""
        params = {
            'output': ['hostid', 'host', 'interfaces'],
            'selectInterfaces': ['ip'],
            'tags': tags
        }
        result = zabbix_api_request(self.url, self.auth_token, "host.get", params)
        return result.get('result', [])

    def get_items_for_host(self, host_id, keys):
        """Obtiene los items para un host"""
        params = {
            'output': 'extend',
            'hostids': [host_id],
            'search': {'key_': keys},
            'monitored': True,
            'searchWildcardsEnabled': True
        }
        result = zabbix_api_request(self.url, self.auth_token, "item.get", params)
        return result.get('result', [])

    def get_trend_data(self, itemid, time_from, time_till):
        """Obtiene los datos de tendencia para un item"""
        params = {
            "output": ["itemid", "clock", "num", "value_min", "value_avg", "value_max"],
            "itemids": [itemid],
            "time_from": time_from,
            "time_till": time_till,
            "limit": "20000"
        }
        result = zabbix_api_request(self.url, self.auth_token, "trend.get", params)
        return result.get('result', [])