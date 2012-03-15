# -*- python -*-
# ex: set syntax=python:

import tarfile
from buildbot.steps import transfer
from buildbot.process.buildstep import BuildStep, SUCCESS, FAILURE, SKIPPED
from buildbot.status.web import authz

def _TarFile__enter__(self):
    self._check()
    return self

def _TarFile__exit__(self, type, value, traceback):
    if type is None:
        self.close()
    else:
        # An exception occurred. We must not call close() because
        # it would try to write end-of-archive blocks and padding.
        if not self._extfileobj:
            self.fileobj.close()
        self.closed = True

if not hasattr(tarfile.TarFile, '__enter__'):
    tarfile.TarFile.__enter__ = _TarFile__enter__
if not hasattr(tarfile.TarFile, '__exit__'):
    tarfile.TarFile.__exit__ = _TarFile__exit__


def finished(self, result):
    # Subclasses may choose to skip a transfer. In those cases, self.cmd
    # will be None, and we should just let BuildStep.finished() handle
    # the rest
    if result == SKIPPED:
        return BuildStep.finished(self, SKIPPED)
    if self.cmd.stdout != '':
        self.addCompleteLog('stdout', self.cmd.stdout)

    if self.cmd.rc is None or self.cmd.rc == 0:
        return BuildStep.finished(self, SUCCESS)
    return BuildStep.finished(self, FAILURE)
transfer.DirectoryUpload.finished = finished

if not hasattr(authz.Authz, 'authenticated'):
    authz.Authz.authenticated = None
    # buildbot 0.8.3pl1 did not support 'showUsersPage'
    # but we need it for later versions, so we just patch
    # the class to add it (it is not used by any template
    # in that release, so it's not a big deal anyway).
    if 'showUsersPage' not in authz.Authz.knownActions:
        authz.Authz.knownActions.append('showUsersPage')

