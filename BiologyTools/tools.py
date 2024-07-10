import platform
import re
from typing import *
import colorama
import numpy
import pandas
import pymysql
from . import Record
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression


class Tools:
    @classmethod
    def is_path(cls, path: str):
        if platform.system() == 'Windows':
            pattern = r'^[A-Za-z]:\\(?:[^\\/:*?"<>|\r\n]+\\)*[^\\/:*?"<>|\r\n]*$'  # Windows路径
        elif platform.system() == 'Darwin':
            pattern = r'|^/(?:[^/\\:*?"<>|\r\n]+/)*[^/\\:*?"<>|\r\n]*$'  # Unix/Linux路径
        else:
            raise SystemError('什么鬼系统?')
        return bool(re.match(pattern, path))


class SQL:
    def __init__(self, host='192.168.1.4', user='cleverboss', password='clever3366', database='biology', port=3307):
        self.table = None
        self.connect = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port
        )
        self.cursor = self.connect.cursor()
        self.info = None
        self.keys = 'value,light,number,part,wrong'

    def tables(self, table: str):
        self.table = table

    def __enter__(self):
        self.__init__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cursor.close()
        self.connect.close()

    def __add__(self, other: list):
        self.cursor.execute(
            "INSERT INTO "
            + self.table
            + " (" + self.keys + ") VALUES ('" +
            str(other[0]) + "','" + str(other[1]) + "','" + str(other[2]) + "','" + str(other[3]) + "','" + str(other[4])
            + "');"
        )

    def __mul__(self, other: dict):
        if type(other) is not dict:
            raise TypeError(f'输入一个字典,不是{type(other)}')
        for k, v in other.items():
            self.cursor.execute(
                f"INSERT INTO {self.table} (value,light) VALUES ('{v}','{self.info}');"
            )

    @classmethod
    def increase(cls, table):
        def decorator(func):
            def wrapper(*args, **kwargs):
                with cls() as db:
                    db.tables(table)
                    # 调用原始函数
                    for i in func(*args, **kwargs):
                        print(i)

            return wrapper

        return decorator


class Output:
    @staticmethod
    def records(records: Record):
        """
        将结果输出为一个好看的格式
        :param records:
        :return:
        """
        print(
            f'{colorama.Style.BRIGHT}{colorama.Fore.WHITE}{colorama.Back.BLACK}{records[0][1]}-'
            f'{records[0][2]}{colorama.Fore.RESET}{colorama.Back.RESET}'
        )
        print(f"{colorama.Fore.GREEN} 分段 {colorama.Fore.BLUE}  速率  {colorama.Fore.RED} 错误 {colorama.Fore.RESET}")
        for i in records:
            print(
                f'{colorama.Fore.GREEN}{i[3]:-3d}  {colorama.Fore.BLUE}{i[0]:.4f} '
                f' {colorama.Fore.RED}{i[4]}{colorama.Fore.RESET}'
            )

    @staticmethod
    def moving_average(data, window_size):
        """
        计算移动平均
        :param data: 输入的数据列表
        :param window_size: 窗口大小
        :return: 平滑后的数据列表
        """
        if window_size > len(data):
            raise ValueError("窗口大小必须小于数据长度")
        # 使用列表推导式计算移动平均
        return [sum(data[i:i + window_size]) / window_size for i in range(len(data) - window_size + 1)]

    @classmethod
    def chart(cls, data: List[float]):
        """
        将数据绘制成图像并拟合趋势
        :param data:
        :return:
        """
        numpy.random.seed(0)  # 为了示例的可重复性
        # 创建坐标列表
        x = numpy.array([i for i in range(1, len(data) + 1)])  # 横坐标(分段)
        y = numpy.array(data)  # 枞坐标(速率)
        # 计算标准差
        std_dev = numpy.std(y)
        print(f"数据的标准差为: {std_dev}")
        # 将x和y的numpy数组转换为二维数组
        x_2d = x.reshape(-1, 1)
        y_2d = y.reshape(-1, 1)
        # 将数据转换为DataFrame
        df = pandas.DataFrame(data, columns=['Value'])
        # 计算滚动标准差，窗口大小为10
        window_size = 10
        rolling_std = df['Value'].rolling(window=window_size).std()
        # 使用线性回归模型拟合数据
        model = LinearRegression()
        model.fit(x_2d, y_2d)
        # 使用模型预测x值的y值，以绘制趋势线
        x_line = numpy.array([[0], [len(data)]])  # 选择一个x值的范围来绘制趋势线
        y_line = model.predict(x_line)
        # 生成平滑后的数据
        smooth_10 = cls.moving_average(data, 10)
        smooth_50 = cls.moving_average(data, 50)
        # 绘制数据点和趋势线
        # plt.scatter(x, y, color='blue', label='Data Point')
        plt.plot(x_line, y_line, color='red', linewidth=3, label='Trend Line')
        plt.plot(rolling_std.index, rolling_std, color='orange',
                 label='Std (Window Size: {})'.format(window_size))
        plt.plot([i for i in range(1, len(smooth_10) + 1)], smooth_10, color='green', linewidth=3, label='Smooth 10')
        plt.plot([i for i in range(1, len(smooth_50) + 1)], smooth_50, color='pink', linewidth=3, label='Smooth 50')
        # 添加标题和坐标轴标签
        """plt.title(f'{data[0][1]}-{data[0][2]}')
        plt.xlabel('分段')
        plt.ylabel('速率')"""
        plt.legend()
        plt.show()
