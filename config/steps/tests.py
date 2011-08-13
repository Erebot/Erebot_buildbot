# -*- coding: utf-8 -*-

from buildbot.process import factory
from Erebot_buildbot.config.steps import common
from Erebot_buildbot.src.steps import Link, PHPUnit

TESTS = factory.BuildFactory()
TESTS.addStep(common.clone)

