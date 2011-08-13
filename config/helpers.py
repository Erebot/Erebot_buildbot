# -*- coding: utf-8 -*-

def get_pear_pkg(rc, stdout, stderr):
    pear_pkg = stdout.strip().rstrip('.tgz')
    if not pear_pkg or "\n" in pear_pkg:
        pear_pkg = None
    return {
        "pear_pkg": pear_pkg,
    }

def has_pear_pkg(step):
    return bool(step.getProperty("pear_pkg"))

