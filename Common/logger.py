import logging
import time
import os.path


# 创建logger实例
logger_name = 'mylogger'
logger = logging.getLogger(logger_name)
# 设置日志级别  即只有日志级别大于等于DEBUG的日志才会输出
logger.setLevel(logging.DEBUG)


# 以当天日期作为日志名称
ct = time.strftime('%Y-%m-%d', time.localtime(time.time()))
# os.path.dirname()获取指定文件路径的上级路径
path_dir = os.path.dirname(__file__)
log_path = os.path.abspath(os.path.dirname(path_dir))+'/log'
log_name = os.path.join(log_path, ct+'.log')

# 创建FileHandler处理器  将warn级别及以上的日志信息输出到指定文件
fh = logging.FileHandler(log_name, encoding='utf8')
fh.setLevel(logging.WARNING)


# 创建StremHandler处理器  将DEBUG级别及以上的日志信息输出到控制台
sh = logging.StreamHandler()
# sh.setLevel(logging.DEBUG)


# 设置输出格式
# asctime:打印日志的世界  levename:打印日志级别名称 funcname:打印日志的当前函数 message:打印日志信息
fmt = '%(asctime)s - %(levelname)s - %(message)s'
datefmt = '%Y-%m-%d %H:%M:%S'
formatter = logging.Formatter(fmt, datefmt)


# 添加处理器和格式到logger
fh.setFormatter(formatter)
sh.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(sh)


def debug(message):
    logger.debug(message)


def info(message):
    logger.info(message)


def warning(message):
    logger.warning(message)


def error(message):
    logger.error(message)


def exception(e):
    logger.exception(e)
# 测试
# logger.warning('张欢的自动化测试框架')
