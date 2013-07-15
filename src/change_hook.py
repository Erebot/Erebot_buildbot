# -*- coding: utf-8 -*-

import re, types
from twisted.python.reflect import namedModule
from twisted.python.log import msg
from buildbot.status.web.change_hook import ChangeHookResource
from buildbot.master import BuildMaster
from buildbot.changes.changes import Change

class CallableChangeHookResource(ChangeHookResource):
    def getChanges(self, request):
        uriRE = re.search(r'^/change_hook/?([a-zA-Z0-9_]*)', request.uri)

        if not uriRE:
            msg("URI doesn't match change_hook regex: %s" % request.uri)
            raise ValueError("URI doesn't match change_hook regex: %s" % request.uri)

        src = None
        res = []

        # Was there a dialect provided?
        if uriRE.group(1):
            dialect = uriRE.group(1)
        else:
            dialect = 'base'

        if dialect in self.dialects:
            if isinstance(self.dialects[dialect], object):
                msg("Attempting to get changes using the %s hook" % dialect)
                res = self.dialects[dialect].getChanges(request)
            else:
                msg("Attempting to load module buildbot.status.web.hooks." + dialect)
                tempModule = namedModule('buildbot.status.web.hooks.' + dialect)
                res = tempModule.getChanges(request, self.dialects[dialect])
            msg("Got the following changes %s" % (res, ))

        else:
            m = "The dialect specified, '%s', wasn't whitelisted in change_hook" % dialect
            msg(m)
            msg("Note: if dialect is 'base' then it's possible your URL is malformed and we didn't regex it properly")
            raise ValueError(m)

        if res:
            # res is a tuple with 2 items:
            # - a list of dicts of change properties (see above)
            # - the name of a VCS source (eg. "git")
            res, src = res
        else:
            # res could be None, which would cause errors later on,
            # so we force it to be an empty list instead.
            res = []

        return (res, src)

