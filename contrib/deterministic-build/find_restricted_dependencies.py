#!/usr/bin/env python3
import sys

try:
    import requests
except ImportError as e:
    sys.exit(f"Error: {str(e)}. Try 'sudo python3 -m pip install <module-name>'")


def check_restriction(p, r):
    # See: https://www.python.org/dev/peps/pep-0496/
    # Hopefully we don't need to parse the whole microlanguage
    if "extra" in r and "[" not in p:
        return False
    for marker in ["os_name", "platform_release", "sys_platform", "platform_system"]:
        if marker in r:
            return True


for p in sys.stdin.read().split():
    p = p.strip()
    if not p:
        continue
    assert (
        "==" in p
    ), f"This script expects a list of packages with pinned version, e.g. package==1.2.3, not {p}"
    p, v = p.rsplit("==", 1)
    try:
        data = requests.get(f"https://pypi.org/pypi/{p}/{v}/json").json()["info"]
    except ValueError:
        raise Exception(f"Package could not be found: {p}=={v}")
    try:
        for r in data["requires_dist"]:  # type: str
            if ";" not in r:
                continue
            # example value for "r" at this point: "pefile (>=2017.8.1) ; sys_platform == \"win32\""
            dep, restricted = r.split(";", 1)
            dep = dep.strip()
            restricted = restricted.strip()
            dep_basename = dep.split(" ")[0]
            if check_restriction(dep, restricted):
                print(dep_basename, sep=" ")
                print(
                    f"Installing {dep} from {p} although it is only needed for {restricted}",
                    file=sys.stderr,
                )
    except TypeError:
        # Has no dependencies at all
        continue

