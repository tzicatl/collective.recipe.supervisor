Supported options
=================

The recipe supports the following options:

debug
    default option is 0. When set to 1, allows tests to run
    on a non-blocking daemon.

start
    Multiline option. Each line is a command line that will be
    called by the daemon when it is called with the `start` option.
    The commands must return immediatly, because the daemon waits
    for it before it launches the next command.

    It is possible though, to push a command line in the background
    with the `background:` prefix.

stop
    Multiline option. Each line is a command line that will be
    called by the daemon when it is called with the `stop` option.
    The commands must return immediatly, because the daemon waits
    for it before it launches the next command.

    It is possible to ask the daemon to kill a given process, by
    providing a `pid:value` command line. Where `value` is either
    a PID number, either a text files that contains a pid.

    The `background:` prefix is also available.

restart
    Multiline option. Each line is a command line that will be
    called by the daemon when it is called with the `restart` option.
    The commands must return immediatly, because the daemon waits
    for it before it launches the next command.

    It is possible to ask the daemon to kill a given process, by
    providing a `pid:value` command line. Where `value` is either
    a PID number, either a text files that contains a pid.

    The `background:` prefix is also available.

pid-file
    Defines the path to the PID file of the daemon.

Example usage
=============

The `cluster` recipe allows you to create composite commands for your  
buildout. There are three commands:

- start
- stop
- restart

Each command is a variable with a list of commands to be
run. The recipe then launches:
- a daemon under Linux based system
- a NT service under Windows

A typical usage for instance is to start zeo, zope and pound::

    [buildout]

    ...

    [cluster]
    recipe = plone.recipe.cluster

    poundctl = ${buildout:bin-directory}/pound -f ${buildout:directory}/parts/pound/etc/pound.cfg -c ${buildout:directory}/pound.pid

    
    start = 
        ${buildout:bin-directory}/zeoserver start
        ${buildout:bin-directory}/instance start
        ${cluster:poundctl}
    
    stop = 
        ${buildout:bin-directory}/zeoserver stop
        ${buildout:bin-directory}/instance stop
        pid:${buildout:directory}/pound.pid
    
    restart = 
        ${buildout:bin-directory}/zeoserver restart
        ${buildout:bin-directory}/instance restart
        ${cluster:poundctl}

Let's try this::

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... parts = cluster
    ... index = http://pypi.python.org/simple
    ... [cluster]
    ... recipe = plone.recipe.cluster
    ... debug = 1
    ... start = 
    ...    background:${buildout:bin-directory}/script1 
    ...    ${buildout:bin-directory}/script2 start
    ...
    ... stop = 
    ...    ${buildout:bin-directory}/script2 stop
    ... 
    ... restart = 
    ...    background:${buildout:bin-directory}/script1 
    ...    ${buildout:bin-directory}/script2 restart
    ...
    ... """)

Running the buildout gives us::

    >>> print system(buildout)
    Getting distribution for 'zc.recipe.egg'.
    Got zc.recipe.egg 1.0.0.
    Installing cluster.
    Generated script '/.../bin/cluster'.
    <BLANKLINE>

Now let's see the script that was created::

    >>> script = join(sample_buildout, 'bin', 'cluster')
    >>> print open(script).read()
    #!...python
    <BLANKLINE>
    import sys
    sys.path[0:0] = [
      ...
      ]
    <BLANKLINE>
    import plone.recipe.cluster.ctl
    <BLANKLINE>
    if __name__ == '__main__':
        plone.recipe.cluster.ctl.main(...)
    <BLANKLINE>

Let's create false scripts::

    >>> script2 = join(sample_buildout, 'bin', 'script2')
    >>> f = open(script2, 'w')
    >>> f.write('echo script 2')
    >>> f.close()
    >>> import os
    >>> os.chmod(script2, 0770)
    
    >>> script1 = join(sample_buildout, 'bin', 'script1') 
    >>> f = open(script1, 'w')
    >>> import sys
    >>> f.write("""\
    ... #!%s
    ... import time
    ... while 1:
    ...     time.sleep(0.1)
    ... """ % sys.executable)
    >>> f.close()
    >>> os.chmod(script1, 0770)

Let's try to execute it::

    >>> print system(script)
    usage: /sample-buildout/bin/cluster start|stop|restart|status
    <BLANKLINE>

Let's ask for the status::

    >>> print system('%s status' % script)
    Not running.

Ah right, let's start it !
::

    >>> print system('%s start' % script)
    Cluster is starting...
    Running in background ...script1
    Background pid is ...
    Background subpid is ...
    Running ...script2 start
    script 2
    Child PIDs: ..., ...
    Started with pid ...
    Cluster is alive...
    <BLANKLINE>

Let's ask for the status::
    
    >>> print system('%s status' % script)
    Running.

We should not be able to start it twice::
    
    >>> print system('%s start' % script)
    <BLANKLINE>
    Start aborded since pid file '...' exists.
    <BLANKLINE>

Let's stop it::

    >>> print system('%s stop' % script)
    <BLANKLINE>
    Cluster is going down...
    <BLANKLINE>

Let's restart it::

    >>> print system('%s restart' % script)
    Could not stop, pid file 'cluster.pid' missing.
    <BLANKLINE>

Oh right, it was stopped !

