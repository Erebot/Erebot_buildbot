# -*- coding: utf-8 -*-

import hmac
import hashlib
import urllib2
import json
import logging
import sys
import traceback
from dateutil.parser import parse as dateparse

from twisted.python import log
from buildbot.status.web.hooks.github import process_change
from buildbot.master import BuildMaster

from Erebot_buildbot.config import misc


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

            # Check integrity/origin.
            body_hash = "sha1=" + hmac.new(self._options.get('key'),
                                           body, hashlib.sha1).hexdigest()
            if body_hash != request.getHeader('X-Hub-Signature'):
                log.msg("HMAC mismatch between header (%s) and actual payload (%s)" % (
                    request.getHeader('X-Hub-Signature'),
                    body_hash,
                ))
                return

            payload = json.loads(body)

            if 'pull_request' in payload:
                return (
                            process_pull_request(
                                payload['pull_request'],
                                payload['action'],
                                self._options.get('token')
                            ),
                            'git'
                        )

            project = payload['repository']['url'].partition('://')[2]
            project = project.split('/', 1)[1]
            user = payload['repository']['owner']['name']
            repo = payload['repository']['name']
            repo_url = payload['repository']['url']

            changes = process_change(payload, user, repo, repo_url, project)

            log.msg("Received %s changes from github" % len(changes))
            return (changes, 'git')
        except Exception:
            logging.error("Encountered an exception:")
            for msg in traceback.format_exception(*sys.exc_info()):
                logging.error(msg.strip())

def gh_api(url, token, data=None):
    headers = {}
    if data != None:
        data = json.dumps(data)
    headers['Authorization'] = 'token %s' % (token, )
    res = urllib2.urlopen(urllib2.Request(url, data, headers))
    return json.load(res)

def process_pull_request(payload, action, token):
    """
    Consumes the JSON as a python object and actually starts the build.

    :arguments:
        payload
            Python Object that represents the JSON sent by GitHub Service
            Hook.

        action
            The action that was performed on the pull request.
            One of "opened", "closed", "synchronized" or "reopened".

        token
            OAuth token to use to query the GitHub API.

    For this method to work, the hook must have been registered to receive
    `pull_request` events for the repository.
    This can be done from the commandline using curl::

        curl -H 'Authorization: bearer :oauth2_token' \
             -i https://api.github.com/repos/:owner/:repo/hooks \
             -d '{
                  "name": "web",
                  "active": true,
                  "events": [
                    "pull_request"
                  ],
                  "config": {
                    "url": "http://ci.example.com/change_hook/erebot_github",
                    "secret": ":secret",
                    "content_type": "json"
                  }
                }'
    """
    log.msg("Processing pull request at %s (%s)" %
            (payload['html_url'], action))
    repo_url = payload['head']['repo']['html_url']
    project = payload['head']['repo']['full_name']
    newrev = payload['head']['sha']
    refname = payload['head']['ref']

    # Retrieve all commits for that pull request.
    commits = gh_api('%s/commits' % (payload['url'], ), token)
    changes = []
    for commit in commits:
        # Retrieve the files added/removed/modified for each commit.
        files = [
            f['filename'] for f
            in gh_api(commit['commit']['url'], token)['files']
        ]
        when_timestamp = dateparse(commit['author']['date'])
        log.msg("New revision: %s" % commit['sha'][:7])

        changes.append({
            'author': '%s <%s>' % (
                commit['commit']['author']['name'],
                commit['commit']['author']['email']
            ),
            'files': files,
            'comments': commit['commit']['message'],
            'revision': commit['sha'],
            'when_timestamp': when_timestamp,
            'branch': refname,
            'revlink': commit['html_url'],
            'repository': repo_url,
            'project': project,
        })
    return changes

