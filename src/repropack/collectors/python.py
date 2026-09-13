"""Python environment information collection."""

import platform
import sys
from importlib import metadata

from repropack.models import PythonInfo


def collect_python_info() -> PythonInfo:
    """Collect Python runtime metadata and installed package versions."""
    packages = {
        name: distribution.version
        for distribution in metadata.distributions()
        if (name := distribution.metadata.get("Name")) is not None
    }

    return PythonInfo(
        version=platform.python_version(),
        implementation=platform.python_implementation(),
        in_virtual_environment=sys.prefix != sys.base_prefix,
        packages=dict(sorted(packages.items(), key=lambda item: item[0].lower())),
    )
