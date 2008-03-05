Supported options
=================

The recipe supports the following options:

.. Note to recipe author!
   ----------------------
   For each option the recipe uses you shoud include a description
   about the purpose of the option, the format and semantics of the
   values it accepts, whether it is mandatory or optional and what the
   default value is if it is omitted.

option1
    Description for ``option1``...

option2
    Description for ``option2``...

(add extra commands, not daemonized, like "purge, save, etc

Example usage
=============

.. Note to recipe author!
   ----------------------
   zc.buildout provides a nice testing environment which makes it
   relatively easy to write doctests that both demonstrate the use of
   the recipe and test it.
   You can find examples of recipe doctests from the PyPI, e.g.
   
     http://pypi.python.org/pypi/zc.recipe.egg

   The PyPI page for zc.buildout contains documentation about the test
   environment.

     http://pypi.python.org/pypi/zc.buildout#testing-support

   Below is a skeleton doctest that you can start with when building
   your own tests.

The `cluster` recipe allows you to create composite commands for your  
buildout to start it. 

There are three base commands:

- start
- stop
- restart

Each command is a variable with a list of commands to be
run. The recipe then launches:
- a daemon under Linux based system
- a NT service under Windows

Let's try this::

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... parts = cluster
    ... index = http://pypi.python.org/simple
    ... [cluster]
    ... recipe = plone.recipe.cluster
    ... start = 
    ...    ${buildout:bin-directory}/script1 start
    ...    ${buildout:bin-directory}/script2 start
    ...
    ... stop = 
    ...    ${buildout:bin-directory}/script1 stop
    ...    ${buildout:bin-directory}/script2 stop
    ... 
    ... restart = 
    ...    ${buildout:bin-directory}/script1 restart
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

Let's try to execute it::

    >>> print system(script)
    usage: /sample-buildout/bin/cluster start|stop|restart
    <BLANKLINE>

Ah right, let's start it !
::

    >>> print system('%s start' % script)
    <BLANKLINE>
    Started with pid ...
    Cluster is alive...
    <BLANKLINE>

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
    Cluster is going down...
    Could not stop, pid file 'cluster.pid' missing.
    <BLANKLINE>

Oh right, it was stopped !

