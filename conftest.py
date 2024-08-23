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
# Modified   : Friday August 23rd 2024 02:54:56 pm                                                 #
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
from appstorestream.infra.web.profile import SessionHistory, SessionProfile

# ------------------------------------------------------------------------------------------------ #
collect_ignore = [""]
# mypy: allow-untyped-calls


# ------------------------------------------------------------------------------------------------ #
#                                  SET ENV TO TEST                                                 #
# ------------------------------------------------------------------------------------------------ #
@pytest.fixture(scope="module", autouse=True)
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
