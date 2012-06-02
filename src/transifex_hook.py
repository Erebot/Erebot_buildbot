# -*- coding: utf-8 -*-
import re
import calendar
import datetime
import logging
import sys
import traceback
from twisted.python import log
from Erebot_buildbot.config.steps.common import convert_repourl

def isiterable(v):
    return hasattr(v, '__iter__')

def process_change(project, resource, repo_url, language, percent):
    files = [u"data/i18n/%s/LC_MESSAGES/%s.po" % (language, resource)]
    when = calendar.timegm(datetime.datetime.utcnow().utctimetuple())
    chdict = dict(
        who         = u"Transifex <https://www.transifex.net/projects/p/Erebot/>",
        files       = files,
        comments    = u'i18n for %s (%s)\n\nProgress: %s%%' %
                            (resource, language, percent),
        when        = when,
        branch      = None,
        revlink     = 'https://www.transifex.net/projects/p/%s/'
                      'resource/%s/l/%s/download/reviewed/' %
                            (project, resource, language),
        repository  = repo_url,
        project     = '%s/%s' % (project, resource),
        category    = 'transifex',
        properties  = {
            'locale': language,
            'percent': percent,
            'txProject': project,
            'txResource': resource,
        },
    )
    log.msg("Received i18n update for '%s/%s' and locale '%s' (%s%%)" %
            (project, resource, language, percent))
    return [chdict]

class TransifexChangeHook(object):
    def __init__(self, options=None):
        if not isinstance(options, dict):
            options = {}
        self._options = options
        self._converter = convert_repourl(False)
        self._language_re = re.compile('^[a-z_-]+$', re.I)

    def getChanges(self, request, options=None):
        """
        Responds only to POST events and starts the build process

        :arguments:
            request
                the http request object
        """
        try:
            project = request.args['project'][0]
            resource = request.args['resource'][0]
            language = request.args['language'][0]
            percent = request.args['percent'][0]
            key = request.args['key'][0]

            # Check the project & resource against our whitelist.
            ghProject = '%s/%s' % (project, resource)
            allowed_projects = self._options.get('project', [ghProject])
            if ghProject not in allowed_projects:
                log.msg("Refused change request from %s "
                        "(invalid project/resource)" %
                        ghProject)
                return

            # Check the key against our whitelist.
            allowed_keys = self._options.get('key')
            if not isiterable(allowed_keys):
                allowed_keys = [allowed_keys]
            if (key not in allowed_keys):
                log.msg("Refused change request "
                        "from %s (invalid key)" % ghProject)
                return

            # Check that the language is well-formed.
            if not self._language_re.match(language):
                log.msg("Refused change request "
                        "from %s (invalid language: %s)" %
                        (ghProject, language))
                return

            # URL to the repository.
            repo_url = "%s/%s" % (
                self._options.get('url_base').rstrip('/'),
                ghProject,
            )

            # What Transifex calls a "resource" is actually
            # a project name for us, while its "project"
            # is simply a repository prefix in our case.
            changes = process_change(project, resource, repo_url,
                                     language, percent)
            return (changes, 'git')
        except Exception:
            logging.error("Encountered an exception:")
            for msg in traceback.format_exception(*sys.exc_info()):
                logging.error(msg.strip())

