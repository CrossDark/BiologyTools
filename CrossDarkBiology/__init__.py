from itertools import cycle
from moviepy.editor import ImageSequenceClip
from ultralytics import YOLO
from .tools import SQL
from typing import List, Dict, Tuple, Union
import numpy
import av
import os
import glob
import math
import copy


class Video:
    Datas = List[Dict[int, Tuple[float, float, float, float]]]

    def __init__(self, path: str, cache: str):
        self.value = 0
        self.lost = 0
        self.stream: Video.Datas = []
        self.image_paths = []
        self.path = path
        self.cache = cache
        self.video = av.open(path)
        self.final: str = ''
        self.db: dict = {
            'LightTemperature': 'value,temperature,light,part,wrong',
            'LightIntensity': 'value,light,number,part,wrong'
        }

    def split_flame(self, sampling_rate: int = 1):  # 将视频拆分成帧(可设置间隔)
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
        if self.final == self.path:  # 说明视频无需处理
            return
        # 通过图片生成视频
        clip = ImageSequenceClip(self.image_paths, fps=fps)
        # 写入视频文件
        self.final = os.path.join(self.cache, 'processed.mp4')
        clip.write_videofile(self.final, codec='libx264')  # 写入视频文件，指定编码器为libx264

    def yolo(self, model: str):
        lost = 0
        output_ = []
        for i in YOLO(model).track(source=self.final, save=True, conf=0.05, iou=0.1):
            chloroplast = {}
            # 将ID与坐标转换成一个字典
            for id_ in i.boxes.id.tolist():
                for post in i.boxes.xyxy.tolist():
                    chloroplast[int(id_)] = tuple(post)
            output_.append(chloroplast)
        self.stream = output_
        self.lost = lost

    def output(self, path: str):
        with open(path, 'w', encoding='utf-8') as file:
            for flame in self.stream:
                for id_, block in flame.items():
                    file.write(f'{id_}:{block[0]}-{block[1]}-{block[2]}-{block[3]}  ')
                file.write('\n')

    def clean(self):
        # 使用glob模块列出目录下的所有文件
        for filename in glob.glob(os.path.join(self.cache, '*')):
            try:
                # 检查是否为文件（而不是目录）
                if os.path.isfile(filename) or os.path.islink(filename):
                    os.unlink(filename)  # 删除文件
            except Exception as e:
                print(f'Error deleting {filename}: {e}')

    @staticmethod
    def analise(datas: Datas, interval=1, reliable_num=10) -> Tuple[float, float, bool, int]:
        distances = []  # 存储每帧的平均距离
        standard_deviation = []  # 存储每帧方差
        reliable = True  # 结果是否可靠
        lost = 0
        for index, value in enumerate(zip(datas, datas[1:])):  # 逐帧遍历视频(数据)
            if index % interval != 0:  # 不是要处理的帧,跳过
                continue
            last, now = value
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

    def database(self, spread: int, interval: int, tables):
        xy = self.stream
        part = len(self.stream) / spread
        part1 = cycle([math.floor(part), math.ceil(part)])
        part2 = copy.deepcopy(part1)
        for index, k in enumerate([xy[i:i + next(part2)] for i in range(0, len(xy), next(part1))]):
            with SQL() as db:
                db.tables(tables)
                db.keys = self.db[tables]
                info = os.path.splitext(os.path.basename(self.path))[0].split('-')
                try:
                    result = self.analise(k, interval)
                except ZeroDivisionError:
                    continue
                db + ([str(result[0])]
                      + list(info[:2] if len(info) == 2 else info[:1] + [0])
                      + [index + 1, result[3]])

    def load(self, file):
        with open(file, 'r') as datas:
            for flame in datas:
                posts = {}
                for post in flame.split('  '):
                    post_ = post.split(':')
                    if post_[0] == '\n':
                        continue
                    posts[int(post_[0])] = tuple([float(i) for i in post_[1].split('-')])
                self.stream.append(posts)

    @classmethod
    def exec(cls, path, operation: Dict[str, Union[str, Dict[str, Union[int, str]], int]]):
        video = cls(path, 'cache/')
        if '预处理' in operation:
            video.split_flame(operation['预处理']['间隔'])
            video.generate_video()
            video.clean()
        if '模型' in operation:
            video.yolo(operation['模型'])
        if '输出' in operation:
            video.output(operation['输出'])
        if '加载' in operation:
            video.load(operation['加载'])
        if '数据库' in operation:
            video.database(operation['数据库']['分段'], operation['数据库']['分析间隔'], operation['数据库']['表格'])

    @classmethod
    def yaml(cls):
        pass
