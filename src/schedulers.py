# -*- coding: utf-8 -*-

import sqlalchemy as sa
from twisted.python import log
from buildbot.schedulers.basic import BaseBasicScheduler
from buildbot.changes import filter
from buildbot.util import NotABranch

class PerProjectAndBranchScheduler(BaseBasicScheduler):
    def getChangeFilter(self, branch, branches, change_filter, categories):
        return filter.ChangeFilter.fromSchedulerConstructorArgs(
                change_filter=change_filter, branch=branches,
                categories=categories)

    def getTimerNameForChange(self, change):
        return (change.project, change.branch)

    def getChangeClassificationsForTimer(self, schedulerid, timer_name):
        project, branch = timer_name # set in getTimerNameForChange
        def thd(conn):
            sch_ch_tbl = self.master.db.model.scheduler_changes
            ch_tbl = self.master.db.model.changes
            wc = (
                (sch_ch_tbl.c.objectid == schedulerid) &
                (sch_ch_tbl.c.changeid == ch_tbl.c.changeid) &
                (ch_tbl.c.project == project) &
                (ch_tbl.c.branch == branch)
            )

            q = sa.select(
                [ sch_ch_tbl.c.changeid, sch_ch_tbl.c.important ],
                whereclause=wc)
            return dict([ (r.changeid, [False,True][r.important])
                          for r in conn.execute(q) ])
        return self.master.db.pool.do(thd)

