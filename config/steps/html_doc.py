# -*- coding: utf-8 -*-

from buildbot.process import factory
from Erebot_buildbot.config.steps import common

HTML_DOC = factory.BuildFactory()
HTML_DOC.addStep(common.clone)

