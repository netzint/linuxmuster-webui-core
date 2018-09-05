import subprocess
import traceback

import wu

# TODO sort this out


def platform_select(**values):
    """
    Selects a value from **kwargs** depending on runtime platform

    ::

        service = platform_select(
            debian='samba',
            ubuntu='smbd',
            centos='smbd',
            default='samba',
        )

    """
    if wu.platform_unmapped in values:
        return values[wu.platform_unmapped]
    if wu.platform in values:
        return values[wu.platform]
    return values.get('default', None)


def make_report(e):
    """
    Formats a bug report.
    """
    import platform as _platform
    from wu import platform, platform_unmapped, platform_string, version, debug

    tb = traceback.format_exc(e)
    tb = '\n'.join('    ' + x for x in tb.splitlines())


    import gevent
    import greenlet
    import psutil
    from wu.plugins import PluginManager

    return """Webui bug report
--------------------


Info | Value
----- | -----
Webui | %s
Platform | %s / %s / %s
Architecture | %s
Python | %s
Debug | %s
Loaded plugins | %s

Library | Version
------- | -------
gevent | %s
greenlet | %s
psutil | %s


%s

            """ % (
            version,
            platform, platform_unmapped, platform_string,
            subprocess.check_output(['uname', '-mp']).strip(),
            '.'.join([str(x) for x in _platform.python_version_tuple()]),
            debug,
            ', '.join(sorted(PluginManager.get(wu.context).get_loaded_plugins_list())),

            gevent.__version__,
            greenlet.__version__,
            psutil.__version__,

            tb,
        )
