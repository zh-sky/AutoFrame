from Common.Excel import Reader
"""
对用例的执行结果进行统计
"""


class Res:
    def __init__(self, result_path):
        self.status = False
        self.summary = {}
        self.read = Reader()
        self.read.open_excel(result_path)

    def get_head(self):
        """
        获取用例执行结果总的统计信息
        测试状态-status 通过率-pass_rate 开始时间-start_time 结束时间-end_time
        @param: result_path 用例文件路径
        @return: 字典
        """
        # 测试状态
        status = True
        # case通过数量
        pass_count = 0
        # case总数量
        total_count = 0
        # 读取开始、结束时间
        self.summary['start_time'] = self.read.lines[1][3]
        self.summary['end_time'] = self.read.lines[1][4]
        print(self.read.lines[1][3])
        sheet_names = self.read.get_sheets()
        # 外层--循环工作簿  内层--循环工作表
        for sheet in sheet_names:
            self.read.set_sheet(sheet)
            # 文件前三行非有效的用例信息  所以不再执行防止对后面数据造成干扰
            for i in range(2, len(self.read.lines)):
                line = self.read.lines[i]
                # 当该行为用例时：若‘执行结果‘为通过，pass_count数量+1 否则：测试状态置为false
                if len(line[2]) > 0:
                    if line[6] == 'PASS':
                        pass_count += 1
                    else:
                        status = False
                    total_count += 1
                else:
                    pass
        # 通过率
        pass_rate = pass_count / total_count
        # 参数格式化 {:.2%}四舍五入显示小数点后两位
        self.summary['pass_rate'] = '{:.2%}'.format(pass_rate)
        # 测试状态
        if status:
            self.summary['status'] = 'PASS'
        else:
            self.summary['status'] = 'FAIL'
        return self.summary

    def get_group(self):

        group_start = True
        group = []
        sheet_names = self.read.get_sheets()
        for sheet in sheet_names:
            self.read.set_sheet(sheet)
            # 重置组内信息和标记信息
            group_start = True
            self.__clear_info()
            # 第一行为头部信息  从第二行开始循环
            for i in range(1, len(self.read.lines)):
                line = self.read.lines[i]
                # 若该行的第一个元素(分组名)不为空  则该行为一组用例的开始,
                if len(line[0]) > 1:
                    # 若已经进入到了下一个分组  先保存上一个分组的信息
                    if not group_start:
                        self.__append_info()
                        group.append(self.group_info)
                        # 清空上一个分组的信息
                        self.__clear_info()
                    # 获取分组名
                    self.group_info.append(line[0])
                    group_start = False
                else:
                    # 第一行为空  检查该行的第3个元素判断该行 是否为用例行
                    if len(line[2]) > 1:
                        if line[6] == 'PASS':
                            self.group_pass += 1
                        else:
                            self.status = False
                        self.group_count += 1
            print(self.group_count, self.group_pass)
            self.__append_info()
            group.append(self.group_info)
        return group

    def __clear_info(self):
        self.group_info = []
        self.group_count = 0
        self.group_pass = 0
        self.status = True

    def __append_info(self):
        self.group_info.append(self.group_count)
        self.group_info.append(self.group_pass)
        if self.status:
            self.group_info.append('PASS')
        else:
            self.group_info.append('FAIL')









if __name__ == '__main__':
    res = Res('../Case/result-Excel接口用例.xlsx')
    res.get_res()
    print(res.get_group())


