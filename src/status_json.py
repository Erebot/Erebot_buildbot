# -*- coding: utf-8 -*-
import urllib
from twisted.internet import defer
from buildbot.status import builder
from buildbot.status.web.status_json import \
    JsonResource, \
    JsonStatusResource as OrigJsonStatusResource
from Erebot_buildbot.config import misc
from sqlalchemy import exc
from twisted.python import log

class ComponentJsonResource(JsonResource):
    help = """Describe the status of a component for every builder.
"""
    pageTitle = 'Component'

    def __init__(self, status, project):
        JsonResource.__init__(self, status)
        self._project = project

    def _engine_txn(self, engine):
        results = {}
        conn = engine.connect()

        q = """
            SELECT
                b.number,
                breqs.buildername,
                breqs.results

            FROM sourcestamps sstamps
            JOIN buildsets bsets
                ON bsets.sourcestampid = sstamps.id
            JOIN buildrequests breqs
                ON breqs.buildsetid = bsets.id
            JOIN builds b
                ON b.brid = breqs.id

            WHERE sstamps.project == '%s'
            GROUP BY breqs.buildername
            HAVING b.number = MAX(b.number);
        """

        q2 = """
            SELECT
                b.number,
                breqs.buildername,
                breqs.results

            FROM sourcestamps sstamps
            JOIN sourcestampsets ssets
                ON ssets.id = sstamps.sourcestampsetid
            JOIN buildsets bsets
                ON bsets.sourcestampsetid = ssets.id
            JOIN buildrequests breqs
                ON breqs.buildsetid = bsets.id
            JOIN builds b
                ON b.brid = breqs.id

            WHERE sstamps.project == '%s'
            GROUP BY breqs.buildername
            HAVING b.number = MAX(b.number);
        """

        def _exec(txn):
            res = {
                'project': self._project,
                'results': {}
            }
            for buildername in self.status.getBuilderNames():
                res['results'][buildername] = {
                    'build': None,
                    'result': 'no build',
                }
            try:
                query_res = txn.execute(q2 % self._project)
            except exc.OperationalError:
                query_res = txn.execute(q % self._project)
            labels = dict(enumerate(builder.Results))
            for number, buildername, result in query_res.fetchall():
                res['results'][buildername] = {
                    'build': number,
                    'result': labels.get(result, 'building'),
                }
            return res

        try:
            results = conn.transaction(_exec)
        finally:
            conn.close()
        return results

    def asDict(self, request):
        # buildbot < 0.8.5 does not support the new DB API.
        if getattr(self.status, 'db', None):
            return defer.success({'error': 'dbapi'})

        whitelist = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' \
                    'abcdefghijklmnopqrstuvwxyz' \
                    '1234567890_./'
        if self._project.lstrip(whitelist):
            return defer.success({'error': 'whitelist'})

        d = self.status.master.db.pool.do_with_engine(self._engine_txn)
        d.addErrback(lambda _unused: {'error': "errback"})
        return d

class ComponentUserJsonResource(JsonResource):
    pageTitle = 'Components'
    help = """Shows components for a given user.
"""

    def __init__(self, status, user):
        JsonResource.__init__(self, status)
        for component in misc.COMPONENTS:
            parts = component.partition('/')
            if parts[0] != user:
                continue
            log.msg("Adding %s as a child component of %s" % (component, user))
            self.putChild(parts[2], ComponentJsonResource(status, component))

class ComponentsJsonResource(JsonResource):
    pageTitle = 'Components'
    help = """Shows users having components.
"""

    def __init__(self, status):
        JsonResource.__init__(self, status)
        users = [component.partition('/')[0] for component in misc.COMPONENTS]
        for user in set(users):
            log.msg("Adding %s as a user component" % (user, ))
            self.putChild(user, ComponentUserJsonResource(status, user))

class JsonStatusResource(OrigJsonStatusResource):
    def __init__(self, status):
        OrigJsonStatusResource.__init__(self, status)
        self.putChild('components', ComponentsJsonResource(status))

