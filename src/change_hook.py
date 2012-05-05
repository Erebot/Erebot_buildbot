# -*- coding: utf-8 -*-

import re, types
from twisted.python.reflect import namedModule
from twisted.python.log import msg
from buildbot.status.web.change_hook import ChangeHookResource

class CallableChangeHookResource(ChangeHookResource):
    def getChanges(self, request):
        uriRE = re.search(r'^/change_hook/?([a-zA-Z0-9_]*)', request.uri)

        if not uriRE:
            msg("URI doesn't match change_hook regex: %s" % request.uri)
            raise ValueError("URI doesn't match change_hook regex: %s" % request.uri)

        changes = []
        src = None

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

        # Recent buildmasters (>= 0.8.4 ?)
        if isinstance(res, (tuple, list)) and isinstance(res[0], list) and \
            res[0][0] and isinstance(res[0][0], dict):
            return res

        # Older buildmasters.
        return changes

