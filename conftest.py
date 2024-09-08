#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Acquire                                                                    #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /conftest.py                                                                        #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Thursday July 25th 2024 04:11:44 pm                                                 #
# Modified   : Friday September 6th 2024 07:22:44 pm                                               #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #

import json
from typing import Any, Generator

import pytest
from dependency_injector.containers import Container

from appvocai.application.orchestration.project import Project
from appvocai.container import AppVoCAIContainer
from appvocai.core.enum import Category, DataType, ProjectFrequency, ProjectStatus
from appvocai.infra.base.config import Config

# ------------------------------------------------------------------------------------------------ #
collect_ignore = [
    "appvocai/infra/*.*",
    "appvocai/application/*.*",
    "appvocai/domain/openty/*.*",
]


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
@pytest.fixture(scope="function", autouse=False)
def container() -> Container:
    container = AppVoCAIContainer()
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
#                                    PROJECT                                                       #
# ------------------------------------------------------------------------------------------------ #
@pytest.fixture(scope="session", autouse=False)
def project() -> Project:
    """Creates a custom prometheus metrics registry."""
    return Project(
        category=Category.HEALTH_FITNESS,
        data_type=DataType.APPDATA,
        frequency=ProjectFrequency.DAILY,
        status=ProjectStatus.IDLE,
    )
