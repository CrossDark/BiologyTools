"""
生物信息工具
目前提供
"""
from typing import List, Dict, Tuple, Union
import pandas
import pathlib

__all__ = ['base_path', 'info', 'Datas', 'Setups', 'Record', 'Result', 'Chloroplasts']


base_path = pathlib.Path(__file__).resolve().parent
info = __doc__


Datas = List[Dict[int, Tuple[float, float, float, float]]]
Setups = Dict[str, Union[list, str, Dict[str, Union[int, str, Dict[str, Union[str, int]]]], int]]
Record = List[List[Union[float, str, int]]]
Result = Tuple[List[float], float, bool, int]
Chloroplasts = Dict[int, Union[pandas, Dict[int, Tuple[float, float]]]]
