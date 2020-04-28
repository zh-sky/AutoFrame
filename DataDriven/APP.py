# -*- coding: utf-8 -*-
import time
from appium import webdriver
from Common import logger
import os
import traceback


class APP:
    def __init__(self, writer):
        """
        APP 关键字驱动 初始化方法
        @param writer Excel文件写操作的对象
        """
        self.driver = None
        # 存储待比较的元素内容（一般为文本）
        self.result = {}
        # 写入文件的对象
        self.writer = writer
        # 当前读取的行
        self.row = 0
        # 配置参数
        self.desired_capabilities = {}

    def app_config(self, caps):
        """
        初始化配置参数
        """
        try:
            self.desired_capabilities = eval(caps)
            self.__write_excel_res('PASS', '配置成功')
        except Exception as e:
            self.__write_excel_res('FAIL', '配置格式错误\n'+str(traceback.format_exc()))
            logger.exception(e)

    def start_appium(self):
        """
        启动appium
        """
        # 1.启动服务前，先kill掉已经启动的进程(若有)
        os.system('killall -9 node')
        # 2.以当天日期作为appium日志名称
        ct = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        log_name = os.path.join('/Users/lanlanxiaohuan/Documents/', ct + 'appium.log')
        try:
            os.system('appium -p 4723 --no-reset --local-timezone --log-timestamp -g ' + log_name + '&')
            self.__write_excel_res('PASS', 'appium服务已经开始运行')
        except Exception as e:
            logger.error('appium服务启动失败——>'+str(e))
            exit(-1)
        time.sleep(5)

    def link_appium(self):
        """
        连接appium 的http服务器
        """
        try:
            self.driver = webdriver.Remote("http://localhost:4723/wd/hub", self.desired_capabilities)
            self.__write_excel_res('PASS', '连接appium服务器成功')
        except Exception as e:
            logger.error("连接appium服务器失败-->"+str(e))
            exit(-1)

    def input(self, location, text):
        """
        元素操作--发送文本
        @param location 元素属性对应的值
        @param text 待输入文本
        """
        element = self.__get_element(location)
        element.send_keys(text)
        self.__write_excel_res('PASS', '元素文本输入成功')

    def click(self, location):
        """
        元素操作--点击
        @param location 元素属性对应的值
        """
        element = self.__get_element(location)
        element.click()
        self.__write_excel_res('PASS', '点击元素成功')

    def clear(self, location):
        """
        清空元素内的文本
        @param location 元素属性对应的值
        """
        element = self.__get_element(location)
        element.clear()
        self.__write_excel_res('PASS', '清空输入框成功')

    def key_event(self, code):
        """
        模拟安心键盘上的按钮
        @param: code 键盘按钮对应的值
        """
        self.driver.keyevent(code)

    def get_text(self, attribute, location):
        """
        获取元素内的文本内容 并存储
        :param attribute: 元素属性名
        :param location: 元素属性对应的值
        :return: None
        """
        # 清空数据字典，防止对其他元素的比较造成影响
        self.result.clear()
        element = self.__get_element(location)
        self.result[attribute] = element.text
        self.__write_excel_res('PASS', '获取文本成功')

    def assert_equals(self, key, respect_value):
        """
        比较实际结果与预期结果是否相等
        :param key:
        :param respect_value:
        :return:
        """
        actual_value = None
        try:
            actual_value = self.result[key]
        except Exception as e:
            print(e)
        if actual_value == respect_value:
            self.__write_excel_res('PASS', '实际结果符合预期结果')
        else:
            self.__write_excel_res('FAIL', '实际结果为'+actual_value)

    @staticmethod
    def compel_sleep(time):
        """
        该方法并未用到实例对象，所以写成静态方法，可以通过类或者实例对象调用
        强制等待  停止X秒后继续向下运行
        :param time: 等待时间
        :return: None
        """
        time.sleep(time)

    def wait(self, time):
        self.driver.implicitly_wait(time)

    def stop_appium(self):
        """
        退出APP
        :return: None
        """
        self.driver.quit()
        os.system('killall -9 node')
        self.__write_excel_res('PASS', 'appium服务停止运行')

    def __get_element(self, location):
        """
        定位元素在页面中的位置
        :param location:元素属性对应的值
        :return:None
        """
        # 元素定位方式
        local_list = location.split('>')
        # 元素地址名称
        by = local_list[0]
        # 需要查找的元素
        element = None
        local_name = local_list[1]
        if by == 'xpath':
            element = self.driver.find_element_by_xpath(local_name)
        elif by == 'accessibility_id':
            element = self.driver.find_element_by_accessibility_id(local_name)
        elif by == 'classname':
            element = self.driver.find_element_by_class_name(local_name)
        elif by == 'id':
            element = self.driver.find_element_by_id(local_name)
        return element

    def __write_excel_res(self, status, msg):
        """
        向测试用例文件写入用例执行结果
        @param status 用例执行状态
        @param msg 用例执行返回信息
        """
        self.writer.write(self.row, 7, str(status))
        self.writer.write(self.row, 8, str(msg))
