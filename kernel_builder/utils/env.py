import os


def _bool_env(var: str, default: str = "false") -> bool:
    return os.getenv(var, default).lower() in ("true", "1", "yes")


def ksu_variant(default: str = "NONE") -> str:
    return os.getenv("KSU", default).upper()


def susfs_enabled(default: str = "false") -> bool:
    return _bool_env("SUSFS", default)


def lxc_enabled(default: str = "false") -> bool:
    return _bool_env("LXC", default)


def local_run(default: str = "false") -> bool:
    return _bool_env("LOCAL_RUN", default)


def verbose_enabled(default: str = "false") -> bool:
    return _bool_env("VERBOSE_OUTPUT", default)
