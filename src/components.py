# -*- coding: utf-8 -*-
import urllib
from buildbot.status import builder
from buildbot.status.web.base import HtmlResource, path_to_root
from Erebot_buildbot.config import misc

class ComponentsResource(HtmlResource):
    title = "Components"
    addSlash = True

    def _txn(self, t, conn):
        results = {}
        q = conn.quoteq("""
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
        """)
        t.execute(q, ())
        labels = dict(enumerate(builder.Results))
        for number, buildername, project, result in t.fetchall():
            if project not in misc.COMPONENTS:
                continue
            if buildername not in results:
                results[buildername] = {}
            results[buildername][project] = (
                number,
                labels.get(result, "pending")
            )
        return results

    def content(self, req, cxt):
        status = self.getStatus(req)
        builders = req.args.get("builder", status.getBuilderNames())
        bs = cxt['builders'] = []
        cxt['components'] = sorted(misc.COMPONENTS, key=lambda x: x.lower())
        cxt['results'] = status.db.runInteractionNow(self._txn, status.db)

        base_builders_url = path_to_root(req) + "builders/"
        for bn in builders:
            bld = { 'link': base_builders_url + urllib.quote(bn, safe=''),
                    'name': bn }
            bs.append(bld)

        template = req.site.buildbot_service.templates.get_template("components.html")
        return template.render(**cxt)

