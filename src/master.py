# -*- coding: utf-8 -*-
"""
Master command that renders properties
when used in the env argument.
"""

import os, types
from twisted.python import runtime
from twisted.internet import reactor
from buildbot.steps.master import MasterShellCommand as MSC

class MasterShellCommand(MSC):
    def start(self):
        # render properties
        properties = self.build.getProperties()
        command = properties.render(self.command)
        # set up argv
        if type(command) in types.StringTypes:
            if runtime.platformType  == 'win32':
                argv = os.environ['COMSPEC'].split() # allow %COMSPEC% to have args
                if '/c' not in argv: argv += ['/c']
                argv += [command]
            else:
                # for posix, use /bin/sh. for other non-posix, well, doesn't
                # hurt to try
                argv = ['/bin/sh', '-c', command]
        else:
            if runtime.platformType  == 'win32':
                argv = os.environ['COMSPEC'].split() # allow %COMSPEC% to have args
                if '/c' not in argv: argv += ['/c']
                argv += list(command)
            else:
                argv = command

        self.stdio_log = stdio_log = self.addLog("stdio")

        if type(command) in types.StringTypes:
            stdio_log.addHeader(command.strip() + "\n\n")
        else:
            stdio_log.addHeader(" ".join(command) + "\n\n")
        stdio_log.addHeader("** RUNNING ON BUILDMASTER **\n")
        stdio_log.addHeader(" in dir %s\n" % os.getcwd())
        stdio_log.addHeader(" argv: %s\n" % (argv,))
        self.step_status.setText(list(self.description))

        if self.env is None:
            env = os.environ
        else:
            assert isinstance(self.env, dict)
            env = properties.render(self.env)
        stdio_log.addHeader(" env: %r\n" % (env,))
        # TODO add a timeout?
        reactor.spawnProcess(self.LocalPP(self), argv[0], argv,
                path=self.path, usePTY=self.usePTY, env=env )
        # (the LocalPP object will call processEnded for us)

