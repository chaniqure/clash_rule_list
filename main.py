import json
import os

import requests

from lib.clash import Clash
from util import logger

log = logger.get_logger('clash')


def get_clash_rule_num():
    headers = {
        'Authorization': 'Bearer 123456'
    }
    resp = requests.get('http://10.1.1.1:9090/rules', headers=headers)
    rule = json.loads(resp.text)
    rules = rule['rules']
    log.info('OpenClash规则数量：%s', len(rules))


def get_rule():
    base_path = os.getcwd()
    clash = Clash(base_path + '/conf/local.ini', base_path + '/conf/rule.yml')
    log.info('转换后的clash的规则数量：%s', len(clash.get_clash_rule('reject')))


def refresh_local_clash_rule():
    base_path = os.getcwd()
    clash = Clash(base_path + '/conf/local.ini', base_path + '/conf/rule.yml')
    clash.write_rule('reject', 'Self_Reject.list')
    clash.write_rule('direct', 'Self_Direct.list')
    clash.write_rule('proxy', 'Self_Proxy.list')


if __name__ == '__main__':
    get_rule()
