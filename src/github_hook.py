# -*- coding: utf-8 -*-
from buildbot.status.web.hooks.github import process_change

import logging
import sys
import traceback
from twisted.python import log
from buildbot.master import BuildMaster

try:
    import json
    assert json
except ImportError:
    import simplejson as json

def isiterable(v):
    return hasattr(v, '__iter__')

class GithubChangeHook(object):
    def __init__(self, options=None):
        if not isinstance(options, dict):
            options = {}
        self._options = options

    def getChanges(self, request, options=None):
            """
            Responds only to POST events and starts the build process

            :arguments:
                request
                    the http request object
            """
            try:
                payload = json.loads(request.args['payload'][0])
                project = payload['repository']['url'].partition('://')[2]
                project = project.split('/', 1)[1]
                user = payload['repository']['owner']['name']
                repo = payload['repository']['name']
                project = request.args.get('project', [project])[0]
                key = request.args.get('key', [None])[0]
                repo_url = payload['repository']['url']

                # Check user whitelist.
                allowed_users = self._options.get('user', user)
                if not isiterable(allowed_users):
                    allowed_users = [allowed_users]
                if (user not in allowed_users):
                    log.msg("Refused change request "
                            "from %s/%s (user not in %s)" %
                            (user, repo, ','.join(allowed_users)))
                    return

                # Check repository whitelist.
                allowed_repos = self._options.get('repository', repo)
                if not isiterable(allowed_repos):
                    allowed_repos = [allowed_repos]
                if (repo not in allowed_repos):
                    log.msg("Refused change request "
                            "from %s/%s (repository not in %s)" %
                            (user, repo, ','.join(allowed_repos)))
                    return

                # Check key whitelist.
                allowed_keys = self._options.get('key')
                if not isiterable(allowed_keys):
                    allowed_keys = [allowed_keys]
                if (key not in allowed_keys):
                    log.msg("Refused change request "
                            "from %s/%s (invalid key)" % (user, repo))
                    return

                # Older versions only accepted 4 args
                # and returned a list of Change objects.
                if process_change.func_code.co_argcount == 4:
                    changes = process_change(payload, user, repo, repo_url)
                    for change in changes:
                        change.project = project
                    log.msg("Received %s changes from github" % len(changes))
                    return changes

                # Newer versions take 5 args, and must return a tuple
                # with (list of dicts of change properties, VCS name).
                changes = process_change(payload, user, repo, repo_url, project)
                log.msg("Received %s changes from github" % len(changes))
                return (changes, 'git')
            except Exception:
                logging.error("Encountered an exception:")
                for msg in traceback.format_exception(*sys.exc_info()):
                    logging.error(msg.strip())

