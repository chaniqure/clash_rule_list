import shutil


def copy(src, dest):
    shutil.copy(src, dest)


def write(file, content):
    with open(file, 'w', encoding='utf-8') as f:
        f.write(content)