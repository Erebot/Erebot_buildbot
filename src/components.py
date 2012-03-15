# -*- coding: utf-8 -*-
import urllib
from twisted.internet import defer
from buildbot.status import builder
from buildbot.status.web.base import HtmlResource, path_to_root
from Erebot_buildbot.config import misc

try:
    from buildbot.db.base import DBConnectorComponent
except ImportError:
    DBConnectorComponent = None

class ComponentsResource(HtmlResource):
    title = "Components"
    addSlash = True

    def _get_results(self, res, root):
        results = {}
        labels = dict(enumerate(builder.Results))
        for number, buildername, project, result in res.fetchall():
            if project not in misc.COMPONENTS:
                continue
            if buildername not in results:
                results[buildername] = {}
            results[buildername][project] = (
                number,
                u"%s%s/builds/%s" % (root, buildername, number),
                labels.get(result, "building")
            )
        return results

    def _txn(self, txn, conn, root):
        q = """
            SELECT
                b.number,
                breqs.buildername,
                sstamps.project,
                breqs.results

            FROM sourcestamps sstamps
            JOIN buildsets bsets
                ON bsets.sourcestampid = sstamps.id
            JOIN buildrequests breqs
                ON breqs.buildsetid = bsets.id
            JOIN builds b
                ON b.brid = breqs.id

            WHERE project != ''
            AND project IS NOT NULL

            GROUP BY breqs.buildername, sstamps.project

            ORDER BY b.number DESC;
        """
        txn.execute(q, ())
        results = self._get_results(txn, root)
        return results

    def _engine_txn(self, engine, root):
        results = {}
        conn = engine.connect()

        q = """
            SELECT
                b.number,
                breqs.buildername,
                sstamps.project,
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

            WHERE project != ''
            AND project IS NOT NULL

            GROUP BY breqs.buildername, sstamps.project

            ORDER BY b.number DESC;
        """

        def _exec(txn):
            res = txn.execute(q)
            return self._get_results(res, root)

        try:
            results = conn.transaction(_exec)
        finally:
            conn.close()
        return results

    def _content(self, req, cxt):
        status = self.getStatus(req)
        builders = req.args.get("builder", status.getBuilderNames())
        base_builders_url = path_to_root(req) + "builders/"
        bs = cxt['builders'] = []
        cxt['components'] = sorted(misc.COMPONENTS, key=lambda x: x.lower())

        if getattr(status, 'db', None):
            cxt['results'] = status.db.runInteractionNow(
                self._txn,
                status.db,
                base_builders_url
            )
        else:
            master = self.getBuildmaster(req)
            wfd = defer.waitForDeferred(
                master.db.pool.do_with_engine(
                    self._engine_txn,
                    base_builders_url
                )
            )
            yield wfd
            cxt['results'] = wfd.getResult()

        for bn in builders:
            bld = { 'link': base_builders_url + urllib.quote(bn, safe=''),
                    'name': bn }
            bs.append(bld)

        template = req.site.buildbot_service.templates.get_template("components.html")
        yield template.render(**cxt)

    def _get_deferred_content(self, *args, **kwargs):
        return self._content(*args, **kwargs).next()

    if DBConnectorComponent:
        content = defer.deferredGenerator(_content)
    else:
        content = _get_deferred_content

