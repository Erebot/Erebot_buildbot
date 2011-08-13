# -*- coding: utf-8 -*-

from buildbot.process import factory
from Erebot_buildbot.config.steps import common

QA_LINT = factory.BuildFactory()
QA_LINT.addStep(common.clone)

