# -*- coding: utf-8 -*-

from buildbot import locks

CHECKOUT_LOCK = locks.SlaveLock("checkout")
PACKAGE_LOCK = locks.MasterLock("package")
TAGFILES_LOCK = locks.MasterLock("tagfiles")

