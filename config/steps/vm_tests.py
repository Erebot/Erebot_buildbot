# -*- coding: utf-8 -*-

from buildbot.process import factory
from buildbot.process.properties import WithProperties
from buildbot.steps import trigger
from Erebot_buildbot.src import master
from Erebot_buildbot.src.steps import MorphProperties
from Erebot_buildbot.config.steps import common
import secrets

VM_TESTS = factory.BuildFactory()
VM_TESTS.addStep(common.fill_properties)

for buildslave in secrets.BUILDSLAVES:
    VM_TESTS.addStep(trigger.Trigger(
        schedulerNames=["Tests - %s" % buildslave],
        copy_properties=['project', 'repository', 'branch', 'revision'],
    ))

