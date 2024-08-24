#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppStoreStream: Apple App Data and Reviews, Delivered!                              #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /conftest.py                                                                        #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appstore-stream.git                             #
# ------------------------------------------------------------------------------------------------ #
# Created    : Thursday July 25th 2024 04:11:44 pm                                                 #
# Modified   : Saturday August 24th 2024 03:22:23 pm                                               #
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

from appstorestream.container import AppStoreStreamContainer
from appstorestream.infra.base.config import Config
from appstorestream.infra.web.adapter import Adapter
from appstorestream.infra.web.profile import (
    SessionHistory,
    SessionProfile,
    SessionStats,
)
from tests.test_infra.test_web.test_adapt import MockSessionHistory

# ------------------------------------------------------------------------------------------------ #
collect_ignore = [""]
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
@pytest.fixture(scope="function", autouse=True)
def container() -> Container:
    container = AppStoreStreamContainer()
    container.init_resources()
    container.wire(modules=["appstorestream.infra.web.adapter"])
    return container


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
@pytest.fixture(scope="function", autouse=False)
def adapter(container: AppStoreStreamContainer) -> Adapter:

    baseline = container.session.baseline()
    rate = container.session.rate()
    concurrency = container.session.concurrency()
    exploit = container.session.exploit()
    adapter = container.session.adapter()

    baseline.next_stage = rate
    rate.next_stage = concurrency
    concurrency.next_stage = exploit
    exploit.next_stage = baseline

    return adapter


# ------------------------------------------------------------------------------------------------ #
#                                      MOCK HISTORY                                                #
# ------------------------------------------------------------------------------------------------ #
@pytest.fixture(scope="session", autouse=False)
def mock_history(*args, **kwargs) -> MockSessionHistory:
    return MockSessionHistory().get_latency_stats
