#! /usr/bin/env python
# -*- coding: utf-8 -*-

# *************************************************************
#     Filename @  daemon.py
#       Author @  Huoty
#  Create date @  2016-06-28 12:49:05
#  Description @  Python daemon
# *************************************************************

from __future__ import absolute_import, print_function, division

import os
import sys
import pwd
import grp
import fcntl
import atexit
import resource
from signal import SIGTERM


__all__ = ["Daemon"]

class Daemon(object):
    """
    A generic daemon class.

    Parameters:

        pidfile: path to the pidfile.
        target: custom function which will be executed after daemonization.
        args: the argument tuple for the target invocation.
        kwargs: a dictionary of keyword arguments for the target invocation.
        logfile: use this file instead of stdout and stderr, default is /dev/null.
        user: drop privileges to this user if provided.
        group: drop privileges to this group if provided.
        chdir: change working directory if provided or /
    """
    def __init__(self, pidfile, target, args=(), kwargs={}, logfile=os.devnull,
                 user=None, group=None, chdir="/"):
        self.pidfile = os.path.abspath(pidfile)
        self.target  = target
        self.args    = args
        self.kwargs  = kwargs
        self.logfile   = os.path.abspath(logfile)
        self.user    = user
        self.group   = group
        self.chdir   = chdir

    def daemonize(self):
        """
        do the UNIX double-fork magic, see Stevens' "Advanced
        Programming in the UNIX Environment" for details (ISBN 0201563177)
        """
        try:
            pid = os.fork()
            if pid > 0:
                # exit first parent
                sys.exit(0)
        except OSError as e:
            sys.stderr.write("fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)

        ## Decouple from parent environment
        # setsid puts the process in a new parent group and detaches its controlling terminal.
        os.setsid()

        # Set umask to default to safe file permissions when running as a root daemon.
        # 022 is an octal number which we are typing as 0o022 for Python3 compatibility.
        os.umask(0o022)

        # Change to a known directory. If this isn't done, starting a daemon in a subdirectory
        # that needs to be deleted results in "directory busy" errors.
        os.chdir(self.chdir)

        # Change gid
        if self.group:
            try:
                gid = grp.getgrnam(self.group).gr_gid
                os.setgid(gid)
            except KeyError:
                sys.stderr.write("Group {0} not found".format(self.group))
                sys.exit(1)
            except OSError as e:
                sys.stderr.write("Unable to change gid: {0}\n".format(e.strerror))
                sys.exit(1)

        # Change uid
        if self.user:
            try:
                uid = pwd.getpwnam(self.user).pw_uid
                os.setuid(uid)
            except KeyError:
                sys.stderr.write("User {0} not found.".format(self.user))
                sys.exit(1)
            except OSError as e:
                sys.stderr.write("Unable to change uid: {0}\n".format(e.strerror))
                sys.exit(1)

        # do second fork
        try:
            pid = os.fork()
            if pid > 0:
                # exit from second parent
                sys.exit(0)
        except OSError as e:
            sys.stderr.write("fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)

        # Close all file descriptors
        for fd in range(3, resource.getrlimit(resource.RLIMIT_NOFILE)[0]):
            try:
                os.close(fd)
            except OSError:
                pass

        # redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        si = open(os.devnull, 'r')
        so = open(self.logfile, 'a')
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(so.fileno(), sys.stderr.fileno())
        sys.stdout = sys.stderr  # because stdout is buffered

        # lock logfile
        if self.logfile != "/dev/null":
            fcntl.flock(so, fcntl.LOCK_EX)

        # write pidfile
        atexit.register(self.delpid)
        pid = str(os.getpid())
        pf = open(self.pidfile, 'w')
        pf.write("%s\n" % pid)
        pf.close()

    def delpid(self):
        if os.path.isfile(self.pidfile):
            os.remove(self.pidfile)
        pass

    def start(self):
        """
        Start the daemon
        """
        # Check for a pidfile to see if the daemon already runs
        if os.path.isfile(self.pidfile):
            message = "pidfile %s already exist. Daemon already running?\n"
            sys.stderr.write(message % self.pidfile)
            sys.exit(1)

        # Check for a pidfile to write access
        try:
            open(self.pidfile, 'w').close()
            self.delpid()
        except IOError as err:
            sys.stderr.write(str(err) + '\n')
            sys.exit(1)

        # Start the daemon
        self.daemonize()
        self.target(*self.args, **self.kwargs)

    def stop(self):
        """
        Stop the daemon
        """
        # Get the pid from the pidfile
        try:
            pf = open(self.pidfile, 'r')
            pid = int(pf.readline().strip())
            pf.close()
        except ValueError:
            message = "The contents of the pidfile(%s) is wrong!\n"
            sys.stderr.write(message % self.pidfile)
            sys.exit(1)
        except IOError:
            pid = None

        if not pid:
            message = "pidfile %s does not exist. Daemon not running?\n"
            sys.stderr.write(message % self.pidfile)
            return  # not an error in a restart

        # Try killing the daemon process
        try:
            os.kill(pid, SIGTERM)
        except OSError as err:
            message = "Failed to stop process(%d): %d (%s)\n"
            sys.stderr.write(message % (pid, err.errno, err.strerror))

        self.delpid()

    def restart(self):
        """
        Restart the daemon
        """
        self.stop()
        self.start()

    def status(self):
        """
        ps daemon status
        """
        try:
            pf = open(self.pidfile, 'r')
            pid = int(pf.readline().strip())
            pf.close()
        except ValueError:
            message = "The contents of the pidfile(%s) is wrong!\n"
            sys.stderr.write(message % self.pidfile)
            sys.exit(1)
        except IOError:
            message = "pidfile %s does not exist. Daemon not running?\n"
            sys.stderr.write(message % self.pidfile)
            sys.exit(1)

        cmd = "ps -aux | grep -E '^.+ %d .+ [0-9]{1,2}\.[0-9]{1} .+$'" % pid
        outs = os.popen(cmd).readlines()
        if outs:
            sys.stdout.write("".join(outs))
        else:
            message = "Failed to show status: No such process(%d)\n"
            sys.stderr.write(message % pid)


# Script starts from here

if __name__ == "__main__":
    import time
    import argparse
    import logging

    logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(levelname)s %(message)s')

    def demodaemon(*args, **kwargs):
        while 1:
            time.sleep(6)
            logging.info('daemon runing')
            print("test print")
            sys.stdout.write("test stdout redirect\n")
            sys.stderr.write("test stderr redirect\n")
            print("get args:", str(args))
            print("get kwargs:", str(kwargs))
        pass

    parser = argparse.ArgumentParser(description="A demo app of daemonize")
    parser.add_argument("-d", "--daemon",
                        type=str,
                        default=None,
                        choices=["start", "stop", "restart", "status"],
                        help="Daemon mode")

    options = parser.parse_args()

    daemon = Daemon("/tmp/demodaemon.pid", target=demodaemon, args=(1, 2, 3, 4, 5),
                    kwargs={'a': 1, 'b': 2, 'c':3}, logfile="/tmp/demodaemon.log",
                    user="kong", group="kong")

    if options.daemon:
        {
            'start':   daemon.start,
            'stop':    daemon.stop,
            'restart': daemon.restart,
            'status':  daemon.status,
        }.get(options.daemon, lambda: None)()
    else:
        demodaemon()
