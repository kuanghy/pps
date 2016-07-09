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
        "cpu": random.random(), "user": "huoty", "dt": datetime.datetime.now()}
    send_email(mail_template % info)

def test_watchpmc():
    pass
