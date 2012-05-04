# -*- coding: utf-8 -*-

from buildbot.process import factory
from buildbot.process.properties import WithProperties
from buildbot.steps import trigger
from Erebot_buildbot.src import master
from Erebot_buildbot.src.steps import MorphProperties
from Erebot_buildbot.config.steps import common
import secrets


def _get_vm_name(properties):
    buildslave = properties.getProperty("slavename")
    vm = secrets.BUILDSLAVES[buildslave].get("vm")
    if vm:
        properties.setProperty("VM", vm, "VirtualMachine")

VM_TESTS = factory.BuildFactory()
VM_TESTS.addStep(common.fill_properties)
VM_TESTS.addStep(MorphProperties(morph_fn=_get_vm_name))
VM_TESTS.addStep(master.MasterShellCommand(
    command=WithProperties("/usr/bin/sudo /root/vm/start.sh '%(VM)s'"),
    description=["Starting", "VM"],
    descriptionDone=["Start", "VM"],
))
VM_TESTS.addStep(trigger.Trigger(
    schedulerNames=[WithProperties("Tests - %(slavename)s")],
    waitForFinish=True,
    copy_properties=['project', 'repository', 'branch', 'revision'],
))
VM_TESTS.addStep(master.MasterShellCommand(
    command=WithProperties("/usr/bin/sudo /root/vm/stop.sh '%(VM)s'"),
    description=["Stopping", "VM"],
    descriptionDone=["Stop", "VM"],
))

