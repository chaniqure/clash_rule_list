import shutil


def copy(src, dest):
    shutil.copy(src, dest)


def write(file, content: str):
    with open(file, 'w', encoding='utf-8') as f:
        f.write(content)


def write_line(file, data: list[str]):
    with open(file, 'w', encoding='utf-8') as f:
        for content in data:
            f.write(content)


def read(file):
    with open(file, 'r', encoding='utf-8') as f:
        file_content = f.read()
    return file_content


def get_filename(s: str):
    if s.__contains__('/'):
        split = s.split('/')
        s = split[len(split) - 1]
        if s == '':
            s = split[len(split) - 2]
    if s.__contains__('.'):
        split = s.split('.')
        s = split[len(split) - 2]
        if s.__contains__('='):
            split = s.split('=')
            s = split[len(split) - 1]
        if s == '':
            s = split[len(split) - 3]
    return s


def find_str_between(content: str, start_prefix: str, end_prefix: str):
    data = content.split('\n')
    length = len(data)
    if length == 0:
        return data
    start_index = 0
    end_index = length
    start_prefix = start_prefix.strip()
    end_prefix = end_prefix.strip()
    for i in range(length):
        if start_prefix != '' and start_index == 0 and data[i].startswith(start_prefix):
            start_index = i
        if end_prefix != '' and end_index == length and data[i].startswith(end_prefix):
            end_index = i
    return '\n'.join(data[start_index:end_index])


def concat_file_between(s: str, start_prefix: str, end_prefix: str, insert_data: str):
    data = s.split('\n')
    if len(data) == 0:
        return data
    result = []
    before = data[0]
    after = data[1]
    start_flag = True
    end_flag = True
    for i in range(len(data)):
        if i == 0 or i == 1:
            result.append(data[i])
            continue
        if data[i - 1].strip() != '':
            before = data[i - 1].strip()
        if data[i].strip() != '':
            after = data[i].strip()
        if start_prefix != '':
            start_flag = before.startswith(start_prefix)
        if start_flag and end_prefix != '':
            end_flag = after.startswith(end_prefix)
        if start_flag and end_flag:
            result.extend(insert_data.split('\n'))
        result.append(data[i])
    return '\n'.join(result)


if __name__ == '__main__':
    s = read('E:/code/python/clash_rule_list/conf/rule.yml')
    print(find_str_between(s, 'rules:', ''))
    # s = read('E:/code/python/clash_rule_list/result/subscribe/self_provider_config.yml')
    # insert_data = read('E:/code/python/clash_rule_list/conf/rule.yml')
    # write('./result.txt', concat_file_between(s, 'allow-lan', 'mode:', insert_data))
