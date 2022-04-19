import re

import requests

from pkg.util import logger

empty = ''


log = logger.get_logger('request')


domain_regex = '(?:[-\\w.]|(?:%[\\da-fA-F]{2}))+'


ip_regex = '[0-9]+(?:\\.[0-9]+){3}'


def format_domain(s: str):
    s = s.strip()
    if s == '' or s == '.':
        return ''
    if s.startswith('.'):
        s = s.removeprefix('.')
    if s.endswith('.'):
        s = s.removesuffix('.')
    return s


def convert_to_clash_rule_list(text: str):
    before_list = text.split("\n")
    effective_list = []
    for domain in before_list:
        s = domain.strip()
        if s.startswith('!') or s.startswith('#') or s.startswith('payload') or s.startswith('&') \
                or s.startswith('/') or s.startswith('-a') or s.endswith('/') or s.endswith('='):
            continue
        if s.startswith('0.0.0.0') or s.startswith('127.0.0.1'):
            s = s.removeprefix('0.0.0.0').removeprefix('127.0.0.1')
        effective_list.append(s)
    after = '\n'.join(effective_list)
    domain_list = re.findall(domain_regex, after)
    ip_list = re.findall(ip_regex, after)
    result = []
    for domain in domain_list:
        s = format_domain(str(domain))
        prefix = 'DOMAIN-SUFFIX,'
        if s.startswith('www'):
            prefix = 'DOMAIN,'
        else:
            arr = len(s.split('.'))
            if arr == 1:
                prefix = 'DOMAIN-KEYWORD,'
        result.append(prefix + s)
    for ip in ip_list:
        result.append('IP-CIDR,' + ip + '/32,no-resolve')
    return result


def convert_to_clash_rule_provider(text: str):
    before_list = text.split("\n")
    effective_list = []
    for domain in before_list:
        s = domain.strip()
        if s.startswith('!') or s.startswith('#') or s.startswith('&') or s.startswith('[') \
                or s.startswith('/') or s.endswith('/') or s.endswith('='):
            continue
        if s.startswith('-') and not s.startswith('- \'') and not s.startswith('- DOMAIN'):
            continue
        if s.__contains__('?') or s.__contains__('/') or s.__contains__('*') or s.__contains__('$'):
            continue
        if s.startswith('payload:'):
            return text
        if s.startswith('0.0.0.0') or s.startswith('127.0.0.1'):
            s = s.removeprefix('0.0.0.0').removeprefix('127.0.0.1')
        if s.startswith('DOMAIN-SUFFIX,'):
            s = s.removeprefix('DOMAIN-SUFFIX,')
        if s.startswith('DOMAIN-KEYWORD,'):
            s = s.removeprefix('DOMAIN-KEYWORD,')
        if s.startswith('DOMAIN,'):
            s = s.removeprefix('DOMAIN,')
        effective_list.append(s)
    after = '\n'.join(effective_list)
    domain_list = re.findall(domain_regex, after)
    result = []
    keyword_template = '  - \'+.{}.+\''
    domain_template = '  - \'{}\''
    domain_regex_template = '  - \'+.{}\''
    for domain in domain_list:
        s = format_domain(str(domain))
        if s.startswith('www'):
            result.append(domain_template.format(s))
        else:
            arr = len(s.split('.'))
            if arr == 1:
                result.append(keyword_template.format(s))
            elif arr == 2:
                result.append(domain_regex_template.format(s))
            else:
                result.append(domain_template.format(s))
    return 'payload:\n' + '\n'.join(result)


if __name__ == '__main__':
    resp = requests.get('https://anti-ad.net/clash.yaml').text
    print('获取数据成功')
    # with open('./my.txt', 'w', encoding='utf-8') as f:
    #     for t in convert_to_clash_rule_list_self(resp):
    #         f.write(t)
    #         f.write('\n')
    with open('rule.txt', 'w', encoding='utf-8') as f:
        f.write(convert_to_clash_rule_provider(resp))
        f.write('\n')
    # with open('rule.txt', 'w', encoding='utf-8') as f:
    #     for t in convert_to_clash_rule_list(resp):
    #         f.write(t)
    #         f.write('\n')