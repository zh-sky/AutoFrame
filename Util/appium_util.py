from Common import logger
import os
import threading
import Util.devicetype


class Port:
    def __init__(self):
        self.dos = DosCmd()

    def port_is_used(self, port_num):
        """
        判断端口是否被占用
        :param port_num: 端口号
        :return: Boolean
        """
        # Mac和Windows查看端口号的命令不一样   这里用的是Mac环境下的
        command = 'lsof -i tcp:' + str(port_num)
        result = self.dos.execute_cmd_result(command)
        # 若端口号被占用
        if len(result) > 0:
            flag = True
        else:
            flag = False
        return flag

    def create_port_list(self, start_port, device_list):
        """
        生成可用端口
        :param start_port: 开始端口
        :param device_list: 设备列表
        :return: list 端口列表
        """
        port_list = []
        if device_list is not None:
            while len(port_list) != len(device_list):
                if self.port_is_used(start_port) is not True:
                    port_list.append(start_port)
                start_port += 1
            return port_list
        else:
            logger.info('设备列表为空,请检查设备连接是否完好')
            # 设备列表为空时，程序不再向下执行
            exit(-1)


class DosCmd:
    """
    执行cmd命令
    """
    @staticmethod
    def execute_cmd_result(command):
        """
        执行命令 & 返回得到的结果
        """
        result_list = []
        result = os.popen(command).readlines()
        # print(result)
        for res in result:
            # 适用于对 adb devices命令过滤
            if '\tdevice\n' in res:
                result_list.append(res.strip('\tdevice\n'))
            # 对普通命令结果 过滤掉换行符
            elif '\n' in res:
                result_list.append(res.strip('\n'))
        return result_list

    @staticmethod
    def execute_cmd(command):
        """
        执行命令 & 不需要返回结果
        """
        os.system(command)


class Server:
    def __init__(self, deviceType):
        # 设备类型
        self.deviceType = deviceType
        # 执行命令的实例对象
        self.dos = DosCmd()
        # 查找设备列表（根据平台: ios/android）
        self.device_list = self.dos.execute_cmd_result(Util.devicetype.find_device)
        # self.write_file = WriteUserCommand()
        # 生成启动appium服务的命令
        self.start_list = self.create_command_list()

    def create_command_list(self):
        """
        生成cmd命令  # appium -p 4700 -bp 4701 -U deviceName
        :return: list
        """
        """
        """
        # 命令列表
        command_list = []
        # 端口类实例对象
        port = Port()
        # 生成端口列表,默认端口为4723
        appium_port_list = port.create_port_list(4723, self.device_list)
        # 生成和bootstrap通信的端口列表(仅针对Android)
        bootstrap_port_list = port.create_port_list(4900, self.device_list)
        if appium_port_list:
            for i in range(len(self.device_list)):
                # 命令行启动appium服务 设置端口号 [bp通信端口号] 设备名称 日志存放位置等
                command = 'appium -p '+str(appium_port_list[i])+' -U '+self.device_list[i] + \
                          ' --no-reset --local-timezone --log-timestamp ' \
                          '-g /Users/lanlanxiaohuan/Documents/appium.log ' \
                          '--device-name '+self.device_list[i] + \
                          ' --platform-version ' + \
                          self.dos.execute_cmd_result('adb shell getprop ro.build.version.release')[0]

                if self.deviceType == 'Android':
                    command += ('-bp'+str(bootstrap_port_list[i]))

                command_list.append(command)
            return command_list
        return {}

    def start_server(self, i):
        """
        根据命令开启服务
        :return: None
        """
        try:
            self.dos.execute_cmd(self.start_list[i])
        except Exception as e:
            logger.error(e)

    def kill_server(self):
        """
        杀掉已开启的node进程
        """
        self.dos.execute_cmd('killall node')

    def main(self):
        # 启动服务之前，先停掉已经启动且没有关闭的appiumfu服务(若有)
        self.kill_server()

        for i in range(len(self.start_list)):
            appium_start = threading.Thread(target=self.start_server, args=(i,))
            appium_start.start()

        # 命令行启动需要一定的是时间，所以休眠一段时间以保证后续操作可以正常执行
        time.sleep(10)


if __name__ == '__main__':
    port = Port()
    print(port.port_is_used('4724'))
    print(port.create_port_list(4723,['127.0.0.1:5555']))
