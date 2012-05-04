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
    vm = secrets.BUILDSLAVES[buildslave].get("vm")
    # No VM, that means the tests are probably run
    # on the server itself (or a contributed machine)
    # and we don't to trigger the tests manually.
    if not vm:
        continue

    VM_TESTS.addStep(master.MasterShellCommand(
        command=WithProperties("/usr/bin/sudo /root/vm/start.sh '%s'" % vm),
        description=["Starting", "VM"],
        descriptionDone=["Start", "VM"],
    ))
    VM_TESTS.addStep(trigger.Trigger(
        schedulerNames=["Tests - %s" % buildslave],
        waitForFinish=True,
        copy_properties=['project', 'repository', 'branch', 'revision'],
    ))
    VM_TESTS.addStep(master.MasterShellCommand(
        command=WithProperties("/usr/bin/sudo /root/vm/stop.sh '%s'" % vm),
        description=["Stopping", "VM"],
        descriptionDone=["Stop", "VM"],
    ))

