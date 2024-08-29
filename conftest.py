#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI - Acquire                                                                  #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /conftest.py                                                                        #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Thursday July 25th 2024 04:11:44 pm                                                 #
# Modified   : Thursday August 29th 2024 01:09:26 am                                               #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #

import json
import time
from dataclasses import dataclass
from typing import Any, Generator

import numpy as np
import pytest
from dependency_injector.containers import Container
from prometheus_client import CollectorRegistry

from appvocai.application.job.project import Project
from appvocai.application.task.base import Task
from appvocai.core.enum import *
from appvocai.infra.base.config import Config
from appvocai.infra.web.profile import (SessionHistory, SessionProfile,
                                        SessionStats)
from tests.test_infra.test_web.test_adapt import MockSessionHistory

# from appvocai.container import appvocaiContainer



# ------------------------------------------------------------------------------------------------ #
collect_ignore = ["appvocai/infra/web/asession.py"]
# mypy: ignore-errors


# ------------------------------------------------------------------------------------------------ #
#                                  SET ENV TO TEST                                                 #
# ------------------------------------------------------------------------------------------------ #
@pytest.fixture(scope="session", autouse=True)
def mode() -> Generator[Any, Any, Any]:
    config = Config()
    prior_mode = config.get_environment()
    config.change_environment(new_value="test")
    yield
    config.change_environment(new_value=prior_mode)


# ------------------------------------------------------------------------------------------------ #
#                              DEPENDENCY INJECTION                                                #
# ------------------------------------------------------------------------------------------------ #
# @pytest.fixture(scope="function", autouse=True)
# def container() -> Container:
#     container = appvocaiContainer()
#     container.init_resources()
#     container.wire(modules=["appvocai.infra.web.adapter"])
#     return container


# ------------------------------------------------------------------------------------------------ #
#                                       APPDATA                                                    #
# ------------------------------------------------------------------------------------------------ #
@pytest.fixture(scope="function", autouse=False)
def appdata_json() -> Any:
    FP = "tests/data/appdata.json"
    with open(FP, "r") as file:
        return json.load(file)


# ------------------------------------------------------------------------------------------------ #
#                                  CUSTOM REGISTRY                                                 #
# ------------------------------------------------------------------------------------------------ #
@pytest.fixture(scope="session", autouse=False)
def custom_prometheus_registry() -> CollectorRegistry:
    """Creates a custom prometheus metrics registry."""
    return CollectorRegistry()


# ------------------------------------------------------------------------------------------------ #
#                                 SESSION HISTORY                                                  #
# ------------------------------------------------------------------------------------------------ #
@pytest.fixture(scope="function", autouse=False)
def session_history() -> SessionHistory:
    """Creates a session profile object."""
    history = SessionHistory()
    for m in range(10):
        profile = SessionProfile()
        k = m / 100
        time.sleep(k)
        profile.send()
        for i in range(10):
            profile.send()
            j = i / 100
            time.sleep(j)
            profile.add_latency(latency=np.random.random())
        profile.recv()
        history.add_metrics(profile=profile)
    return history


# ------------------------------------------------------------------------------------------------ #
#                                     ADAPTER                                                      #
# ------------------------------------------------------------------------------------------------ #
# @pytest.fixture(scope="function", autouse=False)
# def adapter(container: appvocaiContainer) -> Adapter:

#     baseline = container.session.baseline()
#     rate = container.session.rate()
#     concurrency = container.session.concurrency()
#     exploit = container.session.exploit()
#     adapter = container.session.adapter()

#     baseline.next_stage = rate
#     rate.next_stage = concurrency
#     concurrency.next_stage = exploit
#     exploit.next_stage = baseline

#     return adapter


# ------------------------------------------------------------------------------------------------ #
#                                      MOCK HISTORY                                                #
# ------------------------------------------------------------------------------------------------ #
@pytest.fixture(scope="session", autouse=False)
def mock_history(*args, **kwargs) -> MockSessionHistory:
    return MockSessionHistory().get_latency_stats


# ------------------------------------------------------------------------------------------------ #
#                                       PROJECT                                                    #
# ------------------------------------------------------------------------------------------------ #
@pytest.fixture(scope="session", autouse=False)
def project(*args, **kwargs) -> Project:
    return Project(category=Category.EDUCATION, content_type=ContentType.APPREVIEW)


# ------------------------------------------------------------------------------------------------ #
#                                    MOCK TASK                                                     #
# ------------------------------------------------------------------------------------------------ #
@pytest.fixture(scope="session", autouse=False)
def mock_task(*args, **kwargs) -> Task:
    class MockTask(Task):
        def execute(*args, **kwargs):
            pass
    return MockTask()

