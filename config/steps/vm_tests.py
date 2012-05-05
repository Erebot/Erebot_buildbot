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

    # No VM is needed to run tests on this buildslave.
    # Trigger the next test builder right after that.
    if not vm:
        VM_TESTS.addStep(trigger.Trigger(
            schedulerNames=["Tests - %s" % buildslave],
            copy_properties=['project', 'repository', 'branch', 'revision'],
        ))
        continue

    # Start the VM.
    VM_TESTS.addStep(master.MasterShellCommand(
        command=WithProperties("/usr/bin/sudo /root/vm/start.sh '%s'" % vm),
        description=["Starting", "VM"],
        descriptionDone=["Start", "VM"],
    ))

    # Run the tests.
    VM_TESTS.addStep(trigger.Trigger(
        schedulerNames=["Tests - %s" % buildslave],
        waitForFinish=True,
        copy_properties=['project', 'repository', 'branch', 'revision'],
    ))

    # Stop the VM once the tests are over.
    VM_TESTS.addStep(master.MasterShellCommand(
        command=WithProperties("/usr/bin/sudo /root/vm/stop.sh '%s'" % vm),
        description=["Stopping", "VM"],
        descriptionDone=["Stop", "VM"],
    ))

