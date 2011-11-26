# -*- coding: utf-8 -*-
"""
Master command that renders properties
when used in the env argument.
"""

import os, types, re
from twisted.python import runtime
from twisted.internet import reactor
from twisted.internet.protocol import ProcessProtocol
from buildbot.steps.master import MasterShellCommand as MSC

class MasterShellCommand(MSC):
    def __init__(self, command,
                 description=None, descriptionDone=None,
                 env=None, path=None, usePTY=0,
                 extract_fn=None, property=None, strip=True,
                 **kwargs):
        self.extract_fn = extract_fn
        self.property = property
        self.strip = strip

        MSC.__init__(self, command, description, descriptionDone, env, path, usePTY, **kwargs)
        self.addFactoryArguments(property=self.property)
        self.addFactoryArguments(extract_fn=self.extract_fn)
        self.addFactoryArguments(strip=self.strip)
        self.logged_output = []

    class LocalPP(ProcessProtocol):
        def __init__(self, step):
            self.step = step

        def outReceived(self, data):
            self.step.logged_output.append( (1, data) )
            self.step.stdio_log.addStdout(data)

        def errReceived(self, data):
            self.step.logged_output.append( (2, data) )
            self.step.stdio_log.addStderr(data)

        def processEnded(self, status_object):
            self.step.stdio_log.addHeader("exit status %d\n" % status_object.value.exitCode)
            self.step.processEnded(status_object)

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
            env = properties.render(self.env.copy())

            # do substitution on variable values matching patern: ${name}
            p = re.compile('\${([0-9a-zA-Z_]*)}')
            def subst(match):
                return os.environ.get(match.group(1), "")
            newenv = {}
            for key in os.environ.keys():
                # setting a key to None will delete it from the slave environment
                if key not in env or env[key] is not None:
                    newenv[key] = os.environ[key]
            for key in env.keys():
                if env[key] is not None:
                    newenv[key] = p.sub(subst, env[key])
            env = newenv
        stdio_log.addHeader(" env: %r\n" % (env,))

        # TODO add a timeout?
        reactor.spawnProcess(self.LocalPP(self), argv[0], argv,
                path=self.path, usePTY=self.usePTY, env=env )
        # (the LocalPP object will call processEnded for us)

    def processEnded(self, status_object):
        if self.property:
            result = ''.join([data[1] for data in self.logged_output])
            if self.strip: result = result.strip()
            propname = self.build.getProperties().render(self.property)
            self.setProperty(propname, result, "SetProperty Step")
        elif self.extract_fn:
            new_props = self.extract_fn(status_object.value.exitCode,
                    ''.join([data[1] for data in self.logged_output if data[0] == 1]),
                    ''.join([data[1] for data in self.logged_output if data[0] == 2]))
            for k,v in new_props.items():
                self.setProperty(k, v, "SetProperty Step")

        return MSC.processEnded(self, status_object)

