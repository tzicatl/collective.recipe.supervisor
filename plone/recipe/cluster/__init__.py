# -*- coding: utf-8 -*-
"""Recipe cluster"""
import os

import zc.recipe.egg
from zc.buildout import UserError

class Recipe(object):
    """zc.buildout recipe"""

    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options
        self.egg = zc.recipe.egg.Egg(buildout, options['recipe'], options)
        options['location'] = os.path.join(
            buildout['buildout']['parts-directory'],
            self.name,
            )
        options['bin-directory'] = buildout['buildout']['bin-directory']

    def install(self):
        """Installer"""
        options = self.options
        requirements, ws = self.egg.working_set()
        ws_locations = [d.location for d in ws]

        # get options
        bin_directory = options['bin-directory']
        python = options['executable']
        script_name = options.get('control-script', self.name)
        extra_paths = options.get('extra_paths', [])
        start = options['start'].strip()
        stop = options['stop'].strip()
        restart = options.get('restart', '')
        
        zc.buildout.easy_install.scripts(
            [(script_name, 'plone.recipe.cluster.ctl', 'main')],
            ws, python, bin_directory,
            extra_paths=extra_paths, 
            arguments=(start, stop, restart))

        # Return files that were created by the recipe. The buildout
        # will remove all returned files upon reinstall.
        return tuple()

    def update(self):
        """Updater"""
        # XXX do not generate the script when it doesn't change
        self.install()

