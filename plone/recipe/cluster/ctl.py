# -*- coding: utf-8 -*-
"""Control file
"""
import sys
import time
import os

from plone.recipe.cluster.daemon import Daemon

class Cluster(object):

    def __init__(self, stdin=sys.stdin, stdout=sys.stdout, 
                 stderr=sys.stderr, pidfile=None,
                 args=sys.argv[1:]):
        self.starts = self._extract_lines(args[0])
        self.stops = self._extract_lines(args[1])
        self.restarts = self._extract_lines(args[2])
        self.stdin = sys.stdin
        self.stdout = sys.stdout
        self.stderr = sys.stderr
        if pidfile is None:
            self.pidfile = 'cluster.pid'
        else:
            self.pidfile = pidfile
    
    def _extract_lines(self, line):
        return [arg.strip() for arg in line.split('\n')
                if arg.strip() != '']

    def _run_commands(self, pool):
        for command in pool:
            res = self._system(command)
            if not res:
                self.stderr.write('Command "%s" failed\n' % command)  
                self.stderr.flush()
                sys.exit(1)

    def before_start(self):
        """Runned before the daemon is starting"""
        self.stderr.write('Cluster is starting...\n')
        self.stderr.flush()
        self._run_commands(self.starts)
 
    def before_stop(self):
        """Runned before the daemon is stopped"""
        self.stderr.write('Cluster is going down...\n')
        self.stderr.flush()
        self._run_commands(self.stops)
 
    def before_restart(self):
        """Runned before the daemon is restarting"""
        self.stderr.write('Cluster is restarting...\n')
        self.stderr.flush()
        self._run_commands(self.restarts)
        
    def _system(self, command, input=''):
        self.stderr.write('Running %s\n' % command)
        self.stderr.flush()
        i, o, e = os.popen3(command)
        if input:
            i.write(input)
        i.close()
        result = o.read() + e.read()
        o.close()
        e.close()
        self.stderr.write(result)
        self.stderr.flush() 
        return True  # see how to return false in case of a problem

    def run(self):
        """Dameon code"""
        self.stderr.write('Cluster is alive...\n')
        self.stderr.flush()
        # now looping for ever
        while True:
            time.sleep(1)

def main(args=None):
    if args is None:
        args = ([], [], [])
    instance = Cluster(args=args)
    daemon = Daemon(instance)
    if len(sys.argv) != 2:
        print 'usage: %s start|stop|restart' % sys.argv[0]
        sys.exit(1)
    action = sys.argv[1]
    daemon.startstop(action)

