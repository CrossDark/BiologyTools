# BiologyTools
提供一些~~目前只有一个~~生物信息学工具
## 叶绿体测速
基于YOLOv8编写的叶绿体胞质环流速率识别程序
### 使用方法
#### 直接识别单个文件
```python
from BiologyTools import CytoplasmicCirculationSpeedMeasure


CytoplasmicCirculationSpeedMeasure.exec(path='要识别的视频路径', operation={
    '预处理': {'间隔': 10},  # 按照设置的间隔缩短视频的帧数
    '模型': '/Volumes/home/Project/YoloV8/model/不错.pt',  # YOLO模型
    '加载': '/Users/crossdark/Downloads/test.txt',  #  加载识别好的叶绿体坐标数据
    '数据库': {  # 将识别到的速率录入数据库
        '分段': 1,
        '分析间隔': 1,
        '表格': 'LightIntensity'
    }})
```
#### 通过yaml
```python
from BiologyTools import CytoplasmicCirculationSpeedMeasure


CytoplasmicCirculationSpeedMeasure.yaml('yaml文件')
```
```yaml
文件:
  - '/Volumes/home/Experiment/细胞环流/数据/实验数据/光照强度/NO-6/2000lux-6.mp4'
预处理:
  间隔: 10
模型: '/Volumes/home/Project/YoloV8/model/不错.pt'
加载: '/Users/crossdark/Downloads/test.txt'
输出:
  分段: 1
  分析间隔: 1
```
