# -*- coding: utf-8 -*-

from buildbot.process import factory
from Erebot_buildbot.config.steps import common

PACKAGE = factory.BuildFactory()
PACKAGE.addStep(common.clone)

