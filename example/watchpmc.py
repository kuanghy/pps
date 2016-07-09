#! /usr/bin/env python
# -*- coding: utf-8 -*-

# *************************************************************
#     Filename @  watchp.py
#       Author @  Huoty
#  Create date @  2016-07-08 16:09:03
#  Description @  Watch mem and cpu used of process
# *************************************************************

from __future__ import absolute_import, print_function, division

import os
import sys
import platform
import datetime
from time import sleep
from argparse import ArgumentParser
from configparser import ConfigParser
import logging

log = logging
logging.basicConfig(level=logging.INFO,
        format='%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(message)s')

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from pps import Process, mem_percent, cpu_percent
from daemon import Daemon


mail_template = \
"""<pre>
Process(%(pid)d) has been killed:

<strong>Proccess Pid:</strong>   %(pid)d
<strong>Proccess CMD:</strong>   %(cmd)s
<strong>Memory Usage:</strong>   %(mem)f
<strong>CPU Usage:</strong>      %(cpu)f
<strong>Proccess Owner:</strong> %(user)s

%(hostname)s %(system)s %(machine)s
%(dt)s
</pre>"""

def send_email(msg):
    from mailer import Mailer, Message
    mail_msg = Message(From="监听者<%s>"%(os.environ["MAIL_ADDR"]),
                    To=["loveqing2013@foxmail.com"],
                    charset="utf-8")
    mail_msg.Subject = "Watchpmc Report"
    mail_msg.Html = msg
    sender = Mailer(host="smtp.yeah.net", usr=os.environ["MAIL_ADDR"], pwd=os.environ["MAIL_PASS"])
    sender.send(mail_msg)

def watchpmc(pid_list, interval=1, mem_limit=50, cpu_limit=50):
    """Watch mem and cpu used of process"""
    p_list = []
    for pid in pid_list:
        try:
            p = Process(pid)
            p_list.append(p)
        except Exception as err:
            log.error(err)
            continue

    while 1:
        if len(p_list) == 0:
            log.info("Have no process need to watch, watch end.")
            break

        for p in p_list:
            try:
                p.update()
                total_mem_percent = mem_percent()
                total_cpu_percent = cpu_percent()

                condition1 = p.mem > mem_limit and total_mem_percent > 90
                condition2 = p.cpu > cpu_limit and total_cpu_percent > 90

                if condition1 or condition2:
                    p.kill()
                    info = p.to_dict()
                    info["dt"] = datetime.datetime.now()
                    info["hostname"] = platform.node()
                    info["system"] = platform.system()
                    info["machine"] = platform.machine()
                    mail_msg = mail_template % info
                    send_email(mail_msg)
                    log.info("kill: %s" % repr(p))
                    p_list.remove(p)
                    continue
            except Exception as err:
                log.error(err)
                p_list.remove(p)

        sleep(interval)

def main(conf="/etc/watchpmc.conf"):
    conf_file = os.path.abspath(conf)
    config = ConfigParser()
    config.read(conf_file)
    if not config.has_section("PID_LIST"):
        log.error("Invalid format of configuration file.")
        sys.exit(0)

    pid_list = [pid for _, pid in config["PID_LIST"].items()]
    if len(pid_list) == 0:
        log.error("No process is configured.")
        sys.exit(0)

    if config.has_section("PARAMETERS"):
        paras = config["PARAMETERS"]
        interval = paras.get("interval", 1)
        mem_limit = paras.get("mem_limit", 50)
        cpu_limit = paras.get("cpu_limit", 50)
        watchpmc(pid_list, float(interval), float(mem_limit), float(cpu_limit))
    else:
        watchpmc(pid_list)


# Script starts from here

if __name__ == "__main__":
    parser = ArgumentParser(description="Watch mem and cpu used of process")
    parser.add_argument("-c", "--config",
                        type=str,
                        default="/etc/watchpmc.conf",
                        help="Path to config file")
    parser.add_argument("-d", "--daemon",
                        type=str,
                        default=None,
                        choices=["start", "stop", "restart", "status"],
                        help="Daemon mode")

    options = parser.parse_args()
    conf_file = os.path.abspath(options.config)

    if options.daemon:
        config = ConfigParser()
        config.read(conf_file)
        pidfile = "/tmp/watchpmc.pid"
        logfile = "/tmp/watchpmc.log"
        if config.has_section("DAEMON_MODE"):
            pidfile = config["DAEMON_MODE"].get("pidfile", "/tmp/watchpmc.pid")
            logfile = config["DAEMON_MODE"].get("logfile", "/tmp/watchpmc.log")

        daemon = Daemon(pidfile, target=main, args=(conf_file,), logfile=logfile)

        {
            'start':   daemon.start,
            'stop':    daemon.stop,
            'restart': daemon.restart,
            'status':  daemon.status,
        }.get(options.daemon, lambda: None)()
    else:
        main(conf_file)
