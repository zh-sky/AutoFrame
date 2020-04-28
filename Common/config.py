import configparser
from Common import logger

"""
    封装解析文件方法
"""


class Config:
    # 构造方法
    def __init__(self, path):
        # 解析对象实例
        self.config = configparser.ConfigParser()
        # 配置文件路径
        self.path = path
        self.config.read(path)

    def read(self, section=None):
        """
        根据分组名返回对应的键值对
        @param: section 分组名
        """
        if section is not None:
            if section not in self.config.sections():
                logger.error('%s不在配置文件里' % section)
                return
            # 存放结果
            res = {}
            for item in self.config[section].items():  # item->(str,str)
                res[item[0]] = item[1]
            return res
        else:
            logger.warning('请输入想要读取的分组名称')

    def add(self, section, value):
        """
        向配置文件里添加分组信息
        @param: section 分组名->str
        @param: value 分组内的值->dict
        """
        # 对输入类型进行校验
        if type(section) == str and type(value) == dict:
            self.config[section] = value
            self.config.write(open(self.path, 'w'))
        else:
            logger.error('请输入字符串类型的key和字典类型的value')

    def delete_section(self, section):
        """
        删除配置文件内的分组
        @param section 分组名
        """
        try:
            self.config.remove_section(section)
        except KeyError as e:
            logger.error('输入的分组名%s不在配置文件里' % section)
        self.config.write(open(self.path, 'w'))

    def delete_option(self, section, option):
        """
        删除配置文件分组内的某个键值对
        @param: section 分组名
        @param: option 键值
        """
        if section in self.config.sections():
            if option in self.config[section].keys():
                self.config.remove_option(section, option)
                self.config.write(open(self.path, 'w'))
            else:
                logger.error('错误的键名%s' % option)
        else:
            logger.error('输入的分组名%s不在配置文件里' % section)


if __name__ == '__main__':
    config = Config('conf.ini')
    config.read('Mysql')
    config.delete_section('haha')
