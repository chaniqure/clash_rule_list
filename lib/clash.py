import os
import sys
import time
import json
import yaml
import shutil

from util import clash_rule_util
from util import logger
from util import request
from util import ini

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

    def __init__(self, converter_config, rule_config):
        # 获取所有section
        self.__clash_config = ClashConfig(converter_config)
        self.__remote_rule = RemoteClashRule(rule_config)

    def get_clash_rule(self, rule_type):
        urls = []
        if rule_type == 'reject':
            urls = self.__remote_rule.reject
        elif rule_type == 'reject':
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

    def write_rule(self, rule_type, filename):
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

    def refresh_remote_rule(self):
        if is_win():
            os.startfile(self.__clash_config.converter_path + '/subconverter.exe')
            time.sleep(2)
            resp = request.get(self.__clash_config.result_url)
            log.info('执行完毕，执行结果：%s\r\n', resp.ok)
            if not resp.ok:
                log.info('执行失败原因：%s\r\n', resp.text)
            time.sleep(1)
            os.system('taskkill /f /im %s' % 'subconverter.exe')
        else:
            resp = request.get(self.__clash_config.result_url)
            log.info('执行完毕，执行结果：%s', resp.ok)
            if not resp.ok:
                log.info('执行失败原因：%s\r\n', resp.text)
