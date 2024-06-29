import pymysql


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


class Colors:
    # 前景色（文本颜色）
    HEADER = '\033[95m'  # 紫色
    OKBLUE = '\033[94m'  # 深蓝色
    OKGREEN = '\033[92m'  # 绿色
    OKYELLOW = '\033[93m'  # 黄色
    WARNING = '\033[93m'  # 也是黄色
    FAIL = '\033[91m'  # 红色
    ENDC = '\033[0m'  # 重置为默认色
    BOLD = '\033[1m'  # 加粗
    UNDERLINE = '\033[4m'  # 下划线

    # 前景色（更详细的颜色）
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'  # 紫色（洋红色）
    CYAN = '\033[36m'  # 青色（浅蓝色）
    WHITE = '\033[37m'

    # 背景色
    BGBLACK = '\033[40m'
    BGRED = '\033[41m'
    BGGREEN = '\033[42m'
    BGYELLOW = '\033[43m'
    BGBLUE = '\033[44m'
    BGMAGENTA = '\033[45m'  # 紫色（洋红色）背景
    BGCYAN = '\033[46m'  # 青色（浅蓝色）背景
    BGWHITE = '\033[47m'

    @classmethod
    def generate(cls, text, color):
        return f"{color}{text}{cls.ENDC}"

    @classmethod
    def print(cls, text, color):
        print(f"{color}{text}{cls.ENDC}")
