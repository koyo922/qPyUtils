#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 expandtab number
"""
pure python solution for port-forwarding
ref: https://github.com/vinodpandey/python-port-forward/blob/master/port-forward.py

Authors: qianweishuo<qzy922@gmail.com>
Date:    2018/9/2 下午4:15

Usage:
  portforward (-c <conf_path> | -H <host> -p <port> -l <local_port>)
  portforward -h | --help

Demo conf file:
<host>	<port>	<local_port>
www.pku-hall.com	80	8011
www.nic.ad.jp	80	8012
中国互联网络信息中心.中国	80	8013
"""
from __future__ import unicode_literals, print_function

import socket
import time
from io import open

import docopt
from typing import Text

from qPyUtils.debug import is_debugging, start_in_thread


class Route(object):
    def __init__(self, host, port, local_port):
        # type: (Text, int, int) -> None
        self.host = host
        self.port = port
        self.local_port = local_port


def forward(source, destination):
    """
    keep forwarding all packages from source to destination;
    till EOF, then shutdown both sockets
    :param source:
    :param destination:
    :return:
    """
    string = b' '
    while string:
        string = source.recv(10240)
        if string:
            destination.sendall(string)
        else:
            destination.shutdown(socket.SHUT_WR)
            try:
                source.shutdown(socket.SHUT_RD)
            except socket.error as ex:
                if ex.errno != 57:  # pragma: no cover ; socket.error: [Errno 57] Socket is not connected
                    raise


def serve(route):
    # type: (Route) -> None
    """
    keep forwarding ports according to the config of the route object
    :param route:
    :return:
    """
    try:
        dock_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        dock_socket.bind(('', route.local_port))
        dock_socket.listen(5)
        while True:
            client_socket = dock_socket.accept()[0]
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.connect((route.host, route.port))
            start_in_thread(forward, client_socket, server_socket)
            start_in_thread(forward, server_socket, client_socket)
    finally:
        start_in_thread(serve, route)  # pragma: no cover


def main(args_in=None):
    # type: (Text) -> None
    """
    logic entrance for this program
    :param args_in: the specified command line args; default to None, uses sys.argv[1:]
    :return:
    """
    args = docopt.docopt(__doc__, args_in)
    routes = []
    if args['-H']:
        routes = [Route(args['<host>'], int(args['<port>']), int(args['<local_port>']))]
    elif args['-c']:
        with open(args['<conf_path>'], 'rt', encoding='utf8') as f:
            for line in f:
                sp = line.strip().split('\t')
                routes.append(Route(host=sp[0], port=int(sp[1]), local_port=int(sp[2])))
    else:  # pragma: no cover ; should not reach hear; usage would be raised at docopt(...) above
        raise ValueError('^^^^^^^^^^ Neither commandline args nor config file specified.')

    # -------------------- start serving
    for r in routes:
        start_in_thread(serve, r)
    # wait for <ctrl-c>
    while True:
        time.sleep(60)


if __name__ == '__main__':  # pragma: no cover
    if is_debugging:
        main(['-H', '中国互联网络信息中心.中国', '-p', '80', '-l', '8004'])
    main()
