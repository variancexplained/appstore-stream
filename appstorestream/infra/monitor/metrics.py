#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppStoreStream: Apple App Data and Reviews, Delivered!                              #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appstorestream/infra/monitor/metrics.py                                            #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appstore-stream.git                             #
# ------------------------------------------------------------------------------------------------ #
# Created    : Monday July 29th 2024 06:13:17 pm                                                   #
# Modified   : Monday July 29th 2024 11:33:56 pm                                                   #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
import random
import time

from prometheus_client import Counter, Gauge, Histogram, start_http_server


# ------------------------------------------------------------------------------------------------ #
class Metrics:
    def __init__(self, port: int = 8000) -> None:
        # Group 1: Request Metrics
        self.duration = Histogram("duration", "Concurrent request duration in seconds.")
        self.request_delay = Histogram(
            "request_delay_seconds", "Request delay in seconds"
        )
        self.request_delay_average = Gauge(
            "request_delay_average_seconds", "Average request delay in seconds"
        )
        self.request_latency = Histogram(
            "request_latency_seconds", "Request latency in seconds"
        )
        self.request_latency_average = Gauge(
            "request_latency_average_seconds", "Average request latency in seconds"
        )

        # Group 2: Progress Metrics
        self.record_count = Counter("record_count", "Total number of records processed")
        self.request_count = Counter("request_count", "Total number of requests")
        self.response_count = Counter("response_count", "Total number of responses")

        # Group 3: Performance Metrics
        self.records_per_second = Gauge(
            "records_per_second", "Records processed per second"
        )
        self.requests_per_second = Gauge(
            "requests_per_second", "Requests processed per second"
        )
        self.responses_per_second = Gauge(
            "responses_per_second", "Responses processed per second"
        )
        self.runtime_histogram = Histogram(
            "runtime_seconds", "Runtime of jobs in seconds"
        )

        # Group 4: Error Metrics
        self.client_error_rate = Gauge("client_error_rate", "Client error rate")
        self.client_errors = Counter("client_errors", "Total number of client errors")
        self.redirect_error_rate = Gauge("redirect_error_rate", "Redirect error rate")
        self.redirect_errors = Counter(
            "redirect_errors", "Total number of redirect errors"
        )
        self.data_error_rate = Gauge("data_error_rate", "Data error rate")
        self.data_errors = Counter("data_errors", "Total number of data errors")
        self.retries = Counter("retries", "Total number of retries")
        self.server_error_rate = Gauge("server_error_rate", "Server error rate")
        self.server_errors = Counter("server_errors", "Total number of server errors")
        self.unknown_error_rate = Gauge("unknown_error_rate", "Unknown error rate")
        self.unknown_errors = Counter(
            "unknown_errors", "Total number of unknown errors"
        )
        self.page_not_found_error_rate = Gauge(
            "page_not_found_error_rate", "Page not found error rate"
        )
        self.page_not_found_errors = Counter(
            "page_not_found_errors", "Total number of page not found errors"
        )
        self.total_error_rate = Gauge("total_error_rate", "Total error rate")
        self.total_errors = Counter("total_errors", "Total number of errors")

        # Group 5: System Metrics
        self.cpu_usage = Gauge("cpu_usage", "CPU usage")
        self.memory_usage = Gauge("memory_usage", "Memory usage")

        self.start_server(port=port)

    def start_server(self, port=8000):
        start_http_server(port)
