import os
import time
from Common import logger


class Server:
    """
    根据设备类型 启动appium服务,该类不支持多线程启动
    """
    def __init__(self, platform):
        self.platform = platform

    def start(self):
        # 1.启动服务前，先kill掉已经启动的进程(若有)
        os.system('killall node')
        # 2.根据设备类型启动服务 目前只针对iOS、Android,其他类型可后续扩展
        # 以当天日期作为appium日志名称
        ct = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        log_name = os.path.join('/Users/lanlanxiaohuan/Documents/', ct + 'appium.log')

        if str.upper(self.platform) == 'IOS':
            command = 'appium -p 4723 --no-reset --local-timezone --log-timestamp -g ' + log_name + '&'

        elif str.upper(self.platform) == 'ANDROID':
            pass
        else:
            logger.error('设备类型填写错误,无法启动服务,请检查！')
            exit(-1)

    def __device(self):
        # 设备名称 取第一个
        device_name = ''
        if str.upper(self.platform) == 'IOS':
            device_name = os.popen('idevice_id -l').readlines()[0]
        else:
            result = os.popen('adb devices').readlines()
            for res in result:
                # 适用于对 adb devices命令过滤
                if '\tdevice\n' in res:
                    return res.strip('\tdevice\n')
        return device_name



