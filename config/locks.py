# -*- coding: utf-8 -*-

from buildbot import locks

CHECKOUT_LOCK = locks.SlaveLock("checkout")
PIRUM_LOCK = locks.MasterLock("pirum")
TAGFILES_LOCK = locks.MasterLock("tagfiles")

