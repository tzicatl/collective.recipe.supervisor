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
        self.args = args
        self.stdin = sys.stdin
        self.stdout = sys.stdout
        self.stderr = sys.stderr
        if pidfile is None:
            self.pidfile = 'cluster.pid'
        else:
            self.pidfile = pidfile

    def before_stop(self):
        """Runned before the daemon is stopped"""
        self.stderr.write('Cluster is going down...\n')
        self.stderr.flush()
        # running subscripts
        args = [arg.strip() for arg in self.args[1].split('\n')]
        for command in args:
            res = self._system(command)
            if not res:
                self.stderr.write('Command "%s" failed\n' % command)  
                self.stderr.flush()
                sys.exit(1)

    def _system(self, command, input=''):
        self.stderr.write('Running %s\n' % command)
        self.stderr.flush()
        #i, o, e = os.popen3(command)
        #if input:
        #    i.write(input)
        #i.close()
        #result = o.read() + e.read()
        #o.close()
        #e.close()
        res = os.system(command)
        return res == 0

    def run(self):
        """Dameon code"""
        self.stderr.write('Cluster is alive...\n')
        self.stderr.flush()
        
        # running subscripts
        args = [arg.strip() for arg in self.args[0].split('\n')]
        for command in args:
            res = self._system(command)
            if not res:
                self.stderr.write('Command "%s" failed\n' % command)  
                self.stderr.flush()
                sys.exit(1)
        while True:
            time.sleep(1)

def main(args=None):
    if args is None:
        args = sys.argv[1:]
    instance = Cluster(args=args)
    daemon = Daemon(instance)
    daemon.startstop()

