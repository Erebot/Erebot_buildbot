# -*- coding: utf-8 -*-
import urllib
from twisted.internet import defer
from buildbot.status import builder
from buildbot.status.web.base import HtmlResource, path_to_root
from Erebot_buildbot.config import misc
from sqlalchemy import exc

class ComponentsResource(HtmlResource):
    title = "Components"
    addSlash = True

    def _get_results(self, res, root, req):
        status = self.getStatus(req)
        results = {}
        labels = dict(enumerate(builder.Results))
        for number, buildername, project, result in res.fetchall():
            if project not in misc.COMPONENTS:
                continue
            try:
                build = status.getBuilder(buildername).getBuild(number)
            except KeyError:
                # Ignore errors raised for obsolete builders.
                continue
            if buildername not in results:
                results[buildername] = {}
            results[buildername][project] = (
                number,
                u"%s%s/builds/%s" % (root, buildername, number),
                labels.get(result, "building"),
                build,
            )
        return results

    def _engine_txn(self, engine, root, req):
        conn = engine.connect()

        def _exec(txn):
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

                WHERE %(projects)s
                %(revisions)s

                GROUP BY breqs.buildername, sstamps.project

                ORDER BY b.number DESC;
            """
            rvs = []
            for revision in req.args.get("revisions", []):
                try:
                    assert revision != ""
                    revision = revision.tolower()
                    assert revision.lstrip('1234567890abcdef') == ""
                    rvs.append(revision)
                except Exception:
                    pass

            pjs = []
            for project in req.args.get("project", []):
                try:
                    assert project != ""
                    assert project.lstrip(
                        '1234567890-_/.'
                        'abcdefghijklmnopqrstuvwxyz'
                        'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                    ) == ""
                    pjs.append(project)
                except Exception:
                    pass

            args = {
                "projects":
                    "sstamps.project != '' "
                    "AND sstamps.project IS NOT NULL",
                "revisions": "",
            }
            if pjs:
                args["projects"] = \
                    "sstamps.project IN ('%s')" % "','".join(pjs)
            if rvs:
                args["revisions"] = \
                    "AND sstamps.revision IN ('%s')" % "','".join(rvs)
            return self._get_results(txn.execute(q % args), root, req)

        try:
            results = conn.transaction(_exec)
        finally:
            conn.close()
        return results

    @defer.inlineCallbacks
    def content(self, req, cxt):
        status = self.getStatus(req)
        builders = req.args.get("builder", status.getBuilderNames())
        base_builders_url = path_to_root(req) + "builders/"
        bs = cxt['builders'] = []
        cxt['components'] = sorted(misc.COMPONENTS, key=lambda x: x.lower())

        master = self.getBuildmaster(req)
        cxt['results'] = yield master.db.pool.do_with_engine(
                                    self._engine_txn,
                                    base_builders_url,
                                    req,
                                )

        for bn in builders:
            bld = { 'link': base_builders_url + urllib.quote(bn, safe=''),
                    'name': bn }
            bs.append(bld)

        template = req.site.buildbot_service.templates.get_template("components.html")
        defer.returnValue(template.render(**cxt))

