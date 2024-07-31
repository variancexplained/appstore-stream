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
# Modified   : Wednesday July 31st 2024 02:38:58 pm                                                #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
import random
import time

# ------------------------------------------------------------------------------------------------ #
from prometheus_client import Counter, Gauge, Histogram, start_http_server


class Metrics:
    def __init__(self, port: int = 8000) -> None:
        # Group 1: Runtime Metrics
        self.runtime_start_timestamp = Gauge(
            "runtime_start_timestamp_seconds",
            "Start time in timestamp seconds",
            ["job_id", "dataset", "stage"],
        )
        self.runtime_end_timestamp = Gauge(
            "runtime_end_timestamp_seconds",
            "End time in timestamp seconds",
            ["job_id", "dataset", "stage"],
        )
        self.runtime_seconds = Gauge(
            "runtime_seconds",
            "Runtime including all stages of process",
            ["job_id", "dataset", "stage"],
        )
        self.runtime_seconds_total = Counter(
            "runtime_seconds_total",
            "Runtime including all stages of process",
            ["job_id", "dataset", "stage"],
        )

        # Group 2: Session Metrics
        self.session_total_average_latency_seconds_total = Counter(
            "session_total_average_latency_seconds_total",
            "Total average latency",
            ["job_id", "dataset", "stage"],
        )
        self.session_average_latency_seconds = Histogram(
            "session_average_latency_seconds",
            "Latency Histogram",
            ["job_id", "dataset", "stage"],
        )
        self.session_total_latency_seconds_total = Counter(
            "session_total_latency_seconds_total",
            "Sum of request latencies",
            ["job_id", "dataset", "stage"],
        )
        self.session_duration_seconds_total = Counter(
            "session_duration_seconds_total",
            "Time taken to obtain a concurrent response from request",
            ["job_id", "dataset", "stage"],
        )
        self.session_delay_seconds_total = Counter(
            "session_delay_seconds_total",
            "Total delay accumulated over sessions",
            ["job_id", "dataset", "stage"],
        )
        self.session_delay_seconds = Histogram(
            "session_delay_seconds",
            "Total delay for a session",
            ["job_id", "dataset", "stage"],
        )
        self.session_concurrency = Counter(
            "session_concurrency",
            "Number of concurrent requests",
            ["job_id", "dataset", "stage"],
        )

        # Group 3: Throttle Metrics
        self.throttle_pid_error = Gauge(
            "throttle_pid_error", "PID Error", ["job_id", "dataset", "stage"]
        )
        self.throttle_pid_proportional = Gauge(
            "throttle_pid_proportional",
            "PID Proportional",
            ["job_id", "dataset", "stage"],
        )
        self.throttle_pid_integral = Gauge(
            "throttle_pid_integral", "PID Integral", ["job_id", "dataset", "stage"]
        )
        self.throttle_pid_derivative = Gauge(
            "throttle_pid_derivative", "PID Derivative", ["job_id", "dataset", "stage"]
        )
        self.throttle_adjustments_total = Gauge(
            "throttle_adjustments_total",
            "Total number of throttle adjustments made",
            ["job_id", "dataset", "stage"],
        )
        self.throttle_concurrency_efficiency_ratio = Gauge(
            "throttle_concurrency_efficiency_ratio",
            "Average Latency / (Duration / Concurrency)",
            ["job_id", "dataset", "stage"],
        )
        self.throttle_average_latency_efficiency_ratio = Gauge(
            "throttle_average_latency_efficiency_ratio",
            "Average Latency / Duration",
            ["job_id", "dataset", "stage"],
        )
        self.throttle_total_latency_efficiency_ratio = Gauge(
            "throttle_total_latency_efficiency_ratio",
            "Total Latency / Duration",
            ["job_id", "dataset", "stage"],
        )
        self.throttle_latency_standard_deviation_seconds = Gauge(
            "throttle_latency_standard_deviation_seconds",
            "Standard deviation of latency over the stage",
            ["job_id", "dataset", "stage"],
        )
        self.throttle_latency_coefficient_of_variation_seconds = Gauge(
            "throttle_latency_coefficient_of_variation_seconds",
            "Ratio of Standard Deviation and Mean Latency",
            ["job_id", "dataset", "stage"],
        )

        # Group 4: Throughput Metrics
        self.throughput_records_per_duration_seconds = Gauge(
            "throughput_records_per_duration_seconds",
            "Records per duration",
            ["job_id", "dataset", "stage"],
        )
        self.throughput_records_per_runtime_seconds = Gauge(
            "throughput_records_per_runtime_seconds",
            "Records per runtime",
            ["job_id", "dataset", "stage"],
        )
        self.throughput_requests_per_duration_seconds = Gauge(
            "throughput_requests_per_duration_seconds",
            "Requests per duration",
            ["job_id", "dataset", "stage"],
        )
        self.throughput_requests_per_runtime_seconds = Gauge(
            "throughput_requests_per_runtime_seconds",
            "Requests per runtime",
            ["job_id", "dataset", "stage"],
        )
        self.throughput_responses_per_duration_seconds = Gauge(
            "throughput_responses_per_duration_seconds",
            "Responses per duration",
            ["job_id", "dataset", "stage"],
        )
        self.throughput_responses_per_runtime_seconds = Gauge(
            "throughput_responses_per_runtime_seconds",
            "Responses per runtime",
            ["job_id", "dataset", "stage"],
        )

        # Group 5: Workload Metrics
        self.workload_requests_total = Counter(
            "workload_requests_total",
            "Total requests processed for a session",
            ["job_id", "dataset", "stage"],
        )
        self.workload_response_total = Counter(
            "workload_response_total",
            "Total responses returned for a session",
            ["job_id", "dataset", "stage"],
        )
        self.workload_records_total = Counter(
            "workload_records_total",
            "Total records returned for a session",
            ["job_id", "dataset", "stage"],
        )
        self.workload_seconds_total = Gauge(
            "workload_seconds_total",
            "Duration * Concurrency",
            ["job_id", "dataset", "stage"],
        )

        # Group 6: Success/Failure Metrics
        self.success_failure_client_errors_total = Counter(
            "success_failure_client_errors_total",
            "Total client errors for a job",
            ["job_id", "dataset", "stage"],
        )
        self.success_failure_data_errors_total = Counter(
            "success_failure_data_errors_total",
            "Total data errors for a job",
            ["job_id", "dataset", "stage"],
        )
        self.success_failure_errors_total = Counter(
            "success_failure_errors_total",
            "Total errors for a job",
            ["job_id", "dataset", "stage"],
        )
        self.success_failure_page_not_found_errors_total = Counter(
            "success_failure_page_not_found_errors_total",
            "Total page-not-found errors for a job",
            ["job_id", "dataset", "stage"],
        )
        self.success_failure_redirect_errors_total = Counter(
            "success_failure_redirect_errors_total",
            "Total redirect errors for a job",
            ["job_id", "dataset", "stage"],
        )
        self.success_failure_server_errors_total = Counter(
            "success_failure_server_errors_total",
            "Total server errors for a job",
            ["job_id", "dataset", "stage"],
        )
        self.success_failure_unknown_errors_total = Counter(
            "success_failure_unknown_errors_total",
            "Total unknown errors for a job",
            ["job_id", "dataset", "stage"],
        )
        self.success_failure_client_error_rate_ratio = Gauge(
            "success_failure_client_error_rate_ratio",
            "Client error rate for a job",
            ["job_id", "dataset", "stage"],
        )
        self.success_failure_data_error_rate_ratio = Gauge(
            "success_failure_data_error_rate_ratio",
            "Data error rate for a job",
            ["job_id", "dataset", "stage"],
        )
        self.success_failure_error_rate_ratio = Gauge(
            "success_failure_error_rate_ratio",
            "Error Rate for a Job",
            ["job_id", "dataset", "stage"],
        )
        self.success_failure_page_not_found_error_rate_ratio = Gauge(
            "success_failure_page_not_found_error_rate_ratio",
            "Page-not-found error rate for a job",
            ["job_id", "dataset", "stage"],
        )
        self.success_failure_redirect_error_rate_ratio = Gauge(
            "success_failure_redirect_error_rate_ratio",
            "Redirect error rate for a job",
            ["job_id", "dataset", "stage"],
        )
        self.success_failure_server_error_rate_ratio = Gauge(
            "success_failure_server_error_rate_ratio",
            "Server error rate for a job",
            ["job_id", "dataset", "stage"],
        )
        self.success_failure_unknown_error_rate_ratio = Gauge(
            "success_failure_unknown_error_rate_ratio",
            "Unknown error rate for a job",
            ["job_id", "dataset", "stage"],
        )
        self.success_failure_successful_requests = Counter(
            "success_failure_successful_requests",
            "Successful Requests",
            ["job_id", "dataset", "stage"],
        )
        self.success_failure_success_rate_ratio = Gauge(
            "success_failure_success_rate_ratio",
            "Rate of successful requests",
            ["job_id", "dataset", "stage"],
        )
        self.success_failure_retries = Counter(
            "success_failure_retries",
            "Number of retries",
            ["job_id", "dataset", "stage"],
        )
        self.success_failure_retry_rate_ratio = Gauge(
            "success_failure_retry_rate_ratio",
            "Rate of retries",
            ["job_id", "dataset", "stage"],
        )

        # Group 7: System Metrics
        self.system_network_io_bytes = Gauge(
            "system_network_io_bytes", "Network I/O", ["job_id", "dataset", "stage"]
        )
        self.system_disk_io_bytes = Gauge(
            "system_disk_io_bytes", "Disk I/O", ["job_id", "dataset", "stage"]
        )
        self.system_filesystem_usage_bytes = Gauge(
            "system_filesystem_usage_bytes",
            "Filesystem Usage",
            ["job_id", "dataset", "stage"],
        )
        self.system_memory_usage_bytes = Gauge(
            "system_memory_usage_bytes", "Memory Usage", ["job_id", "dataset", "stage"]
        )
        self.system_cpu_usage_seconds = Gauge(
            "system_cpu_usage_seconds", "CPU Usage", ["job_id", "dataset", "stage"]
        )

        self.start_server(port=port)

    def start_server(self, port=8000):
        start_http_server(port)
