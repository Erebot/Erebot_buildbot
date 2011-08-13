# -*- coding: utf-8 -*-

from buildbot import locks

checkout_lock = locks.SlaveLock("checkout")
pirum_lock = locks.MasterLock("pirum")
tagfiles_lock = locks.MasterLock("tagfiles")

