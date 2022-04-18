import re

import requests

from pkg.util import logger

empty = ''


log = logger.get_logger('request')


domain_regex = '(?:[-\\w.]|(?:%[\\da-fA-F]{2}))+'


ip_regex = '[0-9]+(?:\\.[0-9]+){3}'


def convert_to_clash_rule_list(text: str):
    before_list = text.split("\n")
    effective_list = []
    for domain in before_list:
        s = domain.strip()
        if s.startswith('!') or s.startswith('#') or s.startswith('payload'):
            continue
        if s.startswith('0.0.0.0') or s.startswith('127.0.0.1'):
            s = s.removeprefix('0.0.0.0').removeprefix('127.0.0.1')
        effective_list.append(s)
    after = '\n'.join(effective_list)
    domain_list = re.findall(domain_regex, after)
    ip_list = re.findall(ip_regex, after)
    result = []
    for domain in domain_list:
        s = str(domain).strip()
        if s == '' or s == '.':
            continue
        if s.startswith('.'):
            s = s.removeprefix('.')
        if s.endswith('.'):
            s = s.removesuffix('.')
        prefix = 'DOMAIN-SUFFIX,'
        if s.startswith('www'):
            prefix = 'DOMAIN,'
        else:
            arr = len(s.split('.'))
            if arr == 1:
                prefix = 'DOMAIN-KEYWORD,'
            elif arr >= 3:
                prefix = 'DOMAIN,'
        result.append(prefix + s)
    for ip in ip_list:
        result.append('IP-CIDR,' + ip + '/32,no-resolve')
    return result


if __name__ == '__main__':
    resp = requests.get('https://easylist-downloads.adblockplus.org/easylist.txt').text
    print('获取数据成功')
    # with open('./my.txt', 'w', encoding='utf-8') as f:
    #     for t in convert_to_clash_rule_list_self(resp):
    #         f.write(t)
    #         f.write('\n')
    with open('rule.txt', 'w', encoding='utf-8') as f:
        for t in convert_to_clash_rule_list(resp):
            f.write(t)
            f.write('\n')