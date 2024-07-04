from itertools import cycle
from moviepy.editor import ImageSequenceClip
from ultralytics import YOLO
from .tools import SQL
from typing import List, Dict, Tuple, Union, Callable
from .define import Datas, Setups, Record, Result, Chloroplasts
from . import base_path
import colorama
import numpy
import av
import os
import glob
import math
import copy
import ruamel.yaml
import re


class Measure:
    def __init__(
            self, path: str, cache: str = os.path.join(base_path, 'cache/'), interval: int = 1,
            model: str = os.path.join(base_path, 'model/不错.pt'),
            output: Union[str, bool] = 'output.txt'
    ):
        self.value = 0
        self.lost = 0
        self.stream: Datas = []
        self.image_paths = []
        self.path = path
        self.cache = cache
        self.video = av.open(path)
        self.final: str = ''
        self.out = []
        self.interval = interval  # 两个保留的帧的间隔
        self.model = model  # yolo模型路径
        self.safe_path = output  # 输出的坐标文件路径

    def __enter__(self):
        self.split_flame(self.interval)
        self.generate_video()
        self.yolo(model=self.model)
        self.save(self.safe_path)
        return self.stream

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.clean()

    def split_flame(self, sampling_rate: int = 1):
        """
        将视频拆分成帧(可设置间隔)
        :param sampling_rate:
        :return:
        """
        if sampling_rate == 1:
            self.final = self.path
            return
        flames = self.video.decode(self.video.streams.video[0])
        # 逐帧遍历视频
        for index, frame in enumerate(flames):
            if index % sampling_rate == 0:
                image = frame.to_image()
                image_path = os.path.join(self.cache, f'frame-{index:04d}.jpg')
                self.image_paths.append(image_path)
                image.save(image_path)

    def generate_video(self, fps: int = 25):
        """
        将被拆分成帧的视频间隔取帧重新生成视频
        :param fps:
        :return:
        """
        if self.final == self.path:  # 说明视频无需处理
            return
        # 通过图片生成视频
        clip = ImageSequenceClip(self.image_paths, fps=fps)
        # 写入视频文件
        self.final = os.path.join(self.cache, 'processed.mp4')
        clip.write_videofile(self.final, codec='libx264')  # 写入视频文件，指定编码器为libx264

    def yolo(self, model: str):
        """
        通过YOLOv8识别叶绿体并导出坐标,格式见.define.Datas
        :param model:
        :return:
        """
        lost = 0
        output_ = []
        for i in YOLO(model).track(source=self.final, save=True, conf=0.05, iou=0.1):
            chloroplast = {}
            # 将ID与坐标转换成一个字典
            try:  # 看看有没有哪帧识别不到
                for id_ in i.boxes.id.tolist():
                    for post in i.boxes.xyxy.tolist():
                        chloroplast[int(id_)] = tuple(post)
            except AttributeError:  # 数据可以作废了
                lost += 1
            output_.append(chloroplast)
        self.stream = output_
        self.lost = lost

    def save(self, path: str):
        """
        保存识别的叶绿体坐标:
        格式:
            ID:X1-Y1-X2-Y2  ……
            ……
        例如:
            0:0.0-0.0-3.0-0.0  1:0.0-0.0-0.0-0.0
            0:1.0-1.0-4.0-0.0  1:1.0-1.0-1.0-1.0
            0:3.0-3.0-5.0-0.0  1:3.0-3.0-3.0-3.0
        :param path:
        :return:
        """
        with open(path, 'w', encoding='utf-8') as file:
            for flame in self.stream:
                for id_, block in flame.items():
                    file.write(f'{id_}:{block[0]}-{block[1]}-{block[2]}-{block[3]}  ')
                file.write('\n')

    def clean(self):
        """
        清除cache/内的所有文件(主要是视频预处理的图片和视频)
        :return:
        """
        # 使用glob模块列出目录下的所有文件
        for filename in glob.glob(os.path.join(self.cache, '*')):
            try:
                # 检查是否为文件（而不是目录）
                if os.path.isfile(filename) or os.path.islink(filename):
                    os.unlink(filename)  # 删除文件
            except Exception as e:
                print(f'{colorama.Fore.RED}删除错误{filename}: {e}{colorama.Fore.RESET}')


class Analise:
    def __init__(self, stream: Union[Datas, str]):
        self.chloroplasts: Chloroplasts = {}
        self.out = None
        if isinstance(stream, str):  # 说明需要加载
            self.load(stream)
        else:
            self.stream = stream

    def load(self, file):
        """
        加载保存在.txt文件中的叶绿体坐标数据
        :param file:
        :return:
        """
        with open(file, 'r') as datas:
            self.stream = []
            for flame in datas:
                posts = {}
                for post in flame.split('  '):
                    post_ = post.split(':')
                    if post_[0] == '\n':
                        continue
                    posts[int(post_[0])] = tuple([float(i) for i in post_[1].split('-')])
                self.stream.append(posts)

    @staticmethod
    def flame(datas: Datas, interval=1, reliable_num=10) -> Result:
        """
        识别叶绿体运动速率
        :param datas:
        :param interval:
        :param reliable_num:
        :return:
        """
        distances = []  # 存储每帧的平均距离
        standard_deviation = []  # 存储每帧方差
        reliable = True  # 结果是否可靠
        lost = 0
        for index, value in enumerate(zip(datas, datas[1:])):  # 逐帧遍历视频(数据)
            if index % interval != 0:  # 不是要处理的帧,跳过
                continue
            last, now = value  # 获得上一帧与当前帧
            distance = []  # 两帧之间每个叶绿体的移动距离
            for last_id, last_post in last.items():  # 遍历上一帧的所有叶绿体,通过ID对应到下一帧
                try:
                    distance.append(
                        math.sqrt((last_post[0] - now[last_id][0]) ** 2 + (last_post[1] - now[last_id][1]) ** 2)
                    )  # 计算两个叶绿体间的距离
                except KeyError:  # 上一帧的叶绿体在下一帧中没有识别到
                    lost += 1
            if len(distance) <= reliable_num:  # 结果不可靠,发出提示
                reliable = False
            distances.append(sum(distance) / len(distance))
            standard_deviation.append(numpy.std(numpy.array(distance)))
        return sum(distances) / len(distances), numpy.std(numpy.array(standard_deviation)), reliable, lost

    def flames(self, spread: int, interval: int) -> Record:
        """
        分段计算每帧间的速率与其它相关信息并输出至目标文件
        :param spread:
        :param interval:
        :return:
        """
        out = []
        part = len(self.stream) / spread
        part1 = cycle([math.floor(part), math.ceil(part)])
        part2 = copy.deepcopy(part1)
        for index, k in enumerate([self.stream[i:i + next(part2)] for i in range(0, len(self.stream), next(part1))]):
            try:
                result = self.flame(k, interval)
            except ZeroDivisionError:
                continue
            out.append([result[0]] + [index + 1, result[3]])
        self.out = out
        return out

    def chloroplast(self):
        """
        输出每个叶绿体的运动轨迹
        :return:
        """
        chloroplasts: Chloroplasts = {}
        for i, flame in enumerate(self.stream):  # 遍历每帧
            for id_, post in flame.items():
                try:
                    chloroplasts[id_][i] = post[:2]  # 这个叶绿体已被记录
                except KeyError:
                    chloroplasts[id_] = {i: post[:2]}  # 新叶绿体
        self.chloroplasts = chloroplasts
        return chloroplasts


class Exec:
    @classmethod
    def exec(cls, operations: Setups):
        datas: Union[str, Datas, None] = None
        if '识别' in operations:
            with Measure(path=operations['识别']['文件']) as posts:
                datas = posts
        if '分析' in operations:
            if '数据' in operations['分析']:
                datas = operations['分析']['数据']
            analise = Analise(datas)
            if '逐帧' in operations['分析']:
                return analise.flames(spread=operations['分析']['逐帧']['分段'], interval=operations['分析']['逐帧']['间隔'])
            if '追踪' in operations['分析']:
                return analise.chloroplast()

    @classmethod
    def yaml(cls, setup: str) -> Record:
        """
        通过.yaml配置文件运行程序
        :param setup:
        :return:
        """
        with open(setup, encoding='utf-8') as file:
            setups = ruamel.yaml.YAML(typ='safe').load(re.sub('<[^>]*>', '', file.read()))
        out = []
        for path in setups['文件']:
            get = cls.exec(operations=setups)
            if get is not None:
                out += get
        return out
