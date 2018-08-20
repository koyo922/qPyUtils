#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 expandtab number

import json
import re
from datetime import datetime

from functional import seq
from pathlib import Path
from typing import Iterable

from qPyUtils.log.parser.base import BaseLogParser


class TsLogLoader(BaseLogParser):
    LOG_TYPE = 'ts_log'

    def glob_files(self, base_path):
        # type: (Path) -> Iterable[Path]
        return seq(base_path.rglob('ts.log.*'))

    def filepath2date(self, file_path):
        # type: (Path) -> datetime
        return datetime.strptime(file_path.suffix[1:], '%Y%m%d')

    def logfile2blocks(self, path):
        # type: (Path) -> Iterable[str]
        return seq.open(path.as_posix(), encoding='utf8')

    def block2records(self, block):
        # type: (Text) -> Iterable[dict]
        """
        将ts_log中的一行记录转换成dict
        :param block:
        :return:
        """
        mat = _REGEX_TS_LINE.fullmatch(block.rstrip())
        if mat is None:
            malformed_ts_line.append(block)
            yield None
            return

        log_time, brackets_str, _ = mat.groups()
        # e.g. ts_line = NOTICE: 06-30 23:58:01:  ts * 5140 .../speech-arch/ts-ex/ts_context.cpp:1042] [
        # logid:912070234][err:0][pkg_num:0][pdid:1001][appname:com.adamrocker.android.input.simeji][sample:16000][
        # client:8F668491-C598-5B7F-19AA-009D67D9B801][cpid:6572907471162369287][cplen:14804][wcpid:0][
        # workTime:4472][waitTime:475][proxy_ip:10.252.24.52:39861][prop:10005][client_ip:175.135.229.220][
        # sn:df7f97e7-178b-4e42-9aab-1d288846add6][total_decode_time:2068, last_pack:322][realtime_log:{
        # "app_version":"12.4.2","system_version":24,"os":"android","app":"com.dena.mirrativ","input_type":1,
        # "input_action":4}][TaskRecognition, timecost:4358, wait_finish:361, recv_audio:3264, connect: 4,
        # decoder:10.252.12.42:8001, failed: , recog_text:めぐにも入れちゃっていって][TaskWordCorrection, timecost:113, wc_err:0,
        # wc_svr: 10.252.21.33:8990, wc_result: めぐにも入れちゃっていって, proc_type: 2, post_data_len: 4416]
        # 使用_REGEX_TS_LINE正则，配出三段 _REGEX_TS_LINE = re.compile(r"""^NOTICE: ([-\d :]+?):  ts \* \d+ \S+ ((\[
        # .+?\])+)$""")
        #
        # 1. 开头的 "NOTICE: ([-\d :]+?)" 对应于 log_time
        # 2. 结尾的 "((\[.+?\])+)$" 是双重分组，外层对应 所有形如 "[...]" 的分组
        # 3. 内层对应第一个 形如 [...] 的分组

        record = dict(log_time=datetime.strptime(log_time, '%m-%d %H:%M:%S'))  # 直接使用第一个分组作为时间

        for m in _REGEX_BRACKET.finditer(brackets_str):  # 遍历得到每个 "[...]"
            key_path = []  # ts_log每行的记录结构比较复杂，为了达成扁平结构，要分级加前缀; 对于每个 [...] 重置一次
            bracket_content = m.group(1)  # 取出第一个分组，即 "[...]" 方括号里面的内容 "..."
            # e.g. [realtime_log:{"app_version":"12.4.2","system_version":24,"os":"android",
            # "app":"com.dena.mirrativ","input_type":1,"input_action":4}] [TaskRecognition, timecost:4358,
            # wait_finish:361, recv_audio:3264, connect: 4, decoder:10.252.12.42:8001, failed: ,
            # recog_text:めぐにも入れちゃっていって] [TaskWordCorrection, timecost:113, wc_err:0, wc_svr: 10.252.21.33:8990,
            # wc_result: めぐにも入れちゃっていって, proc_type: 2, post_data_len: 4416]

            parts = bracket_content.split(', ')  # 分组，e.g. ["TaskWordCorrection", "timecost:113", "wc_err:0", ... ]
            if parts[0].startswith('Task'):  # 如果首个part是 TaskRecognition / TaskWordCorrection
                key_path.append(parts[0])  # 加上Task前缀
                del parts[0]

            for part in parts:
                # part的结构可能也比较简单或者复杂, e.g.
                # timecost:4358
                # realtime_log:{"app_version":"12.4.2", ...}
                # wc_svr: 10.252.21.33:8990
                part_k, part_v = seq(part.split(':', maxsplit=1)).map(str.strip)

                key_path.append(part_k)  # --- 加part前缀
                if part_v.startswith('{'):
                    # e.g. {"app_version":"12.4.2", ...}
                    for k, v in json.loads(part_v).items():
                        key_path.append(k)  # ---- 加k前缀
                        record['@'.join(key_path)] = v
                        del key_path[-1]  # --- 移除&恢复k前缀
                else:
                    # e.g. "timecost:4358" 中的 "4358"部分
                    record['@'.join(key_path)] = part_v
                del key_path[-1]  # --- 移除&恢复part前缀

        for k in ('err', 'pkg_num', 'pdid', 'sample', 'cpid', 'cplen', 'workTime', 'waitTime', 'total_decode_time',
                  'last_pack',
                  'TaskRecognition@timecost', 'TaskRecognition@wait_finish',
                  'TaskRecognition@recv_audio', 'TaskRecognition@connect',
                  'TaskWordCorrection@timecost', 'TaskWordCorrection@wc_err',
                  'TaskWordCorrection@proc_type', 'TaskWordCorrection@post_data_len',):
            if k in record:
                record[k] = int(record[k])

        yield record


_REGEX_TS_LINE = re.compile(r"""^NOTICE: ([-\d :]+?): {2}ts \* \d+ \S+ ((\[.+?\])+)$""")
_REGEX_BRACKET = re.compile(r"""\[(.+?)\]""")
malformed_ts_line = []
