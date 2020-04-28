import requests
import json
import jsonpath
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep
from Common import logger
from urllib.parse import quote
from selenium.webdriver.chrome.options import Options
import os
import traceback


class BASE:
    def __init__(self, writer):
        # 写入文件的对象
        self.writer = writer
        # 当前读取的行
        self.row = 0

    # 写入测试结果
    def __write_excel_res(self, status, msg):
        self.writer.write(self.row, 7, str(status))
        self.writer.write(self.row, 8, str(msg))


class HTTP:
    """
    接口自动化关键字库
    """
    def __init__(self, writer):
        # 基础host地址
        self.url = ''
        # 保存结果
        self.result = None
        # 保存json解析的结果
        self.json_res = {}
        # 当前会话
        self.session = requests.session()
        # 参数数据关系集合
        self.relations = {}
        # 写入文件的对象
        self.writer = writer
        # 当前需要写入的行
        self.row = 0

    def seturl(self, path):
        self.url = path
        self.__write_excel_res('PASS', '设置成功' + self.url)

    def get(self, path, param):
        """
        发送get请求
        @param: path 请求地址
        @param: param 请求参数
        """
        param = self.__get_relations(param)
        if path.startswith('http'):
            pass
        else:
            self.result = self.session.get(self.url+'/'+path + '?' + param)
        try:
            self.json_res = json.loads(self.result.text)
        except Exception as e:
            self.json_res = None
        self.__write_excel_res('PASS', self.json_res)

    def post(self, path, param):
        param = self.__get_relations(param)
        # url没有带主机地址时 加上
        if not path.startswith('http'):
            path = self.url+'/'+path
        # 接口返回信息 传递参数时对参数进行编码
        self.result = self.session.post(path, data=self.__get_data(param))
        try:
            self.json_res = json.loads(self.result.text)
        except Exception as e:
            self.json_res = None
        self.__write_excel_res('PASS', self.json_res)

    def post_encode(self, path, param):
        """
        发送请求时，对参数进行编码 主要为了适配reseful
        @param: path 请求路径
        @param: param 请求参数
        """
        param = self.__get_relations(param)
        # url没有带主机地址时 加上
        if not path.startswith('http'):
            path = self.url + '/' + path
        # 接口返回信息 传递参数时对参数进行编码
        self.result = self.session.post(path, data=quote(param))
        try:
            self.json_res = json.loads(self.result.text)
        except Exception as e:
            self.json_res = None
        self.__write_excel_res('PASS', self.json_res)

    def addheader(self, key, value):
        self.session.headers[key] = self.__get_relations(value)
        self.__write_excel_res('PASS', '添加成功' + str(self.session.headers[key]))

    def remove_header(self, key):
        """
        删除头；里面的某一个键值对
        :param key: 待删除的键
        :return: 无
        """
        try:
            self.session.headers.pop(key)
        except Exception as e:
            pass
        self.__write_excel_res('PASS', '删除成功' + str(self.session.headers))

    def save_json(self, key, value):
        # print(self.json_res)
        try:
            self.relations[value] = self.json_res[key]
        except:
            self.relations[value] = ''
        self.__write_excel_res('PASS', self.relations[value])

    def assertequals(self, jsonpath_key, respect_value):
        actual_value = None
        # 期望值带大括号的  需要先进行关联
        respect_value = self.__get_relations(str(respect_value))
        try:
            actual_value = str(jsonpath.jsonpath(self.json_res, jsonpath_key)[0])
        except Exception as e:
            print(e)
        if actual_value == respect_value:
            self.__write_excel_res('PASS', actual_value)
        else:
            self.__write_excel_res('FAIL', actual_value)

    def __get_relations(self, param):
        if param is None or param is '':
            return ''
        else:
            # 遍历已保存的参数字典
            # 传递进来的参数若含有参数字典的key
            # 把{key}替换为参数字典里以key为键的值
            for key in self.relations:
                param = param.replace('{'+key+'}', self.relations[key])
            return param

    @staticmethod
    def __get_data(params):
        """
        URL类型的参数字符串转换为字典
        @param:params 字符串
        @return: 转换后的字典
        """
        if params is None or params is '':
            # 如果是None或者空字符串 都返回None
            return None
        else:
            param_dic = {}
            # 用& 分割字符串
            param_list = params.split('&')
            for item in param_list:
                # 如果键值对里面有=号  =左边为键 右边为值
                if item.find('=') >= 0:
                    param_dic[item[0:item.find('=')]] = item[item.find('=')+1:]
                else:
                    # 如果键值对里面没有=号  值为None
                    param_dic[item] = None
            return param_dic

    def __write_excel_res(self, status, msg):
        self.writer.write(self.row, 7, str(status))
        self.writer.write(self.row, 8, str(msg))


class WEB:
    def __init__(self, writer):
        """
        初始化方法
        :param writer: 写入EXCEL文件类的实例对象
        """
        self.driver = None
        # 存储待比较的元素内容（一般为文本）
        self.result = {}
        # 写入文件的对象
        self.writer = writer
        # 当前需要写入的行
        self.row = 0

    def open_browser(self, browser_name):
        """
        根据浏览器名称打开对应的浏览器
        把浏览器对象复制给driver变量
        :param browser_name: 浏览器名称
        :return: None
        """
        try:
            # 如果浏览器名称为空时 默认使用谷歌浏览器
            if browser_name is None or browser_name is '' or browser_name == 'Chrome':
                # 加载浏览器缓存的用户数据  若用户已经登录过，再次打开浏览器可以跳过登录
                # opt = Options()
                # opt.add_argument('--user-data-dir=%s/Library/Application Support/Google/Chrome'
                #                  % os.environ['HOME'])
                # 获取浏览器操作对象
                self.driver = webdriver.Chrome(executable_path='./lib/chromedriver')
            # 火狐浏览器
            elif browser_name == 'Firefox':
                self.driver = webdriver.Firefox(executable_path='')
            # safari浏览器
            elif browser_name == 'Safari':
                self.driver = webdriver.Safari(executable_path='')
            else:
                print('暂不支持%s浏览器' % browser_name)
                self.__write_excel_res('FAIL', '不支持的浏览器')
                return
            # 添加隐式等待
            self.driver.implicitly_wait(10)

            self.__write_excel_res('PASS', '浏览器打开成功')
        except Exception as e:
            self.__write_excel_res('FAIL', traceback.format_exc())
            # 若浏览器打开异常 则程序不再执行
            exit(-1)

    def geturl(self, url):
        """
        打开待测试网站的主页
        :param url: host地址
        :return: None
        """
        try:
            self.driver.get(url)
            self.__write_excel_res('PASS', '打开'+url+'成功')
        except Exception as e:
            self.__write_excel_res('FAIL', traceback.format_exc())

    def input(self, location, text):
        """
        根据location定位到元素  输入文本
        :param location: 元素属性对应的值
        :param text: 待输入文本
        :return: None
        """
        try:
            element = self.__get_element(location)
            element.send_keys(text)
            self.__write_excel_res('PASS', '元素输入成功')
        except Exception as e:
            logger.exception(e)
            self.__write_excel_res('FAIL', traceback.format_exc())

    def click(self, location):
        """
        根据location定位到元素  点击
        :param location: 元素属性对应的值
        :return: None
        """
        try:
            element = self.__get_element(location)
            element.click()
            self.__write_excel_res('PASS', '元素点击成功')
        except Exception as e:
            logger.exception(e)
            self.__write_excel_res('FAIL', traceback.format_exc())

    def click_link(self, location):
        """
        点击a标签 针对selenium点击不了的情况 一般会发生在IE浏览器下
        (点击a标签 触发跳转)
        :param location: 元素属性对应的值
        :return: None
        """
        try:
            element = self.__get_element(location)
            # 获取a标签的跳转链接
            href = element.get_attrbute('href')
            self.driver.get(href)
            self.__write_excel_res('PASS', '元素点击成功')
        except Exception as e:
            logger.exception(e)
            self.__write_excel_res('FAIL', traceback.format_exc())

    def js_link(self, location):
        """
        点击a标签 针对selenium点击不了的情况 一般会发生在IE浏览器下
        (点击a标签 触发js事件)
        :param location: 元素属性对应的值
        :return: None
        """
        try:
            element = self.__get_element(location)
            self.driver.execute_script('$(arguments[0]).click()', element)
            self.__write_excel_res('PASS', '元素点击成功')
        except Exception as e:
            logger.exception(e)
            self.__write_excel_res('FAIL', traceback.format_exc())

    def moveto(self, location):
        """
        根据location定位到元素  鼠标悬停
        :param location: 元素属性对应的值
        :return: None
        """
        try:
            element = self.__get_element(location)
            # 借助ActionChains的实例方法   把鼠标移动到对应元素上 perform方法使前面的操作生效
            ActionChains(self.driver).move_to_element(element).perform()
            self.__write_excel_res('PASS', '鼠标悬停成功')
        except Exception as e:
            logger.exception(e)
            self.__write_excel_res('FAIL', traceback.format_exc())

    def get_text(self, attribute, location):
        """
        获取元素内的文本内容 并存储
        :param attribute: 元素属性名
        :param location: 元素属性对应的值
        :return: None
        """
        try:
            # 清空数据字典，防止对其他元素的比较造成影响
            self.result.clear()
            element = self.__get_element(location)
            self.result[attribute] = element.text
            print(self.result)
            self.__write_excel_res('PASS', '获取文本成功')
        except Exception as e:
            logger.exception(e)
            self.__write_excel_res('FAIL', traceback.format_exc())

    def get_title(self, attribute):
        """
        获取当前HTML页面的title
        :param attribute: 元素属性名
        :return: None
        """
        # 清空数据字典，防止对其他元素的比较造成影响
        self.result.clear()
        self.result[attribute] = self.driver.title
        self.__write_excel_res('PASS', '获取title成功')

    def assert_equals(self, key, respect_value):
        """
        比较实际结果与预期结果是否相等
        :param key:
        :param respect_value:
        :return:
        """
        actual_value = None
        try:
            print(key)
            actual_value = self.result[key]
        except Exception as e:
            logger.exception(e)
        if str(actual_value) == str(respect_value):
            self.__write_excel_res('PASS', actual_value)
        else:
            self.__write_excel_res('FAIL', actual_value)

    @staticmethod
    def compel_sleep(time):
        """
        该方法并未用到实例对象，所以写成静态方法，可以通过类或者实例对象调用
        强制等待  停止X秒后继续向下运行
        :param time: 等待时间
        :return: None
        """
        sleep(int(time))

    def wait(self, time):
        self.driver.implicitly_wait(time)
        self.__write_excel_res('PASS', '隐式等待成功')

    def switch_out(self):
        """
        返回最外层的html页面
        :return: None
        """
        try:
            self.driver.switch_to.default_content()
            self.__write_excel_res('PASS', '返回默认页面成功')
        except Exception as e:
            logger.exception(e)
            self.__write_excel_res('FAIL', traceback.format_exc())

    def switch_iframe(self, location):
        """
        切换iframe
        :return:None
        """
        try:
            element = self.__get_element(location)
            self.driver.switch_to.frame(element)
            self.__write_excel_res('PASS', '切换iframe成功')
        except Exception as e:
            logger.exception(e)
            self.__write_excel_res('FAIL', traceback.format_exc())

    def switch_window(self, index):
        """
        切换窗口
        :param index: 待切换的窗口在所有窗口句柄中的位置
        :return:None
        """
        try:
            self.driver.switch_to.window(self.driver.window_handles[int(index)])
            self.__write_excel_res('PASS', '切换窗口成功')
        except Exception as e:
            logger.exception(e)
            self.__write_excel_res('FAIL', traceback.format_exc())

    def execute_js(self, script):
        """
        执行js的脚本
        :param script: 脚本
        :return: None
        """
        try:
            # 执行js脚本前 最好休眠几秒 防止执行错误
            self.compel_sleep(2)
            # 同步方法，阻塞主线程直到js脚本执行完毕
            self.driver.execute_script(script)
            self.__write_excel_res('PASS', '执行js脚本成功')
        except Exception as e:
            logger.exception(e)
            self.__write_excel_res('FAIL', traceback.format_exc())

    def quit(self):
        """
        关闭浏览器
        :return: None
        """
        self.driver.quit()
        self.__write_excel_res('PASS', '退出浏览器成功')

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
        elif by == 'id':
            element = self.driver.find_element_by_id(local_name)
        elif by == 'classname':
            element = self.driver.find_element_by_class_name(local_name)
        return element

    def __write_excel_res(self, status, msg):
        self.writer.write(self.row, 7, str(status))
        self.writer.write(self.row, 8, str(msg))