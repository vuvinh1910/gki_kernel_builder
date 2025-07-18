#!/usr/bin/env python3
# encoding: utf-8

from argparse import ArgumentParser, Namespace, BooleanOptionalAction
import argparse
import os
from pathlib import Path
import shutil
import platform
from kernel_builder.utils.log import log


def build_parser() -> ArgumentParser:
    parser: ArgumentParser = argparse.ArgumentParser(description="Kernel Builder")
    sub = parser.add_subparsers(dest="command", required=True)

    # Build
    build = sub.add_parser(
        "build",
        help="Compile a kernel image",
        usage="%(prog)s build [-v/--verbose] [-k/--ksu {NONE,NEXT,SUKI}] [-s/--susfs] [-l/--lxc]",
    )
    build.add_argument(
        "-v",
        "--verbose",
        help="Enable verbose output",
        action=BooleanOptionalAction,
        default=False,
    )
    build.add_argument(
        "-k",
        "--ksu",
        choices=["NONE", "NEXT", "SUKI"],
        help="KernelSU variant (default: %(default)s)",
        default=os.getenv("KSU", "NONE").upper(),
    )
    build.add_argument(
        "-s",
        "--susfs",
        help="Enable SUSFS support",
        action=BooleanOptionalAction,
        default=os.getenv("SUSFS", "false").lower(),
    )
    build.add_argument(
        "-l",
        "--lxc",
        help="Enable LXC support",
        action=BooleanOptionalAction,
        default=os.getenv("LXC", "false").lower(),
    )

    # Clean
    clean: ArgumentParser = sub.add_parser("clean", help="Remove build artifacts")
    clean.add_argument(
        "-a",
        "--all",
        action=BooleanOptionalAction,
        default=False,
        help="Also delete dist/ (out) directory",
    )

    return parser


def cmd_build(args: Namespace) -> None:
    if args.ksu == "NONE" and args.susfs:
        raise SystemExit("SUSFS requires KernelSU ≠ NONE")

    os.environ["KSU"] = args.ksu
    os.environ["SUSFS"] = str(args.susfs).lower()
    os.environ["LXC"] = str(args.lxc).lower()
    os.environ["VERBOSE_OUTPUT"] = str(args.verbose).lower()

    from kernel_builder.kernel_builder import KernelBuilder

    builder: KernelBuilder = KernelBuilder()
    builder.run_build()


def cmd_clean(args: Namespace) -> None:
    from kernel_builder.config.config import OUTPUT
    from kernel_builder.constants import WORKSPACE, TOOLCHAIN, ROOT

    build_folder: list[Path] = [WORKSPACE, TOOLCHAIN]

    if args.all:
        build_folder.append(OUTPUT)
    for folder in build_folder:
        shutil.rmtree(folder, ignore_errors=True)

    github_exported_env: Path = ROOT / "github.env"
    github_exported_env.unlink(missing_ok=True)


def main():
    parser: ArgumentParser = build_parser()
    args: Namespace = parser.parse_args()

    match args.command:
        case "build":
            cmd_build(args)
        case "clean":
            cmd_clean(args)
        case _:
            parser.error("Unknown command")


if __name__ == "__main__":
    try:
        if platform.system() != "Linux":
            raise RuntimeError("Only Linux machines supported")

        main()
    except (Exception, RuntimeError) as err:
        log(str(err), "error")
