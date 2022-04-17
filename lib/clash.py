import os
import shutil
import sys
import time

import yaml

from lib.github import GistFile
from lib.github import Github
from util import clash_rule_util
from util import ini
from util import logger
from util import request

# 文档地址 https://github.com/tindy2013/subconverter/blob/master/README-cn.md#%E8%87%AA%E5%8A%A8%E4%B8%8A%E4%BC%A0
# 拒绝策略
log = logger.get_logger('clash')


class RemoteClashRule:
    def __init__(self, file):
        with open(file, 'r', encoding='utf-8') as f:
            file_content = f.read()
        content = yaml.load(file_content, yaml.FullLoader)
        self.reject = content['rule']['reject']
        self.direct = content['rule']['direct']
        self.proxy = content['rule']['proxy']

    def __str__(self):
        return '{}\n\treject：{}\n\tdirect：{}\n\tproxy：{}\n{}'.format('{', self.reject, self.direct, self.proxy, '}')


def is_win():
    return sys.platform.startswith('win')


class ClashConfig:
    def __init__(self, config):
        parser = ini.IniParser(config)
        section = 'linux'
        if is_win():
            section = 'windows'
        self.converter_path = parser.item(section, 'converter_path')
        self.result_url = parser.item(section, 'result_url')
        self.token = parser.item('github', 'token')
        item = parser.item('rule', 'config_file')
        self.rule_files = item.split(',')


class Clash:

    def __init__(self):
        base_path = os.getcwd()
        converter_config = base_path + '/conf/local.ini'
        rule_config = base_path + '/conf/rule.yml'
        # 获取所有section
        self.__clash_config = ClashConfig(converter_config)
        self.__remote_rule = RemoteClashRule(rule_config)
        self.__github = Github(self.__clash_config.token)

    def get_clash_rule(self, rule_type):
        urls = []
        if rule_type == 'reject':
            urls = self.__remote_rule.reject
        elif rule_type == 'direct':
            urls = self.__remote_rule.direct
        elif rule_type == 'proxy':
            urls = self.__remote_rule.proxy
        data = []
        for url in urls:
            resp = request.get(url)
            if resp is None:
                continue
            before = len(data)
            domain_list = resp.split("\n")
            if len(domain_list) > 0:
                for domain in domain_list:
                    s = clash_rule_util.convert(domain)
                    if str.isspace(s):
                        continue
                    data.append(s)
            log.info('%s：获取数据成功，共：%s条', url, len(data) - before)
        return list(set(data))

    def refresh_local_rule_list(self, rule_type, filename):
        data = self.get_clash_rule(rule_type)
        file = (self.__clash_config.converter_path + '/rules/{}').format(filename)
        if os.path.exists(file):
            os.remove(file)
            log.info("文件%s已存在，进行删除", file)
        result = list(set(data))
        log.info('数据处理完毕，总共%s条规则', len(result))
        if len(result) == 0:
            log.info('没有规则，结束')
            exit(0)
        log.info('开始写入文件')
        with open(file, 'w', encoding='utf-8') as f:
            for result in result:
                f.write(result)
                f.write("\n")
        log.info('写入文件完毕')

    def __upload_github(self, name, content):
        rule_file = GistFile(name, content.encode("utf-8").decode("latin1"))
        files = [rule_file]
        result = self.__github.gist_batch_save('self custom clash rule', files)
        log.info('同步到github结果：%s', result)

    def refresh_remote(self):
        if is_win():
            os.startfile(self.__clash_config.converter_path + '/subconverter.exe')
            time.sleep(2)
        file_str = self.__clash_config.converter_path + '/config/self_config.yml'
        for rule in self.__clash_config.rule_files:
            if os.path.exists(file_str):
                os.remove(file_str)
                log.info("文件%s已存在，进行删除", file_str)
            shutil.copy(os.getcwd() + '/rule/' + rule, file_str)
            resp = request.get(self.__clash_config.result_url)
            log.info('执行完毕，获取到的数据长度：%s', len(resp))
            self.__upload_github(rule.split('.')[0], resp)
        if is_win():
            time.sleep(1)
            os.system('taskkill /f /im %s' % 'subconverter.exe')
            log.info('关闭程序成功')