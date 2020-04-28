# -*- coding: utf-8 -*-
from Common.Excel import Reader, Writer
from DataDriven.KeyWords import HTTP, WEB
from DataDriven.APP import APP
from DataDriven.soapkey import SOAP
import inspect
import time
from Common import logger
from Common.statistics import Res
from Common.mail import Mail


def execute_case_and_send_mail(reader, writer):
    sheet_names = reader.get_sheets()
    for sheet in sheet_names:
        # 设置当前需要读的表格
        reader.set_sheet(sheet)
        # 设置当前需要写的表格
        writer.set_sheet(sheet)
        for row in range(len(reader.lines)):
            obj.row = row + 1
            run_case(obj, reader.lines[row])
            logger.info(reader.lines[row])

    # 切回到第一个sheet
    writer.set_active()
    # 写入用例结束时间
    writer.write(2, 5, time.strftime('%Y-%m-%d %H:%M:%S'))
    # 保存EXCEL文件
    writer.save_close()

    # 统计Excel用例文件 把相应数据替换到HTML模板中
    # 统计
    case_statistics = Res('./Case/result-%s.xlsx' % case_name)
    head_info = case_statistics.get_head()
    group = case_statistics.get_group()
    # 读取html模板
    html = open('./Common/module1.html').readline()
    # 替换总体统计信息
    for key in head_info.keys():
        html = html.replace(key, head_info[key])

    # 生成html一行内容
    allstr = ''
    for info in group:
        tr = '<tr><td width="100" height="28" align="center" bgcolor="#FFFFFF" style="border:1px solid #ccc;">分组信息</td><td width="80" height="28" align="center" bgcolor="#FFFFFF" style="border:1px solid #ccc;">用例总数</td><td width="80" align="center" bgcolor="#FFFFFF" style="border:1px solid #ccc;">通过数</td><td width="80" align="center" bgcolor="#FFFFFF" style="border:1px solid #ccc;">状态</td></tr>'
        tr = tr.replace('分组信息', str(info[0]))
        tr = tr.replace('用例总数', str(info[1]))
        tr = tr.replace('通过数', str(info[2]))
        tr = tr.replace('状态', str(info[3]))
        allstr += tr
    html = html.replace('mailbody', allstr)

    # 发送邮件
    mail = Mail('./Common/conf.ini')
    mail.send(html)


def run_case(obj, line):
    """
    执行每一行用例
    :param obj: 关键字对象
    :param line: 用例数据列表（row）
    :return:None
    """
    if len(line[0]) > 1 or len(line[1]) > 0:
        return
    else:
        # 获取关键字对应的函数名
        func = getattr(obj, line[3])
        # 获取关键字对象的参数名称和默认值 并转换为字符串类型
        params = inspect.getfullargspec(func).__str__()
        # 对字符串切割  获取自定义的参数列表
        params = params[params.find('args=')+5:params.find(', varargs')]
        # 转换为列表类型
        params = eval(params)
        # 移除掉不需要的参数(若有)
        if 'self' in params:
            params.remove('self')

        # 执行函数
        if len(params) == 0:
            func()
        elif len(params) == 1:
            func(line[4])
        elif len(params) == 2:
            func(line[4], line[5])
        elif len(params) == 3:
            func(line[4], line[5], line[6])
        else:
            print('暂不支持3个以上的参数')


if __name__ == '__main__':
    # 用例名称
    case_name = 'web-电商项目UI自动化测试用例'
    reader = Reader()
    reader.open_excel('./Case/%s.xlsx' % case_name)

    writer = Writer()
    writer.copy_open('./Case/%s.xlsx' % case_name, './Case/result-%s.xlsx' % case_name)
    # 写入用例执行开始时间
    writer.write(2, 4, time.strftime('%Y-%m-%d %H:%M:%S'))

    # ——————————————————————————用例类型为APP时 适配多线程————————————————————————
    # if case_type == 'APP':
    #     # 1.根据移动设备数量 开启相同数量的线程
    #     dos = DosCmd()
    #     device_list = dos.execute_cmd('adb devices')
    #     for i in range(len(device_list)):
    #         writer = Writer()
    #         writer.copy_open('./Case/%s.xlsx' % case_name, './Case/result-%s-%s.xlsx' % (device_list[i],case_name))
    #         # 写入用例执行开始时间
    #         writer.write(2, 4, time.strftime('%Y-%m-%d %H:%M:%S'))
    #         obj = APP(writer, i)
    #         app_thread = threading.Thread(target=execute_case_and_send_mail, args=(reader, writer,))
    #         app_thread.start()
    # 用例类型-- WEB/HTTP/APP等

    case_type = reader.lines[1][1]
    # 关键字实例对象
    obj = None
    if case_type == 'HTTP':
        # 执行http接口自动化
        obj = HTTP(writer)
    elif case_type == 'WEB':
        # 执行web UI自动化
        obj = WEB(writer)
    elif case_type == 'APP':
        # 执行APP自动化
        obj = APP(writer)
    elif case_type == 'SOAP':
        # 执行soap协议接口自动化
        obj = SOAP(writer)
    # 执行用例 写入执行结果 发送邮件
    execute_case_and_send_mail(reader, writer)