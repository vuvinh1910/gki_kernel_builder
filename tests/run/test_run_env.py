from pytest_mock.plugin import MockType


import os
import types

from pytest import MonkeyPatch
from pytest_mock import MockerFixture
import run


def test_env_var(mocker: MockerFixture, monkeypatch: MonkeyPatch) -> None:
    fake: MockType = mocker.patch("kernel_builder.main.KernelBuilder", autospec=True)

    ns = types.SimpleNamespace(
        command="build", ksu="NEXT", susfs=False, lxc=True, verbose=False
    )

    run.cmd_build(ns)

    fake.assert_called_once_with()
    fake.return_value.run_build.assert_called_once()

    assert os.environ["KSU"] == "NEXT"
    assert os.environ["SUSFS"] == "false"
    assert os.environ["LXC"] == "true"
    assert os.environ["LOCAL_RUN"] == "true"
    assert os.environ["VERBOSE_OUTPUT"] == "false"
