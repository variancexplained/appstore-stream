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
# Modified   : Thursday August 1st 2024 11:32:25 am                                                #
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
    AThrottleController,
    AThrottleStage,
    ExploitationPID,
    ExploitationPIDMultivariate,
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


# ------------------------------------------------------------------------------------------------ #
#                              ATHROTTLE RANDOM LATENCIES                                          #
# ------------------------------------------------------------------------------------------------ #


@pytest.fixture
def random_latencies():
    # Provide a list of random latencies for testing
    return [0.2, 0.5, 1.2, 0.7, 0.8, 1.1, 0.6, 1.0]


# ------------------------------------------------------------------------------------------------ #
#                              ATHROTTLE EXPLORATIONS STAGE                                        #
# ------------------------------------------------------------------------------------------------ #
@pytest.fixture
def exploration_stage():
    return ExplorationStage(
        base_rate=0.5,
        window_size=10,
        heatup_factor=0.1,
        cooldown_factor=0.05,
        exploration_threshold=1.2,
        temperature=0.3,
        min_rate=0.1,
        max_rate=2.0,
    )


# ------------------------------------------------------------------------------------------------ #
#                              ATHROTTLE EXPLOITATION PID                                          #
# ------------------------------------------------------------------------------------------------ #
@pytest.fixture
def exploitation_pid():
    return ExploitationPID(
        target_latency=1.0,
        kp=1.0,
        ki=0.1,
        kd=0.05,
        temperature=0.3,
        min_rate=0.1,
        max_rate=2.0,
        sample_time=0.01,
    )


# ------------------------------------------------------------------------------------------------ #
#                      ATHROTTLE EXPLOITATION PID MULTIVARIATE STAGE                               #
# ------------------------------------------------------------------------------------------------ #
@pytest.fixture
def exploitation_pid_multivariate():
    return ExploitationPIDMultivariate(
        target_mean_latency=1.0,
        target_cv_latency=0.01,
        target_std_latency=0.01,
        kp=[1.0, 1.2],
        ki=[0.1, 0.15],
        kd=[0.05, 0.07],
        temperature=0.3,
        min_rate=0.1,
        max_rate=2.0,
        sample_time=0.01,
    )


# ------------------------------------------------------------------------------------------------ #
#                         ATHROTTLE THROTTLE CONTROLLER STAGE                                      #
# ------------------------------------------------------------------------------------------------ #
@pytest.fixture
def controller(exploration_stage, exploitation_pid, exploitation_pid_multivariate):
    return AThrottleController(
        stages={
            AThrottleStage.BURNIN: exploration_stage,
            AThrottleStage.EXPLORATION: exploration_stage,
            AThrottleStage.EXPLOITATION_PID: exploitation_pid,
            AThrottleStage.EXPLOITATION_PID_MULTIVARIATE: exploitation_pid_multivariate,
        }
    )
