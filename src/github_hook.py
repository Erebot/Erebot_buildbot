# -*- coding: utf-8 -*-
from buildbot.status.web.hooks.github import process_change

import logging
import sys
import traceback
from twisted.python import log

try:
    import json
    assert json
except ImportError:
    import simplejson as json

def getChanges(request, options = None):
        """
        Reponds only to POST events and starts the build process
        
        :arguments:
            request
                the http request object
        """
        if not isinstance(options, dict):
            options = {}
        try:
            payload = json.loads(request.args['payload'][0])
            category = request.args.get('category', [None])[0]
            project = request.args.get('project', [None])[0]
            user = payload['repository']['owner']['name']
            repo = payload['repository']['name']
            if user != options.get('user', user) or \
               repo != options.get('repository', repo) or \
               request.args.get('key', [None])[0] != options.get('key'):
                log.msg("Refused change request from %s/%s.git" % (user, repo))
                return
            repo_url = payload['repository']['url']
            # This field is unused:
            #private = payload['repository']['private']
            changes = process_change(payload, user, repo, repo_url)
            for change in changes:
                change.category = category
                change.project = project
            log.msg("Received %s changes from github" % len(changes))
            return changes
        except Exception:
            logging.error("Encountered an exception:")
            for msg in traceback.format_exception(*sys.exc_info()):
                logging.error(msg.strip())

