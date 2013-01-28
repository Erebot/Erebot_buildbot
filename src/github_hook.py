# -*- coding: utf-8 -*-
from buildbot.status.web.hooks.github import process_change

import hmac
import hashlib
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
            body = request.content.read()
            payload = json.loads(body)
            project = payload['repository']['url'].partition('://')[2]
            project = project.split('/', 1)[1]
            user = payload['repository']['owner']['name']
            repo = payload['repository']['name']
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

            # Check integrity/origin.
            body_hash = hmac.new(self._options.get('key'), body, hashlib.sha1)
            if body_hash.hexdigest() != request.getHeader('X-Hub-Signature'):
                log.msg("HMAC mismatch between header and actual payload")
                return

            # Older versions only accepted 4 args (no project).
            if process_change.func_code.co_argcount == 4:
                changes = process_change(payload, user, repo, repo_url)
            else:
                # Newer versions take 5 args.
                changes = process_change(payload, user, repo,
                                         repo_url, project)

            log.msg("Received %s changes from github" % len(changes))
            if not changes: # No changes.
                return (changes, 'git')
            elif not isinstance(changes[0], dict):
                # Probably an old buildmaster (< 0.8.4p1).
                # -> changes is a list of Change objects.
                # We patch them to add information about the project.
                for change in changes:
                    change.project = project
            return (changes, 'git')
        except Exception:
            logging.error("Encountered an exception:")
            for msg in traceback.format_exception(*sys.exc_info()):
                logging.error(msg.strip())

