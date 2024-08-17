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
# Modified   : Saturday August 17th 2024 08:30:44 am                                               #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
import json
import time
from dataclasses import dataclass

import numpy as np
import pytest
from prometheus_client import CollectorRegistry

from appstorestream.application.metrics.extract import ExtractMetrics
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
#                                  RESPONSE OBJECT                                                 #
# ------------------------------------------------------------------------------------------------ #


@pytest.fixture(scope="session", autouse=False)
def response():
    """Mocks a response object."""

    @dataclass
    class Response:
        content_length: int = 0

    return Response()


# ------------------------------------------------------------------------------------------------ #
#                                  CUSTOM REGISTRY                                                 #
# ------------------------------------------------------------------------------------------------ #


@pytest.fixture(scope="session", autouse=False)
def custom_prometheus_registry():
    """Creates a custom prometheus metrics registry."""
    return CollectorRegistry()


# ------------------------------------------------------------------------------------------------ #
#                               EXTRACT METRICS                                                    #
# ------------------------------------------------------------------------------------------------ #


@pytest.fixture(scope="session", autouse=False)
def extract_metrics():
    """Creates an extract metrics object.."""
    RESPONSES = 10
    LATENCY_LOW = 0.1
    LATENCY_HIGH = 2
    RESPONSE_SIZE_LOW = 100
    RESPONSE_SIZE_HIGH = 1000
    metrics = ExtractMetrics()
    metrics.start()
    for i in range(1, RESPONSES + 1):
        metrics.request_count_total += 1
        metrics.add_latency(np.random.uniform(low=LATENCY_LOW, high=LATENCY_HIGH))
        response.content_length = np.random.randint(
            low=RESPONSE_SIZE_LOW, high=RESPONSE_SIZE_HIGH
        )
        metrics.add_response(response=response)
        if i % 5 == 0:
            metrics.log_http_error(return_code=303)
            metrics.log_http_error(return_code=404)
            metrics.log_http_error(return_code=550)
            metrics.log_http_error(return_code=600)
            metrics.success_failure_retries_total += 1

    metrics.stop()
    return metrics
