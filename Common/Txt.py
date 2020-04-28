class Txt:
    """
    对文件进行读写操作
    """
    def __init__(self, filepath, t='r', coding='utf8'):
        """
        初始化一个实例 打开文件
        @param: filepath 文件路径
        @param:t 打开文件方式 r->只读(默认)；w->只写；rw->读写
        @param:coding 文件编码 默认urf8
        """
        self.filepath = filepath
        # 存放读取结果
        self.data = []
        # 文件操作对象
        self.file = None
        if t == 'r':
            for line in open(filepath, encoding=coding):
                self.data.append(line)
            for i in range(len(self.data)):
                # 处理非法字符
                self.data[i] = self.data[i].encode('utf-8').decode('utf-8-sig')
                # 替换换行符
                self.data[i] = self.data[i].replace('\n', '')


if __name__ == '__main__':
    # data = open('../Common/conf.ini', encoding='utf8')
    # print(data.readline())
    for line in open('../Common/module1.html', encoding='utf8'):
        print(line)
    # print(with open('../Common/module1.html', encoding='utf8') as f .readline())