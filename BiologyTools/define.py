from typing import List, Dict, Tuple, Union
from numpy import typing as ntype
import numpy


class Info:
    """
    ^^^^^^^
    """
    @classmethod
    def print(cls):
        print(cls.__doc__)


Datas = List[Dict[int, Tuple[float, float, float, float]]]
Setups = Dict[str, Union[list, str, Dict[str, Union[int, str]], int]]
Record = List[List[Union[float, str, int]]]
Result = Tuple[float, float, bool, int]
Chloroplasts = Dict[int, Union[List[tuple], ntype.NDArray[ntype.NDArray[numpy.float64]]]]
