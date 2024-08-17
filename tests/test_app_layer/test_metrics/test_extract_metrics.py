#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppStoreStream: Apple App Data and Reviews, Delivered!                              #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /tests/test_app_layer/test_metrics/test_extract_metrics.py                          #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appstore-stream.git                             #
# ------------------------------------------------------------------------------------------------ #
# Created    : Friday August 16th 2024 12:03:24 pm                                                 #
# Modified   : Friday August 16th 2024 02:29:00 pm                                                 #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
import inspect
import logging
import time
from datetime import datetime

import numpy as np
import pytest

from appstorestream.application.metrics.extract import (
    ExtractMetrics,
    ExtractMetricServer,
)

# ------------------------------------------------------------------------------------------------ #
# pylint: disable=missing-class-docstring, line-too-long
# ------------------------------------------------------------------------------------------------ #
# ------------------------------------------------------------------------------------------------ #
logger = logging.getLogger(__name__)
# ------------------------------------------------------------------------------------------------ #
double_line = f"\n{100 * '='}"
single_line = f"\n{100 * '-'}"


@pytest.mark.extract_metrics
@pytest.mark.metrics
class TestExtractMetrics:  # pragma: no cover
    # ============================================================================================ #
    def test_extract_metrics(self, response, caplog):
        start = datetime.now()
        logger.info(
            f"\n\nStarted {self.__class__.__name__} {inspect.stack()[0][3]} at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(double_line)
        # ---------------------------------------------------------------------------------------- #
        JOB_ID = f"test_job {datetime.now().strftime('%m/%d/%Y-%H:%M:%S')}"
        PORT = 8020
        DATASET = "TestData"
        RESPONSES = 10
        LATENCY = 0.1
        DURATION = RESPONSES * LATENCY
        LATENCY_LOW = 0.1
        LATENCY_HIGH = 2
        RESPONSE_SIZE_LOW = 100
        RESPONSE_SIZE_HIGH = 1000
        metrics = ExtractMetrics()
        metrics.start()
        for i in range(1, RESPONSES + 1):
            metrics.request_count_total += 1
            time.sleep(LATENCY)
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

        # Runtime Metrics
        assert metrics.runtime_start_timestamp_seconds > 0
        assert metrics.runtime_stop_timestamp_seconds > 0
        assert metrics.runtime_duration_seconds > RESPONSES * LATENCY
        assert metrics.runtime_duration_seconds > 0

        # Request Metrics
        assert metrics.request_count_total == 10
        assert metrics.request_per_second_ratio < RESPONSES / DURATION
        assert metrics.request_per_second_ratio > 0

        # Response Metrics
        assert metrics.response_count_total == 10
        assert metrics.response_per_second_ratio > 0
        assert metrics.response_average_latency_seconds > LATENCY_LOW
        assert metrics.response_average_latency_seconds < LATENCY_HIGH
        assert metrics.response_latency_seconds_total > LATENCY_LOW * RESPONSES
        assert metrics.response_latency_seconds_total < LATENCY_HIGH * RESPONSES
        assert metrics.response_average_size_bytes > RESPONSE_SIZE_LOW
        assert metrics.response_average_size_bytes < RESPONSE_SIZE_HIGH
        assert metrics.response_size_bytes_total > RESPONSE_SIZE_LOW * RESPONSES
        assert metrics.response_size_bytes_total < RESPONSE_SIZE_HIGH * RESPONSES

        # Success/Failure Metrics
        assert metrics.success_failure_retries_total == RESPONSES // 5
        assert metrics.success_failure_errors_total == RESPONSES // 5 * 4
        assert metrics.success_failure_redirect_errors_total == RESPONSES // 5
        assert metrics.success_failure_client_errors_total == RESPONSES // 5
        assert metrics.success_failure_server_errors_total == RESPONSES // 5
        assert metrics.success_failure_unknown_errors_total == RESPONSES // 5
        assert (
            metrics.success_failure_request_failure_rate_ratio
            == RESPONSES // 5 * 4 / RESPONSES
        )
        assert (
            metrics.success_failure_request_success_rate_ratio
            == 1 - metrics.success_failure_request_failure_rate_ratio
        )

        # Throttle Metrics
        assert metrics.throttle_concurrency_efficiency_ratio > 0
        assert metrics.throttle_average_latency_efficiency_ratio > 0
        assert metrics.throttle_total_latency_efficiency_ratio > 0

        # Update Metrics
        metric_server = ExtractMetricServer(job_id=JOB_ID, dataset=DATASET, port=PORT)
        metric_server.update_metrics(metrics=metrics)

        # ---------------------------------------------------------------------------------------- #
        end = datetime.now()
        duration = round((end - start).total_seconds(), 1)

        logger.info(
            f"\n\nCompleted {self.__class__.__name__} {inspect.stack()[0][3]} in {duration} seconds at {start.strftime('%I:%M:%S %p')} on {start.strftime('%m/%d/%Y')}"
        )
        logger.info(single_line)
