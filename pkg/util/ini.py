import configparser


class IniParser:

    def __init__(self, file):
        # 读取文件
        self.__file = file

    # 获取所有section
    def sections(self):
        parser = configparser.ConfigParser()
        parser.read(self.__file, encoding='utf-8')
        return parser.sections()

    def section(self, section):
        parser = configparser.ConfigParser()
        parser.read(self.__file, encoding='utf-8')
        return parser[section]

    # 获取section的items
    def items(self, section):
        parser = configparser.ConfigParser()
        parser.read(self.__file, encoding='utf-8')
        return parser.items(section)

    def item(self, section, key):
        parser = configparser.ConfigParser()
        parser.read(self.__file, encoding='utf-8')
        return parser[section][key]

    def write_item(self, section, key, value):
        parser = configparser.ConfigParser()
        parser.read(self.__file, encoding='utf-8')
        if not parser.has_section(section):
            self.__initsection(section)
        parser.set(section, key, value)
        with open(self.__file, 'w') as configfile:
            parser.write(configfile)

    def __initsection(self, section):
        parser = configparser.ConfigParser()
        parser.read(self.__file, encoding='utf-8')
        parser[section]['test'] = ''
        with open(self.__file, 'w') as configfile:
            parser.write(configfile)

    def remove_item(self, section, key):
        parser = configparser.ConfigParser()
        parser.read(self.__file, encoding='utf-8')
        parser.remove_option(section, key)
        with open(self.__file, 'w') as configfile:
            parser.write(configfile)

    def remove_section(self, section):
        parser = configparser.ConfigParser()
        parser.read(self.__file, encoding='utf-8')
        parser.remove_section(section)
        with open(self.__file, 'w') as configfile:
            parser.write(configfile)
