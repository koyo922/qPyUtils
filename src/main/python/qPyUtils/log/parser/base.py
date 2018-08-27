# coding=utf-8
"""
用于提取、分析各种日志文件，得到规整的DataFrame的工具模块
目前支持的日志格式有
- sn_log
- ts_log
- sn_validate

Authors: qianweishuo<qzy922@gmail.com>
Date:    2018/8/3 上午9:44
"""
import abc
from abc import abstractmethod
from datetime import datetime

import six
# noinspection PyCompatibility
from pathlib import Path
from typing import Union, Iterable, Text, Tuple

import pandas as pd
import pandas.errors
# noinspection PyPackageRequirements
from functional import seq

from qPyUtils import logger
from qPyUtils.log.writer import init_log
from qPyUtils.constant import INF
from qPyUtils.parallel import para

if six.PY3:
    # noinspection PyUnresolvedReferences
    from collections import ChainMap
else:
    from chainmap import ChainMap


@six.add_metaclass(abc.ABCMeta)
class BaseLogParser:
    """
    LogLoader基类，提供了统一的接口，供各个具体子类继承实现
    """
    LOG_TYPE = 'base'

    def __init__(self, take_files=INF, take_records=INF, date_range=None, parallel_args=None):
        # type: (int, int, Tuple[Union[datetime, Text], Union[datetime, Text]], dict) -> None
        """
        :param take_files: 只遍历一部分文件；加速单测
        :param take_records: 只遍历文件的头几条有效记录；加速单测
        :param date_range: 只处理该日期范围内的文件；可以直接传入datetime对象，也可以给str
        :type parallel_args: 用于指导并行逻辑的参数；默认10线程
        """
        self.take_files = take_files
        self.take_head = take_records
        self.date_range = None if date_range is None else \
            (seq(date_range)
             .map(lambda dt: dt if isinstance(dt, datetime) else datetime.strptime(dt, '%Y%m%d'))
             .to_list()
             )

        if parallel_args is None:
            parallel_args = dict()
        self.parallel_args = ChainMap(parallel_args,
                                      dict(n_jobs=10, front_num=1, pool_type='thread', desc=self.LOG_TYPE))

    def load_dir(self, base_path):
        # type: (Union[Path, Text]) -> pd.DataFrame
        """
        从指定的目录下，加载若干个符合条件的log文件，并将得到的结果pd.concat到一起
        :param base_path: 这一类log 所在的根路径
        :return:
        """
        if isinstance(base_path, six.string_types):
            base_path = Path(base_path)
        assert base_path is not None and base_path.is_dir()
        # 扫描得到所有待处理的文件Path
        # noinspection PyUnresolvedReferences
        logfile_paths = (seq(self.glob_files(base_path))
                         .filter(self.is_in_daterange)
                         .sorted()
                         .take(self.take_files)
                         .to_list()
                         )
        # 并行处理，得到各自对应的DataFrame
        dfs = para(logfile_paths, self.load_single_file,
                   **self.parallel_args)
        # 有些文件(例如 sn_vali)可能为空，需要安全的跳过
        non_empty_dfs = [df for df in dfs if not isinstance(df, pandas.errors.EmptyDataError)]
        if non_empty_dfs:
            return pd.concat(non_empty_dfs, ignore_index=True, sort=False)
        else:
            return pd.DataFrame()  # emtpy

    def load_single_file(self, path=None):
        # type: (Path) -> pd.DataFrame
        """
        将指定的单个log文件，转化成DataFrame
        :param path:
        :return:
        """
        assert path.is_file()
        # 下面的逻辑写得有点复杂，因为sn_log中\n没有转义，导致有些行需要join起来才是完整记录
        # noinspection PyUnresolvedReferences
        df = (seq(self.logfile2blocks(path))  # 抽取得到stream of block（就是str）
              .filter(None)  # 过滤掉空的block
              .map(self.block2records)
              .flatten()  # 每个block可能对应一至多条记录
              .take(self.take_head)  # 只取部分记录
              .to_pandas()
              )
        logger.info('---------- done loading[%s]: %s', self.LOG_TYPE, path.as_posix())
        return df

    def is_in_daterange(self, file_path):
        # type: (Path) -> bool
        """
        检测各种文件名所反映的日期，是否在允许的范围内;
        self.date_range is None 时，默认不限制日期

        :param file_path: 文件路径
        :return:
        """
        if self.date_range is None:
            return True
        file_date = self.filepath2date(file_path)
        return self.date_range[0] <= file_date <= self.date_range[1]

    def glob_files(self, base_path):
        # type: (Path) -> Iterable[Path]
        """ 从根路径下，查找所有log文件的Path """
        return seq(base_path.rglob('*.log'))

    def filepath2date(self, file_path):
        # type: (Path) -> datetime
        """ 每种具体子类对应的日志文件名风格都不同，需要各自的方法提取日期 """

    @abstractmethod
    def logfile2blocks(self, path):
        # type: (Path) -> Iterable[Text]
        """ 从每个log文件中抽取若干个block(对应于一条或一组方便一起提取的记录) """

    @abstractmethod
    def block2records(self, block):
        # type: (Text) -> Iterable[dict]
        """ 将每个block对应的str转化为多个records(如果是一个，就用tuple或者yield包裹) """
