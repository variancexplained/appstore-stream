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
# Modified   : Monday July 29th 2024 02:51:26 pm                                                   #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
import json

import pandas as pd
import pytest

from appstorestream.container import AppStoreStreamContainer
from appstorestream.infra.base.config import Config

# ------------------------------------------------------------------------------------------------ #
collect_ignore = [""]


# ------------------------------------------------------------------------------------------------ #
#                                  SET ENV TO TEST                                                 #
# ------------------------------------------------------------------------------------------------ #
@pytest.fixture(scope="module", autouse=True)
def mode():
    config = Config()
    prior_mode = config.get_environment()
    config.change_environment(new_value="test")
    yield
    config.change_environment(new_value=prior_mode)


# ------------------------------------------------------------------------------------------------ #
#                              DEPENDENCY INJECTION                                                #
# ------------------------------------------------------------------------------------------------ #
@pytest.fixture(scope="function", autouse=True)
def container():
    container = AppStoreStreamContainer()
    container.init_resources()
    container.wire(
        packages=[
            "appstorestream.application.appdata.job",
        ]
    )

    return container


# ------------------------------------------------------------------------------------------------ #
#                                       APPDATA                                                    #
# ------------------------------------------------------------------------------------------------ #
@pytest.fixture(scope="function", autouse=False)
def appdata_json():
    FP = "tests/data/appdata.json"
    with open(FP, "r") as file:
        return json.load(file)
