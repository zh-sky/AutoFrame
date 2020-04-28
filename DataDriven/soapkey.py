from suds.client import Client
import json
import jsonpath
import traceback


class SOAP:
    """
    接口自动化关键字库
    """
    def __init__(self, writer):

        # 保存结果
        self.result = None
        # 保存json解析的结果
        self.json_res = {}
        # 对webservice访问的代理
        self.client = None
        # 参数数据关系集合
        self.relations = {}
        # 写入文件的对象
        self.writer = writer
        # 当前需要写入的行
        self.row = 0
        # 请求头集合
        self.headers = {}

    def setwsdl(self, url):
        """
        设置请求地址
        @param: wsdl的url地址
        """
        self.wsdl = url
        self.client = Client(url)
        self.__write_excel_res('PASS', '设置成功' + url)

    def callmethod(self, inter_name, param):
        """
        发送请求
        @param: inter_name 接口名字
        @param: param 请求参数
        """
        param = self.__get_relations(param)
        param = self.__get_data(param)
        try:
            if param is None:
                # 不传递参数
                self.result = self.client.service.__getattr__(inter_name)()
            else:
                self.result = self.client.service.__getattr__(inter_name)(*param)
        except Exception as e:
            # 获取报错的堆栈信息
            self.result = str(traceback.format_exc())
        try:
            self.json_res = json.loads(self.result)
        except Exception as e:
            self.json_res = self.result
        self.__write_excel_res('PASS', self.json_res)

    def addheader(self, key, value):
        """
        添加请求头
        @param: key 请求头参数key
        @param: value 请求头参数key对应的值
        """
        # 去关系集合里取value对应的值
        value = self.__get_relations(value)
        self.headers[key] = value
        self.client = Client(self.wsdl, headers=self.headers)
        self.__write_excel_res('PASS', '添加成功' + str(self.headers))

    def removeheader(self, key):
        """
        删除头；里面的某一个键值对
        :param key: 待删除的键
        :return: 无
        """
        try:
            self.headers.pop(key)
        except Exception as e:
            pass
        self.client = Client(self.wsdl, headers=self.headers)
        self.__write_excel_res('PASS', '删除成功' + str(self.headers))

    def savejson(self, key, value):
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
        把以、号连接的参数字符串转换为列表
        @param:params 字符串
        @return: 转换后的列表
        """
        if params is None or params is '':
            # 如果是None或者空字符串 都返回None
            return None
        else:
            return params.split('、')

    def __write_excel_res(self, status, msg):
        self.writer.write(self.row, 7, str(status))
        self.writer.write(self.row, 8, str(msg))