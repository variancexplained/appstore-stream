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
# Modified   : Friday August 2nd 2024 12:38:33 pm                                                  #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
import json

import pandas as pd
import pytest

from appstorestream.container import AppStoreStreamContainer
from appstorestream.infra.base.config import Config
from appstorestream.infra.web.throttle import (
    AThrottleCore,
    BurninStage,
    ExploitPIDStage,
    ExplorationStage,
)

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
    container.wire(modules=["appstorestream.infra.web.throttle"])

    return container


# ------------------------------------------------------------------------------------------------ #
#                                       APPDATA                                                    #
# ------------------------------------------------------------------------------------------------ #
@pytest.fixture(scope="function", autouse=False)
def appdata_json():
    FP = "tests/data/appdata.json"
    with open(FP, "r") as file:
        return json.load(file)


# ------------------------------------------------------------------------------------------------ #
#                              ATHROTTLE RANDOM LATENCIES                                          #
# ------------------------------------------------------------------------------------------------ #


@pytest.fixture(scope="function", autouse=False)
def random_latencies():
    # Provide a list of random latencies for testing
    return [0.2, 0.5, 1.2, 0.7, 0.8, 1.1, 0.6, 1.0]


# ------------------------------------------------------------------------------------------------ #
#                                   ATHROTTLE METRICS                                              #
# ------------------------------------------------------------------------------------------------ #
@pytest.fixture(scope="function", autouse=False)
def athrottle_acore():
    # Create the initial acore object that is initialized by the controller and fed to the burnin stage
    return AThrottleCore(current_rate=50, min_rate=10)


# ------------------------------------------------------------------------------------------------ #
#                                ATHROTTLE BURNIN STAGE                                            #
# ------------------------------------------------------------------------------------------------ #
@pytest.fixture(scope="function", autouse=False)
def burnin_stage(container, athrottle_acore):
    return BurninStage(
        acore=athrottle_acore,
        controller=container.athrottle.controller(),
        stage_length=1,
    )


# ------------------------------------------------------------------------------------------------ #
#                            ATHROTTLE EXPLORATION STAGE                                           #
# ------------------------------------------------------------------------------------------------ #
@pytest.fixture(scope="function", autouse=False)
def exploration_stage(container, athrottle_acore):
    return ExplorationStage(
        acore=athrottle_acore,
        controller=container.athrottle.controller(),
        stage_length=5,
    )


# ------------------------------------------------------------------------------------------------ #
#                           ATHROTTLE EXPLOITATION STAGE                                           #
# ------------------------------------------------------------------------------------------------ #
@pytest.fixture(scope="function", autouse=False)
def exploitation_stage(container, athrottle_acore):
    return ExploitPIDStage(
        acore=athrottle_acore,
        controller=container.athrottle.controller(),
        stage_length=600,
        kp=-0.1,
        ki=-0.01,
        kd=-0.05,
        target=0.40917980243766183,
    )
