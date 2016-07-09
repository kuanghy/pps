#! /usr/bin/env python
# -*- coding: utf-8 -*-

# *************************************************************
#     Filename @  test_pps.py
#       Author @  Huoty
#  Create date @  2016-07-04 19:44:05
#  Description @  test pps module by pytest
# *************************************************************

from __future__ import print_function

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from pps import *

def test_mem_percent():
    print(mem_percent())

def test_cpu_percent():
    print(cpu_percent())

def test_class_process():
    p = Process(4264)
    print(p)
    print(p.to_dict())

def test_processes():
    for p in processes():
        print(p)

    print(list(processes()))
