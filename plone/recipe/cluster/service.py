# -*- coding: utf-8 -*-
"""Control file for win32

$Id$
"""
import sys
import os

import win32serviceutil
from nt_service import Service
import win32process
import win32api, win32con
import pywintypes

join = os.path.join

PYTHON = sys.executable()
PYTHONSERVICE_EXE = join(os.path.dirname(__file__), 'PythonService.exe')
HKEY_LM = win32con.HKEY_LOCAL_MACHINE
KEY_PATH = "SYSTEM\\CurrentControlSet\\Services"

class NTService(Service):
    """adds a few hooks"""
    def checkRestart(self):
        res = Service.checkRestart(self)
        if res:
            self.onRestart()
        return res

    def run(self):
        res = Service.run(self)
        if res:
            self.onStart()
        return res

    def onRestart(self):
        raise NotImplementedError
    onStart = onRestart

def get_service_klass(label, display_name, args=''):
    """class factory"""
    class ClusterService(NTService):
        _exe_name_ = PYTHONSERVICE_EXE
        process_runner = PYTHON
        process_args = args
        _svc_name_ = label
        _svc_display_name_ = display_name
           
        def _runCommand(self, cmd):
            si = win32process.STARTUPINFO()
            si.dwFlags = win32process.STARTF_USESTDHANDLES | \
                         win32process.STARTF_USESHOWWINDOW
            si.wShowWindow = win32con.SW_HIDE
            create_flags = win32process.CREATE_NEW_CONSOLE
            return win32process.CreateProcess(None, cmd, None, None, True,
                        create_flags, None, None, si)

        def onStop(self):
            """called when stopped"""
            pass

        def onRestart(self):
            """called when restarted"""
            pass

        def onStart(self):
            """called when starting"""
            pass

    return ClusterService

def main(args=None):
    if args is None:
        args = ([], [], [], False, 'cluster.pid')
    foreground = not bool(args[-2])
    pidfile = args[-1]
    args = args[:3]

    service_name = "Cluster_%s" % str(hash(args))
    key = "%s\\%s" % (KEY_PATH, service_name)
    label = display_name = 'Plone Cluster Service'

    # getting the key
    try:
        win32api.RegOpenKey(HKEY_LM, key, 0, win32con.KEY_READ)
    except pywintypes.error, msg:
        raise

    # creating the service instance
    if len(sys.argv) != 2:
        print 'usage: %s start|stop|restart|status|install|remove' % sys.argv[0]
        sys.exit(1)
    action = sys.argv[1]
    klass = get_service_klass(label, display_name, action)
    win32serviceutil.HandleCommandLine(klass)

