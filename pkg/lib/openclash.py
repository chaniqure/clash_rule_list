import requests
import os

from pkg.util import logger

data_list = ["reject", "icloud", "apple", "google", "proxy", "direct", "private", "gfw",
             "greatfire", "tld-not-cn", "telegramcidr", "cncidr", "lancidr", "applications"]

data_prefix = {
    "direct": "- DOMAIN,",
    "proxy": "- DOMAIN,",
    "private": "- DOMAIN-SUFFIX,",
    "apple": "- DOMAIN-SUFFIX,",
    "icloud": "- DOMAIN-SUFFIX,",
    "google": "- DOMAIN-SUFFIX,",
    "gfw": "- DOMAIN-SUFFIX,",
    "greatfire": "- DOMAIN-SUFFIX,",
    "tld-not-cn": "- DOMAIN-SUFFIX,",
    "telegramcidr": "- IP-CIDR,",
    "lancidr": "- IP-CIDR,",
    "cncidr": "- IP-CIDR,",
    "reject": "- DOMAIN-SUFFIX,",
}

data_suffix = {
    "reject": "🛑 广告拦截",
    "apple": "🍎 苹果服务",
    "google": "📢 谷歌FCM",
    "direct": ",🎯 全球直连",
    "telegramcidr": "📲 电报信息",
    "gfw": "🧱 墙",
    "icloud": "☁ 苹果云",
    "private": "🔏 私人",
    "proxy": "🪜 代理",
    "applications": "📱 应用",
}

data_regex = {
    "direct": "- \'",
    "proxy": "- \'",
    "private": "- \'+.",
    "apple": "- \'+.",
    "icloud": "- \'+.",
    "google": "- \'+.",
    "gfw": "- \'+.",
    "greatfire": "- \'+.",
    "tld-not-cn": "- \'+.",
    "telegramcidr": "- \'",
    "lancidr": "- \'",
    "cncidr": "- \'",
    "applications": "- ",
    "reject": "- \'+."
}

urls = ["https://cdn.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/{}.txt"]

log = logger.get_logger('clash')

# 获取基础数据
def query_data(type):
    for url in urls:
        try:
            return requests.get(url.format(type)).text
        except BaseException:
            log.error("请求报错")


def format_domain(key, data):
    domain_list = data.split("\n")
    results = []
    v = (data_suffix[key] if data_suffix.__contains__(key) else key)
    if len(domain_list) > 0:
        del domain_list[0]
        for domain in domain_list:
            s = domain.strip().replace(data_regex[key], "").replace("\'", "")
            prefix = data_prefix[key] if data_prefix.__contains__(key) else "- " + key + ","
            if len(prefix) == 0:
                prefix = '- DOMAIN-SUFFIX,'
            results.append(prefix + s + ',' + v)
    return results


if __name__ == '__main__':
    filter = ['reject']
    for key in data_list:
        if len(filter) > 0 and filter.count(key) == 0:
            log.info("{}不需要获取数据，跳过……".format(key))
            continue
        data = query_data(key)
        if data is None:
            log.info("{}获取数据失败，跳过……".format(key))
            continue
        results = format_domain(key, data)
        file = "./clash/{}.txt".format(key)
        if os.path.exists(file):
            os.remove(file)
            log.info("文件{}已存在，进行删除".format(file))
        with open(file, 'w', encoding='utf-8') as f:
            for result in results:
                f.write(result)
                f.write("\n")
