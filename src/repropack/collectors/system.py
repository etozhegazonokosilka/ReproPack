"""System information collection."""

import platform

from repropack.models import SystemInfo


def collect_system_info() -> SystemInfo:
    """Collect safe operating-system metadata."""
    return SystemInfo(
        os_name=platform.system(),
        os_version=platform.version(),
        architecture=platform.machine(),
    )
