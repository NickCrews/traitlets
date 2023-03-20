import inspect
import os
import warnings


def warn(msg, category, *, stacklevel, source=None):
    """Like warnings.warn(), but category and stacklevel are required.

    You pretty much never want the default stacklevel of 1, so this helps
    encourage setting it explicitly."""
    return warnings.warn(msg, category=category, stacklevel=stacklevel, source=source)


def deprecated_method(method, cls, method_name, msg):
    """Show deprecation warning about a magic method definition.

    Uses warn_explicit to bind warning to method definition instead of triggering code,
    which isn't relevant.
    """
    warn_msg = "{classname}.{method_name} is deprecated in traitlets 4.1: {msg}".format(
        classname=cls.__name__, method_name=method_name, msg=msg
    )

    for parent in inspect.getmro(cls):
        if method_name in parent.__dict__:
            cls = parent
            break
    # limit deprecation messages to once per package
    package_name = cls.__module__.split(".", 1)[0]
    key = (package_name, msg)
    if not should_warn(key):
        return
    try:
        fname = inspect.getsourcefile(method) or "<unknown>"
        lineno = inspect.getsourcelines(method)[1] or 0
    except (OSError, TypeError) as e:
        # Failed to inspect for some reason
        warn(
            warn_msg + ("\n(inspection failed) %s" % e),
            DeprecationWarning,
            stacklevel=2,
        )
    else:
        warnings.warn_explicit(warn_msg, DeprecationWarning, fname, lineno)


_deprecations_shown = set()


def should_warn(key):
    """Add our own checks for too many deprecation warnings.

    Limit to once per package.
    """
    env_flag = os.environ.get("TRAITLETS_ALL_DEPRECATIONS")
    if env_flag and env_flag != "0":
        return True

    if key not in _deprecations_shown:
        _deprecations_shown.add(key)
        return True
    else:
        return False
