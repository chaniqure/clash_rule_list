import os
import shutil
import sys
import time
import urllib.parse
import yaml

from pkg.lib.github import GistFile
from pkg.lib.github import Github
from pkg.util import logger, ini, request, clash_rule_util

# 文档地址 https://github.com/tindy2013/subconverter/blob/master/README-cn.md#%E8%87%AA%E5%8A%A8%E4%B8%8A%E4%BC%A0
# 拒绝策略
log = logger.get_logger('clash')


class RemoteClashRuleList:
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


def write_data(file: str, data: str):
    log.info('开始写入文件：%s', file)
    if os.path.exists(file):
        os.remove(file)
        log.info("文件%s已存在，进行删除", file)
    with open(file, 'w', encoding='utf-8') as f:
        f.write(data)
    log.info('写入文件完毕')


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
        self.__remote_rule = RemoteClashRuleList(rule_config)
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
        # for url in urls:
        #     try:
        #         resp = request.get(url)
        #         if resp is None:
        #             continue
        #         before = len(data)
        #         data.extend(clash_rule_util.convert_to_clash_rule_list(resp))
        #         log.info('%s：获取数据成功，共：%s条', url, len(data) - before)
        #     except ConnectionError:
        #         log.error('获取规则失败')
        if len(data) == 0:
            log.info('获取在线规则失败，转为获取本地规则')
            local_rule_dir = os.getcwd() + '/conf/remote_rule_text/' + rule_type
            for file in os.listdir(local_rule_dir):
                with open(local_rule_dir + '/' + file, 'r', encoding='utf-8') as f:
                    file_content = f.read()
                    data.extend(clash_rule_util.convert_to_clash_rule_list(file_content))
        return list(set(data))

    # 刷新本地的规则集，
    def refresh_local_rule_list(self, rule_type, filename):
        data = self.get_clash_rule(rule_type)
        result = list(set(data))
        log.info('数据处理完毕，总共%s条规则', len(result))
        if len(result) == 0:
            log.info('没有规则，结束')
            return 0
        content = '\n'.join(result)
        converter_rule_file = (self.__clash_config.converter_path + '/rules/{}').format(filename)
        local_rule_file = (os.getcwd() + '/result/rule_list/{}').format(filename)
        write_data(converter_rule_file, content)
        write_data(local_rule_file, content)

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
            write_data(file, content)

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