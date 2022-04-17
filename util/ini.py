import configparser


class IniParser:
    __con__ = configparser.ConfigParser()

    def __init__(self, file):
        # 读取文件
        self.__con__.read(file, encoding='utf-8')

    # 获取所有section
    def sections(self):
        return self.__con__.sections()

    # 获取section的items
    def items(self, section):
        return self.__con__.items(section)

    def item(self, section, key):
        return self.__con__[section][key]
