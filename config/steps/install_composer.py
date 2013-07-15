# -*- coding: utf-8 -*-

from buildbot.process import factory
from buildbot.process.properties import WithProperties
from buildbot.steps import shell
from Erebot_buildbot.config.steps import common
from Erebot_buildbot.config import misc
from Erebot_buildbot.src.steps import CountingShellCommand

INSTALL_COMPOSER = factory.BuildFactory()
INSTALL_COMPOSER.addStep(common.fill_properties)
INSTALL_COMPOSER.addStep(common.erebot_path)
INSTALL_COMPOSER.addStep(common.clone)
INSTALL_COMPOSER.addStep(common.composer_install)
INSTALL_COMPOSER.addStep(common.dependencies_install)

