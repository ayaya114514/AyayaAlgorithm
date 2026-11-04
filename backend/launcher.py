"""Resource guard for trusted local practice; not a hostile-code sandbox."""

import math
import os
import resource
import sys


def main():
    seconds, memory_mb = float(sys.argv[1]), int(sys.argv[2])
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    resource.setrlimit(resource.RLIMIT_FSIZE, (1024 * 1024, 1024 * 1024))
    cpu = max(1, math.ceil(seconds))
    resource.setrlimit(resource.RLIMIT_CPU, (cpu, cpu + 1))
    resource.setrlimit(resource.RLIMIT_NOFILE, (64, 64))
    # macOS address-space limits can prevent dyld from starting otherwise valid code.
    # Do not advertise a memory verdict there. Linux can enforce RLIMIT_AS.
    if sys.platform.startswith("linux"):
        memory = memory_mb * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_AS, (memory, memory))
    os.execv(sys.argv[3], sys.argv[3:])


if __name__ == "__main__":
    main()
