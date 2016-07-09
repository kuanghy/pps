#! /usr/bin/env python
# -*- coding: utf-8 -*-

# *************************************************************
#     Filename @  test_case.py
#       Author @  Huoty
#  Create date @  2016-07-09 11:17:46
#  Description @  test by pytest
# *************************************************************

from __future__ import absolute_import, print_function, division

import random

from watchpmc import *

def test_send_email():
    info = {"pid": 123, "cmd": "test cmd", "mem": random.random(), \
        "cpu": random.random(), "user": "huoty", "dt": datetime.datetime.now(), \
        "hostname": platform.node(), "system": platform.system(), \
        "machine": platform.machine()}
    send_email(mail_template % info)

def test_watchpmc():
    import multiprocessing

    def resource_consume():
        lst = []
        while 1:
            lst += [random.uniform(0, 10000000) for x in range(10000000)]
            lst.sort()
        pass

    consume = multiprocessing.Process(target=resource_consume)
    consume.start()

    test_p1 = multiprocessing.Process(target=watchpmc,args=([consume.pid],), kwargs={"mem_limit": 0})
    test_p2 = multiprocessing.Process(target=watchpmc,args=([consume.pid],), kwargs={"cpu_limit": 0})
    test_p1.start()
    test_p2.start()

    consume.join()
    test_p1.join()
    test_p2.join()
