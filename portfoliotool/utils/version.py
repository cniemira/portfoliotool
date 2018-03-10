from distutils.version import LooseVersion

def version_gte(a, b):
    if LooseVersion(a) >= LooseVersion(b):
        return True
    return False

def version_lte(a, b):
    if LooseVersion(a) <= LooseVersion(b):
        return True
    return False
