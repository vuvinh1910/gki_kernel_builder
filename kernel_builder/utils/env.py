import os


def _bool_env(var: str, default: str = "false") -> bool:
    return os.getenv(var, default).lower() in ("true", "1", "yes")


def ksu_variant(default: str = "NONE") -> str:
    return os.getenv("KSU", default).upper()


def susfs_enabled(default: str = "false") -> bool:
    return _bool_env("SUSFS", default)


def lxc_enabled(default: str = "false") -> bool:
    return _bool_env("LXC", default)
