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

def if_component(component):
    def _inner(step):
        return component == step.getProperty('project')
    return _inner

def if_buildslave(buildslave):
    def _inner(step):
        return buildslave == step.getSlaveName()
    return _inner

def with_links(links, f=None):
    def _inner(step):
        if isinstance(links, dict):
            it = links.iteritems()
        else:
            it = links
        for (name, url) in it:
            step.addURL(name, url)

        if f is None:
            return True
        return f(step)
    return _inner

