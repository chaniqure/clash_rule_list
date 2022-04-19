import os
import shutil
import sys
import time
import urllib.parse
import yaml

from pkg.lib.github import GistFile
from pkg.lib.github import Github
from pkg.util import logger, ini, request, clash_rule_util
from pkg.util import file_util

# 文档地址 https://github.com/tindy2013/subconverter/blob/master/README-cn.md#%E8%87%AA%E5%8A%A8%E4%B8%8A%E4%BC%A0
# 拒绝策略
log = logger.get_logger('clash')


class RemoteClashRuleConfig:
    def __init__(self, file):
        content = file_util.read(file)
        d = yaml.load(content, yaml.FullLoader)
        self.reject = d['rule-list']['reject']
        self.direct = d['rule-list']['direct']
        self.proxy = d['rule-list']['proxy']
        self.rules = file_util.find_str_between(content, 'rules', '')
        self.rule_providers = file_util.find_str_between(content, 'rule-providers', 'rules')

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
        self.token = parser.item('github', 'token')
        self.upload = bool(parser.item('github', 'token'))
        self.subconverter_config = parser.section('subconverter')
        item = parser.item('rule', 'config_file')
        self.rule_files = item.split(',')


class Clash:

    def __init__(self):
        base_path = os.getcwd()
        converter_config = base_path + '/conf/local.ini'
        rule_config = base_path + '/conf/rule.yml'
        # 获取所有section
        self.__clash_config = ClashConfig(converter_config)
        self.__remote_rule = RemoteClashRuleConfig(rule_config)
        self.__github = Github(self.__clash_config.token)

    def __get_urls(self, rule_type):
        urls = []
        if rule_type == 'reject':
            return self.__remote_rule.reject
        elif rule_type == 'direct':
            return self.__remote_rule.direct
        elif rule_type == 'proxy':
            return self.__remote_rule.proxy
        return urls

    def get_clash_rule_list(self, rule_type):
        data = []
        for url in self.__get_urls(rule_type):
            try:
                resp = request.get(url)
                if resp is None:
                    continue
                before = len(data)
                data.extend(clash_rule_util.convert_to_clash_rule_list(resp))
                log.info('%s：获取数据成功，共：%s条', url, len(data) - before)
            except ConnectionError:
                log.error('获取规则失败')
        if len(data) == 0:
            log.info('获取在线规则失败，转为获取本地规则')
            local_rule_dir = os.getcwd() + '/conf/remote_rule_text/' + rule_type
            for file in os.listdir(local_rule_dir):
                file_content = file_util.read(local_rule_dir + '/' + file)
                data.extend(clash_rule_util.convert_to_clash_rule_list(file_content))
        return list(set(data))

    def get_clash_rule_provider(self, rule_type):
        data = {}
        for url in self.__get_urls(rule_type):
            try:
                url = str(url)
                resp = request.get(url)
                if resp is None:
                    continue
                log.info('%s：获取rule-provider成功', url)
                data['{}.yml'.format(file_util.get_filename(url))] = clash_rule_util.convert_to_clash_rule_provider(resp)
            except ConnectionError:
                log.error('获取规则失败')
        if len(data) == 0:
            log.info('获取在线规则失败，转为获取本地规则')
            local_rule_dir = os.getcwd() + '/conf/remote_rule_text/' + rule_type
            for file in os.listdir(local_rule_dir):
                file_content = file_util.read(local_rule_dir + '/' + file)
                data['{}.yml'.format(file_util.get_filename(file))] = clash_rule_util.convert_to_clash_rule_provider(file_content)
        return data

    # 刷新本地的规则集，
    def refresh_local_rule_list(self, rule_type, filename):
        data = self.get_clash_rule_list(rule_type)
        result = list(set(data))
        log.info('数据处理完毕，总共%s条规则', len(result))
        if len(result) == 0:
            log.info('没有规则，结束')
            return 0
        content = '\n'.join(result)
        # converter_rule_file = (self.__clash_config.converter_path + '/rules/{}').format(filename)
        local_rule_file = (os.getcwd() + '/result/rule_list/{}').format(filename)
        # file_util.write(converter_rule_file, content)
        file_util.write(local_rule_file, content)

    def refresh_local_rule_provider(self, rule_type):
        data = self.get_clash_rule_provider(rule_type)
        for k, v in data.items():
            file_util.write((os.getcwd() + '/result/rule_providers/{}').format(k), v)

    def refresh_remote(self):
        if is_win():
            os.startfile(self.__clash_config.converter_path + '/subconverter.exe')
            time.sleep(2)
        for config_rule_file in self.__clash_config.rule_files:
            file_str = '{}/config/{}'.format(self.__clash_config.converter_path, config_rule_file)
            if os.path.exists(file_str):
                os.remove(file_str)
                log.info("文件%s已存在，进行删除", file_str)
            shutil.copy(os.getcwd() + '/conf/subconverter_config/' + config_rule_file, file_str)
            resp = request.get(self.__get_sub_url(config_rule_file))
            log.info('执行完毕，获取到的数据长度：%s', len(resp))
            self.__hand_result(config_rule_file, resp)
        if is_win():
            time.sleep(1)
            os.system('taskkill /f /im %s' % 'subconverter.exe')
            log.info('关闭程序成功')

    def __hand_result(self, name, content):
        if self.__clash_config.upload:
            rule_file = GistFile(name, content.encode("utf-8").decode("latin1"))
            files = [rule_file]
            result = self.__github.gist_batch_save(name, files)
            log.info('同步到github结果：%s', result)
        else:
            file = os.getcwd() + '/result/subscribe/' + name
            file_util.write(file, content)

    def __get_sub_url(self, config_rule_file):
        c = self.__clash_config.subconverter_config
        data = [urllib.parse.urlencode({'config': 'config/{}'.format(config_rule_file)}), 'target=clash']
        sub_url_prefix = 'http://127.0.0.1:25500/sub?'
        for key, value in c.items():
            value = value.strip()
            if value == '':
                continue
            if key == 'url':
                data.append(urllib.parse.urlencode({'url': value}))
                continue
            data.append('{}={}'.format(key, value))
        return sub_url_prefix + '&'.join(data)
