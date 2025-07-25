from pathlib import Path


import os
import subprocess
from kernel_builder.constants import PATCHES, WORKSPACE
from kernel_builder.utils.command import apply_patch
from kernel_builder.utils.github import GithubAPI
from kernel_builder.utils.log import log
from kernel_builder.utils.source import SourceManager
from kernel_builder.utils import env


class KSUInstaller:
    VARIANT_URLS: dict[str, str] = {
        "NEXT": "https://raw.githubusercontent.com/KernelSU-Next/KernelSU-Next/next/kernel/setup.sh",
        "SUKI": "https://raw.githubusercontent.com/SukiSU-Ultra/SukiSU-Ultra/main/kernel/setup.sh",
    }

    def __init__(self) -> None:
        self.source: SourceManager = SourceManager()
        self.gh_api: GithubAPI = GithubAPI()
        self.variant: str = env.ksu_variant()
        self.use_susfs: bool = env.susfs_enabled()

    def _install_ksu(self, url: str, ref: str | None) -> None:
        if not self.source.is_simplified(url):
            url = self.source.git_simplifier(url)

        user, repo = url.split(":", 1)[1].split("/", 1)
        latest_tag: str = self.gh_api.fetch_latest_tag(
            f"https://api.github.com/repos/{user}/{repo}/releases/latest"
        )

        if not ref:
            ref = latest_tag

        os.environ["KSU_VERSION"] = latest_tag

        setup_url = f"https://raw.githubusercontent.com/{url.split(':', 1)[1]}/{ref}/kernel/setup.sh"

        log(f"Installing KernelSU from {url} | {ref}")

        # Temporary fix
        script: str = subprocess.run(
            ["curl", "-LSs", setup_url],
            capture_output=True,
            check=True,
            text=True,
        ).stdout

        subprocess.run(
            ["bash", "-s", ref],
            input=script,
            cwd=str(WORKSPACE),
            check=True,
            text=True,
        )

    def _patch_manual_hooks(self) -> None:
        unsupported: list[str] = ["NONE", "OFFICIAL"]
        if self.variant.upper() in unsupported:
            return
        hook_patch: Path = PATCHES / "manual_hooks.patch"
        apply_patch(hook_patch, check=False, cwd=WORKSPACE)

    def install(self) -> None:
        variant: str = self.variant.upper()

        match variant:
            case "NONE":
                return
            case "OFFICIAL":
                self._install_ksu("github.com:tiann/KernelSU", "main")
            case "NEXT":
                self._install_ksu("github.com:KernelSU-Next/kernelSU-Next", "next")
            case "SUKI":
                if self.use_susfs:
                    self._install_ksu(
                        "github.com:SukiSU-Ultra/SukiSU-Ultra", "susfs-main"
                    )
                else:
                    self._install_ksu("github.com:SukiSU-Ultra/SukiSU-Ultra", "nongki")
            case _:
                return

        self._patch_manual_hooks()


if __name__ == "__main__":
    raise SystemExit("This file is meant to be imported, not executed.")
