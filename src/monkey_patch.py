# -*- python -*-
# ex: set syntax=python:

import tarfile
from twisted.python import log
from twisted.internet import defer
from buildbot.steps import transfer
from buildbot.process.buildstep import BuildStep, SUCCESS, FAILURE, SKIPPED
from buildbot.status.web import authz

try:
    from buildbot.process.users import users
except ImportError:
    users = None

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


    if getattr(self.cmd, 'stdout', '') != '':
        self.addCompleteLog('stdout', self.cmd.stdout)

    if getattr(self.cmd, 'stderr', '') != '':
        self.addCompleteLog('stderr', self.cmd.stderr)

    if self.cmd.rc is None or self.cmd.rc == 0:
        return BuildStep.finished(self, SUCCESS)
    return BuildStep.finished(self, FAILURE)
transfer.DirectoryUpload.finished = finished


def createUserObject(master, author, src=None):
    """
    Take a Change author and source and translate them into a User Object,
    storing the user in master.db, or returning None if the src is not
    specified.

    @param master: link to Buildmaster for database operations
    @type master: master.Buildmaster instance

    @param authors: Change author if string or Authz instance
    @type authors: string or status.web.authz instance

    @param src: source from which the User Object will be created
    @type src: string
    """

    if not src:
        log.msg("No vcs information found, unable to create User Object")
        return defer.succeed(None)

    if src in users.srcs:
        log.msg("checking for User Object from %s Change for: %s" %
                (src, author.encode("ascii", "replace")))
        usdict = dict(identifier=author, attr_type=src, attr_data=author)
    else:
        log.msg("Unrecognized source argument: %s" % src)
        return defer.succeed(None)

    return master.db.users.findUserByAttr(
            identifier=usdict['identifier'],
            attr_type=usdict['attr_type'],
            attr_data=usdict['attr_data'])

if users:
    users.createUserObject = createUserObject

