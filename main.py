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


def refresh_clash_rule():
    base_path = os.getcwd()
    clash = Clash(base_path + '/conf/local.ini', base_path + '/conf/rule.yml')
    rule = clash.get_clash_rule('reject')
    log.info('转换后的clash的规则数量：%s', len(rule))


if __name__ == '__main__':
    refresh_clash_rule()
