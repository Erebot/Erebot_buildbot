# -*- coding: utf-8 -*-

from buildbot.status.web.authz import Authz as _Authz

class Authz(_Authz):
    # buildbot 0.8.3pl1 did not support 'showUsersPage'
    # but we need it for later versions, so we just patch
    # the class to add it if required (it is not used by
    # any template in that release, so, not a big deal).
    knownActions = _Authz.knownActions[:]
    if 'showUsersPage' not in knownActions:
        knownActions.append('showUsersPage')

    # This method does not exist on older versions but is used
    # by templates in newer versions. We define an attribute with
    # the same name and add a test in layout.html to check that
    # the method is indeed defined before it's called.
    if not hasattr(_Authz, 'authenticated'):
        authenticated = None

    def advertiseAction(self, action, request=None):
        # This method takes 3 arguments in recent versions of buildbot,
        # while it only accepted 2 arguments in buildbot 0.8.3pl1.
        # We patch it so that the signature becomes the same (3 args)
        # on all versions.
        if _Authz.advertiseAction.__func__.func_code.co_argcount == 2:
            return super(Authz, self).advertiseAction(action)
        return super(Authz, self).advertiseAction(action, request)
