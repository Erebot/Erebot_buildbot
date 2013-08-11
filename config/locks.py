# -*- coding: utf-8 -*-

from buildbot import locks

# Those locks are used in buildsteps.
CHECKOUT_LOCK = locks.SlaveLock("checkout")
PACKAGE_LOCK = locks.MasterLock("package")
TAGFILES_LOCK = locks.MasterLock("tagfiles")

# Those locks are used in builders.
QA_LOCK = locks.SlaveLock("QA", maxCount=2)
DOC_LOCK = locks.SlaveLock("doc", maxCount=2)
PACKAGING_LOCK = locks.SlaveLock("packaging", maxCount=2)

