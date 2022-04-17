import json
import os

import requests

from lib.clash import Clash
from lib.github import Github
from lib.github import GistFile
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
    clash = Clash()
    clash.refresh_local_rule_list('reject', 'Self_Reject.list')
    clash.refresh_local_rule_list('direct', 'Self_Direct.list')
    clash.refresh_local_rule_list('proxy', 'Self_Proxy.list')


def refresh_remote_clash_rule():
    clash = Clash()
    # clash.refresh_remote_rule('self_full_config.yml')
    clash.refresh_remote()


def upload_github():
    token = ''
    github = Github(token)
    base_path = os.getcwd()
    with open(base_path + '/self_full_config.yml', 'r', encoding='UTF-8') as f:
        data = f.read()
    file = GistFile('test', data.encode("utf-8").decode("latin1"))
    github.gist_save('test', [file])


if __name__ == '__main__':
    # upload_github()
    # refresh_local_clash_rule()
    # refresh_remote_clash_rule()
    refresh_remote_clash_rule()