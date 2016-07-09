#! /usr/bin/env python
# -*- coding: utf-8 -*-

# *************************************************************
#     Filename @  pps.py
#       Author @  Huoty
#  Create date @  2016-07-07 18:59:42
#  Description @  Linux 'ps -aux' command wrapper
# *************************************************************


class UnfoundException(Exception):
    pass


class CMDOutException(Exception):
    pass


class Process(object):
    def __init__(self, pid):
        self.pid   = int(pid)
        self.user  = None
        self.cpu   = None
        self.mem   = None
        self.vsz   = None
        self.rss   = None
        self.tty   = None
        self.stat  = None
        self.start = None
        self.time  = None
        self.cmd   = None
        self.update()

    def update(self):
        import os

        def find_exe(exe):
            for path in os.environ['PATH'].split(':'):
                if path and os.path.exists(os.path.join(path, exe)):
                    return os.path.join(path, exe)
            raise UnfoundException("executable %s file not found" % exe)

        ps_exe = find_exe("ps")
        grep_exe = find_exe("grep")

        ps_args = "-aux"  # List all the process
        grep_args = "-E '^.+ %d .+ [0-9]{1,2}\.[0-9]{1} .+$'"
                          # Filter process by pid

        cmd = " ".join([ps_exe, ps_args, "|", grep_exe, grep_args]) % self.pid
        with os.popen(cmd) as f:
            outs = [line.strip() for line in f.readlines()]
            ln = len(outs)
            if ln == 0:
                raise UnfoundException("process %d not found" % self.pid)
            if ln > 1:
                raise CMDOutException("abnormal output" + "".join(outs))
            pass

        pinfo = outs[0].strip().split(None, 10)
        if len(pinfo) != 11:
            raise CMDOutException("abnormal output", "".join(outs))

        convert_funcs = [str, int, float, float, int, int] + [str] * 5
        pinfo = [f(v) for v, f in zip(pinfo, convert_funcs)]

        self.user, self.pid, self.cpu, self.mem, self.vsz, self.rss, \
        self.tty, self.stat, self.start, self.time, self.cmd = pinfo

    def kill(self):
        from os import kill
        from signal import SIGTERM
        try:
            while 1:
                kill(self.pid, SIGTERM)
        except OSError:
            pass

    def to_dict(self):
        return {
            "pid": self.pid,
            "user": self.user,
            "cpu": self.cpu,
            "mem": self.mem,
            "vsz": self.vsz,
            "rss": self.rss,
            "tty": self.tty,
            "stat": self.stat,
            "start": self.start,
            "time": self.time,
            "cmd": self.cmd,
        }

    def __repr__(self):
        return "pps.Process(pid={}, cmd='{}')".format(self.pid, self.cmd)

    def __str__(self):
        from json import dumps
        return dumps(self.to_dict())


def processes():
    import os

    def find_exe(exe):
        for path in os.environ['PATH'].split(':'):
            if path and os.path.exists(os.path.join(path, exe)):
                return os.path.join(path, exe)
        raise UnfoundException("executable %s file not found" % exe)

    ps_exe = find_exe("ps")
    grep_exe = find_exe("grep")
    awk_exe = find_exe("awk")

    ps_args = "-aux"
    grep_args = "-v PID"
    awk_args = "'{print $2}'"

    cmd = " ".join([ps_exe, ps_args, "|", grep_exe, grep_args, "|", awk_exe, awk_args])
    with os.popen(cmd) as f:
        for pid in f:
            try:
                yield Process(int(pid))
            except Exception:
                continue
    pass

def mem_percent():
    with open("/proc/meminfo") as f:
        meminfo = {}
        for line in f:
            k, v = [x.strip() for x in line.split(":")]
            if k in ("MemTotal", "MemFree", "Buffers", "Cached"):
                v, u = v.split()
                if u == "kB":
                    v = float(v)
                elif u == "mB":
                    v = float(v) * 1024
                elif u == "gB":
                    v = float(v) * 1024 * 1024
                else:
                    raise UnfoundException("Undefined unit: %s"%u)

                meminfo[k] = v

    memfree = meminfo["MemFree"] + meminfo["Buffers"] + meminfo["Cached"]
    percent = (1 - memfree/meminfo["MemTotal"]) * 100
    return round(percent, 2)

def cpu_percent():
    def cputimes():
        with open("/proc/stat") as f:
            cpuinfo = [float(x) for x in f.readline().split()[1:]]
            total_cputime = sum(cpuinfo)
            idle_cputime = cpuinfo[3]

        return total_cputime, idle_cputime

    import time
    total_cputime_1, idle_cputime_1 = cputimes()
    time.sleep(0.1)
    total_cputime_2, idle_cputime_2 = cputimes()
    total_cputime = total_cputime_2 - total_cputime_1
    idle_cputime = idle_cputime_2 - idle_cputime_1
    percent = ((total_cputime - idle_cputime) / total_cputime) * 100
    return round(percent, 2)

__all__ = ["Process", "processes", "mem_percent", "cpu_percent"]


# Script starts from here

if __name__ == "__main__":
    pass
