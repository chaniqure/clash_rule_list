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

