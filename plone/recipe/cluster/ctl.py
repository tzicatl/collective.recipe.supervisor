# -*- coding: utf-8 -*-
"""Control file
"""
import sys
import time
import os
from pty import fork as forkpty
from subprocess import Popen, PIPE
from signal import SIGTERM

from plone.recipe.cluster.daemon import Daemon

class Cluster(object):

    def __init__(self, stdin=sys.stdin, stdout=sys.stdout, 
                 stderr=sys.stderr, pidfile=None,
                 args=sys.argv[1:], foreground=True):
        self.starts = self._extract_lines(args[0])
        self.stops = self._extract_lines(args[1])
        self.restarts = self._extract_lines(args[2])
        self.stdin = sys.stdin
        self.stdout = sys.stdout
        self.stderr = sys.stderr
        self.foreground = foreground
        if pidfile is None:
            self.pidfile = 'cluster.pid'
        else:
            self.pidfile = pidfile
    
    def _extract_lines(self, line):
        return [arg.strip() for arg in line.split('\n')
                if arg.strip() != '']

    def _kill(self, pid):
        #self.stderr.write('Stopping PID %d\n' % pid) 
        try:
            while 1:
                os.kill(pid, SIGTERM)
                time.sleep(1)
            sys.stderr.write("\n%s\n" % self.stopmsg % pid)
            sys.stderr.flush()
        except OSError, err:
            err = str(err)
            if not err.find("No such process") > 0:
                sys.stderr.write('%s\n' % err)
                sys.stderr.flush()
                return False
        return True

    def _run_commands(self, pool):
        def _run(command):
            if command.startswith('pid:'):
                pid = command.split(':')[-1]
                if os.path.exists(pid):
                    pidfile = pid
                    pid = open(pidfile).read().strip()
                    try:
                        pid = int(pid)
                    except ValueError:
                        pass
                    else:
                        if self._kill(pid):
                            try:
                                os.remove(pidfile)
                            except OSError:
                                pass # might be removed already
                else:
                    try:
                        pid = int(pid)
                    except ValueError:
                        pass
                    else:
                        self._kill(pid)
                return None

            if command.startswith('background:'):
                command = command.replace('background:', '')
                background = True
            else:
                background = False
            pid = self._system(command, background)
            if not pid:
                self.stderr.write('Command "%s" failed\n' % command)  
                self.stderr.flush()
                sys.exit(1)
            return pid
        res = [_run(command) for command in pool]
        return [pid for pid in res if pid is not None]
    
    def before_start(self):
        """Runned before the daemon is starting.

        Returns a list of PIDs"""
        self.stderr.write('Cluster is starting...\n')
        self.stderr.flush()
        return self._run_commands(self.starts)
 
    def before_stop(self):
        """Runned before the daemon is stopped.

        Returns a list of PIDs"""
        self.stderr.write('Cluster is going down...\n')
        self.stderr.flush()
        return self._run_commands(self.stops)
 
    def before_restart(self):
        """Runned before the daemon is restarting.

        Returns a list of PIDs"""
        self.stderr.write('Cluster is restarting...\n')
        self.stderr.flush()
        return self._run_commands(self.restarts)
        
    def _system(self, command, background=False):
                
        # foreground
        if not background:
            self.stderr.write('Running %s\n' % command)
            self.stderr.flush()

            p = Popen([command], shell=True, stderr=PIPE,
                  stdin=PIPE, stdout=PIPE, close_fds=True)
 
            result = p.stdout.read()
            errors =  p.stderr.read()
            self.stderr.write(result + errors)
            self.stderr.flush() 
            child_pid = p.pid
        else:
            self.stderr.write('Running in background %s\n' % command)  
            self.stderr.flush()
            # background, let's fork
            curdir = os.curdir
            child_pid, fd = forkpty()
            if child_pid == 0:
                os.chdir(curdir)
                p = Popen([command], shell=True)
                # returning the pid to the master
                sys.stderr.write('%d' % p.pid)
                sys.stderr.write('#')
                # stay here
                os.waitpid(p.pid, 0)
                # bye
                sys.exit(0)
            else: 
                # XXX see how to get child
                # output
                sub_pid = ''
                n = os.read(fd, 1)
                while n in '0123456789':
                    sub_pid += n
                    n = os.read(fd, 1) 
                sub_pid = int(sub_pid)
                self.stderr.write('Background pid is %d\n' % child_pid)
                self.stderr.write('Background subpid is %d\n' % sub_pid)
        return child_pid  # see how to return false in case of a problem

    def run(self):
        """Dameon code"""
        self.stderr.write('Cluster is alive...\n')
        self.stderr.flush()
        if not self.foreground:
            return
        # now looping for ever
        while True:
            time.sleep(1)

def main(args=None):
    if args is None:
        args = ([], [], [], False, 'cluster.pid')
    args = args[:3]
    foreground = not args[-2]
    pidfile = args[-1]
    instance = Cluster(args=args, foreground=foreground, pidfile=pidfile)
    daemon = Daemon(instance)
    if len(sys.argv) != 2:
        print 'usage: %s start|stop|restart|status' % sys.argv[0]
        sys.exit(1)
    action = sys.argv[1]
    daemon.startstop(action)

