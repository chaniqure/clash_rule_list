empty = ''


def convert(domain):
    s = str(domain).strip()
    if s.startswith('!') or s.startswith('#') or s.startswith('payload'):
        return empty
    if s.startswith('DOMAIN-SUFFIX') or s.startswith('DOMAIN-KEYWORD'):
        return empty
    elif s.__contains__('IP-CIDR'):
        return empty
    elif s.__contains__('https'):
        return empty
    else:
        if s.__contains__('- \'+.'):
            s = s.replace('- \'+.', "").replace("\'", "")
        if s.__contains__('- \''):
            s = s.replace('- \'', "").replace("\'", "")
        if s.startswith('||*.'):
            s = s.replace('||*.', "").replace("^", "")
        if s.startswith('@@||'):
            s = s.replace('@@||', "").replace("^", "")
        if s.startswith('||'):
            s = s.replace('||', "").replace("^", "")
        if s.startswith('0.0.0.0') or s.startswith('127.0.0.1'):
            s = s.replace('0.0.0.0', "")
        if s.__contains__('{') or s.__contains__('}') or s.__contains__('(') or s.__contains__('+'):
            return empty
        if s.__contains__('^'):
            s = s.split('^')[0]
        s = s.strip().replace('|', "").replace('*', '').replace("\'", "")
        if s.startswith("."):
            s = s.strip().removeprefix('.')
        if s.endswith("."):
            s = s.strip().removesuffix('.')
        prefix = 'DOMAIN-SUFFIX,'
        if s.startswith('www'):
            prefix = 'DOMAIN,'
        else:
            arr = len(s.split('.'))
            if arr == 1:
                prefix = 'DOMAIN-KEYWORD,'
            elif arr >= 3:
                prefix = 'DOMAIN,'
    return prefix + s
