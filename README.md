# qPyUtils
<!---
![Progress](http://progressed.io/bar/30?title=completed)
[![codebeat badge](https://codebeat.co/badges/a0171eb6-cda3-4c33-b5bc-fbba1affa373)](https://codebeat.co/projects/github-com-koyo922-qpyutils-master)
[![MIT Licence](https://badges.frapsoft.com/os/mit/mit.svg?v=103)](https://opensource.org/licenses/mit-license.php)
[![Join the chat at https://gitter.im/qPyUtils/Lobby](https://badges.gitter.im/qPyUtils/Lobby.svg)](https://gitter.im/qPyUtils/Lobby?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
-->
[![Build Status](https://travis-ci.org/koyo922/qPyUtils.svg?branch=master)](https://travis-ci.org/koyo922/qPyUtils)
[![codecov](https://codecov.io/gh/koyo922/qPyUtils/branch/master/graph/badge.svg)](https://codecov.io/gh/koyo922/qPyUtils)
[![PyPI version](https://badge.fury.io/py/qPyUtils.svg)](https://badge.fury.io/py/qPyUtils)
[![Python versions](https://img.shields.io/badge/python-2.7%20|%203.6-blue.svg)](https://www.python.org/downloads/release)
![platform](https://img.shields.io/badge/platform-mac%20os%20|%20linux-lightgrey.svg)

Python/Bash utils by qianws and his collections  
--- A util package for human (usability/readability is the first-concern)

## Getting Started

Basically, it's a warehouse of all the handy "wheels" I built/collected along my life as a Pythonista.

Just open and use, intuitively as the following examples:

### Debuging / Testing

- `start_in_thread(fn, *args, **kwargs)` single line to run a function in background thread
- `auto_unstub()` Automatically unstub mockito patch/mocks
- `mockify`a context protocol for modifying one or more objects

```python
from qPyUtils.debug import auto_unstub, mockify, start_in_thread

# ---------- start_in_thread
start_in_thread(function_to_start_a_web_server, host='localhost', port=8011)
time.sleep(0.1)  # waiting server to start, critical for Travis-CI
assert requests.get('http://localhost:8011/...') == ...

# ---------- auto_unstub
@auto_unstub  # `mockito.unstub()` is inserted into `tearDown()` logic
class TestInitLog(TestCase):
    def test_method(self):
        ... # code that may use mockito
        
    def test_method2(self):
        # ---------- mockify
        with mockify(sys.stderr) as sys.stderr:  # temporarily suppress stderr
            ...  # code that calls `sys.stderr.write()`
            verify(sys.stderr, atleast=1).write(Ellipsis)
```

### Log (or any text file) parser

Just inherent the `BaseLogParser` and implement some methods; 
the framework will do the heavy-lifting for you, including:
- filtering files by date
- using thread/process_pool for multiple loading files in parallel
- logging malformed lines
- recursively find and load all target files under specified path

```python
from qPyUtils.log.parser.base import BaseLogParser

# extend and implement some logic (please read full API documentation for complete info)
class MyLogLoader(BaseLogParser):
    LOG_TYPE = 'my_log'

    def glob_files(self, base_path):
        # type: (Path) -> Iterable[Path]
        return base_path.rglob('*.log')

    def logfile2blocks(self, path):
        # type: (Path) -> Iterable[Text]
        from qPyUtils.text import csplit  # python mimic for the `csplit` command in bash
        with path.open(mode='rt', encoding='utf8') as lines:
            return (''.join(block) for block in csplit(lines, re.compile(r'^{"version')))

    def block2records(self, block):
        # type: (Text) -> Iterable[dict]
        for rec in dirty_json_or_none(block)['records']:
            yield dict(**rec)
            
# now, use the magic power for free
my_log_loader = MyLogLoader()
my_log_loader.load_dir('./log')
my_log_loader.load_single_file('./log/my_log.2018-08-01.log')
```

### Standardized manner of initializing a logger

The easy & standardized usage of logger in Python 
```python
from qPyUtils.log.writer import init_log

# set logger_name to None or ''(as default), to use the root-logger
# the directories along the log_path will be automatically created if not yet exist
# a reasonable default format string, and daily log rotation is also provided.
logger = init_log(log_path='/home/my_name/my_project/log/my_log_file')

# set log_path to None or ''(as default)
# so that no file handlers are involved, only logs to console
logger = init_log()

# set `is_writing_console=False` to suppress console output
# not that for such case, you must provide a log_path; otherwise, no handlers will work
logger = init_log(is_writing_console=False, log_path='./log/my_log_file')
```

### `Timer` as a context manager

```python
import time
import qPyUtils.log.timer

# user-defined output_fn; feel free to try using `output_fn=logger.info` etc.
res = []
with qPyUtils.log.timer.Timer('Long task 中文', output_fn=res.append) as timer:
    with timer.child('large step'):
        time.sleep(1)
    for _ in range(5):
        with timer.child('small step'):
            time.sleep(0.5)
    print(res[0])
# ----- result:
# Long task 中文: 3.506s
#   5x small step: 2.503s (71%)
#   1x large step: 1.001s (28%)

# user-defined format_string
with qPyUtils.log.timer.Timer('Long task 中文', fmt='{name} --> {elapsed:.3f}') as timer:
    time.sleep(0.1)
# ----- result:
# Long task 中文 --> 0.101s
```

### Constant variables and functions

- `dummy_fn(*args, **kwargs)`: accepts anything but does nothing
- `identify_fn(arg)`: just reflect the `arg` passed in
- `T`: a `typing.TypeVar` for generic programming type-hints

### Parallel util

A light weight thread/process pool
- intuitive interface
- auto utilize multi CPU cores
- progress bar
- support `*args` / `*kwargs`
- Exception object returned in place of the corresponding task result

```python
from qPyUtils.parallel import para
import math

# simple usage; pass in tasks and function, get results
tasks = range(5)
fn = math.factorial
assert [1, 1, 2, 6, 24] == para(tasks, fn)

# you can still degrade to single thread --- sequential
# or even suppress the progress bar
para(tasks, fn, n_jobs=1, is_suppress_progressbar=True)

# support kwargs via the `use_kwargs` param
# CAUTION: `fn` should avoid appear in closure of the `para()` func; this is just for demo
fn2 = lambda x: math.factorial(x)
para([{'x': t} for t in tasks], fn2, use_kwargs=True)
```
### Streaming utils
Data streaming / Functional programming related utils.

```python
from qPyUtils.streaming import Repeat

# ---------- decorator over function
# turns a generator factory function into a sequence-like iterable;
# which could be iterated multiple epochs
@Repeat(n_epoch=2) # default to INF; parenthesis is necessary here
def my_gen():
    for i in range(3):
        yield i
        
# first 2 epochs as expected
# NOTE: now the name `my_gen` is the wrapped structure; no parenthesis here
assert (0, 1, 2) == tuple(my_gen)
assert (0, 1, 2) == tuple(my_gen)
# 3rd epoch is empty
assert tuple() == tuple(my_gen)

# ---------- decorator over method
class MyClazz(object):
    @Repeat(n_epoch=2)
    def my_method(self, a, b, prefix='>>>'):
        for i in range(a, b):
            yield '{}{}'.format(prefix, i)

obj = MyClazz()
my_gen = obj.my_method(0, 3, prefix=':') # call as normal

assert (':0', ':1', ':2') == tuple(my_gen)
assert (':0', ':1', ':2') == tuple(my_gen)
assert tuple() == tuple(my_gen) # emtpy for the 3rd epoch
```


### Text utils

```python
from qPyUtils.text import *

>>> assert is_none_or_empty('')
>>> assert is_none_or_empty(None)

# avoid python2's stupid handling logic for str/unicode
>>> dump_utf8({'name': u'中文'})  # use json.dumps() to avoid the ugly `\u....` / `\x..`
{"name": "中文"}

>>> lines = [
...     'line1',
...     '---- line2',
...     'line3',
...     'line4',
...     '---- line5',
...     'line6'
... ]
>>> pattern = r'----'
# mimic the `csplit` command in bash
# which groups text lines into blocks; from current line (inclusive) to next pattern-matching-line (exclusive)
# auto handles last buffer or empty input sequence
>>> list(csplit(lines, pattern))
[('line1',), ('---- line2', 'line3', 'line4'), ('---- line5', 'line6')]

# unify str/unicode/bytes in py2/py3 into Text type, using UTF8
>>> ensure_text(b'abc')
u'abc'
>>> ensure_text(b'中文')
u'中文'
>>> ensure_text(u'中文')
u'中文'
```

### Web utils

One-liner annotation turns your function into a RESTful service

```python
# ----- server side (CAUTION: UNICODE_LITERALS OR u'...' IS NECESSARY FOR NON-ASCII REQUESTS)
# encoding: utf-8
from __future__ import unicode_literals
from qPyUtils.web import RESTful

@RESTful(port=8004, route='/')
def introduce(name, friends):
    return '{} has friends: {}'.format(name.upper(), ', '.join(friends))
    
introduce.serve()
```

```bash
# ----- client side
# Unicode is automatically translated by UTF8
$ curl 'http://localhost:8004?name=koyo' -d 'friends=solar' -d 'friends=ape' -d 'friends=tutor' -d 'friends=斑马'
KOYO has friends: solar, ape, tutor, 斑马%
```

### System utils

A command line tool for forwarding port(s); Unicode Domain-Name is also supported.

```bash
# ----- ensure PYTHON_BIN is in the PATH; consider adding it to ~/.bashrc
PYTHON_BIN=$(python -c 'from distutils.sysconfig import EXEC_PREFIX as p; print(p + "/bin")')
export PATH=${PYTHON_BIN}:$PATH
portforward -H www.pku-hall.com -p 80 -l 8011

# ----- OR just simply call by `python -m ...` as an ad-hoc solution
python -m qPyUtils.system.portforward -H www.pku-hall.com -p 80 -l 8011
```

```commandline
Usage:
  portforward (-c <conf_path> | -H <host> -p <port> -l <local_port>)
  portforward -h | --help

Demo conf file:
<host>	<port>	<local_port>
www.pku-hall.com	80	8011
www.nic.ad.jp	80	8012
中国互联网络信息中心.中国	80	8013
```

A function simulating `rm -f <path>`
- support both dir and file
- ignore_errors, if not exist

```python
from qPyUtils.system.file_system import rm
rm('path/to/your/dir/or/file', ignore_errors=True)
```

### Prerequisites

- A *NIX OS
- python >= 2.7 or python >= 3.5

### Installing

For common package users,
it's as simple as typing `pip install qPyUtils` and having a cup of coffee, then it's done.

If you want to develop it, please follow the instructions below:

1. `git clone <url-of-this-repo> && cd qPyUtils/` , get the repo and cd inside
2. `pip install -r requirements-dev.txt` , install all the dependencies for developing
3. `pyb install_dependencies analyze -v` , using the powerful PyBuilder build-system to get the rest job done.


## Running the tests

1. following the installing procedure for developers as above
2. `pyb run_integration_tests -v`

## Deployment

Read the `.travis.yml` file for deployment settings, I use Travis-CI for PyPI/ReadTheDocs continuous delivery.

## Built With

* [PyBuilder](http://pybuilder.github.io) - The modern build tool for Python(just like maven/gradle for java)
* [Travis-CI](https://travis-ci.org) - The famous CI service vendor
* [Sphinx](http://www.sphinx-doc.org) - The de facto standard for docs the Python world

## Contributing

Bug, Issues, Doc, Pull Request ... --- Any contribution is welcomed! 
Feel free to get your hands dirty and help me improve it.

Most of the code is well-documented and carefully-tested;
It's easier than you might think to extend it.

## Authors

- **QIAN Weishuo** - *Initial work* - [Facebook](https://www.facebook.com/profile.php?id=100005178853657)

See also the list of [contributors](https://github.com/koyo922/qPyUtils/contributors) who participated in this project.

## License

This project is licensed under the MIT License 
[![MIT Licence](https://badges.frapsoft.com/os/mit/mit.svg?v=103)](https://opensource.org/licenses/mit-license.php)


## Acknowledgments

* `debug.auto_unstub()` https://gist.github.com/jnape/5767029
* `log.writer()` http://styleguide.baidu.com/style/python/index.html
* `text.dirty_json_or_none()` https://github.com/codecobblers/dirtyjson
* `log.timer.Timer()` https://github.com/mherrmann/timer-cm
