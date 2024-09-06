#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Acquire                                                                    #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appvocai/application/metrics/monitor.py                                            #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Friday September 6th 2024 03:51:20 pm                                               #
# Modified   : Friday September 6th 2024 04:13:14 pm                                               #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
import statistics
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from functools import wraps
from typing import Callable, Optional

# ------------------------------------------------------------------------------------------------ #


# Decorator class
class MonitorDecorator:
    def __init__(self, repo):
        self.repo = repo
        self.metrics = None
        self.task_id = None
        self.latencies = []
        self.instance_count = 0
        self.start_time = None
        self.end_time = None

    def compute_metrics(self):
        # Calculate the latency and throughput statistics
        if not self.latencies:
            raise ValueError("No latencies collected to compute statistics.")

        self.end_time = datetime.now()
        total_duration = (self.end_time - self.start_time).total_seconds()
        latency_min = min(self.latencies)
        latency_max = max(self.latencies)
        latency_average = sum(self.latencies) / len(self.latencies)
        latency_median = statistics.median(self.latencies)
        latency_std = statistics.stdev(self.latencies) if len(self.latencies) > 1 else 0

        # Throughput based on instance count / latency
        throughputs = [1 / latency for latency in self.latencies]
        throughput_min = min(throughputs)
        throughput_max = max(throughputs)
        throughput_average = sum(throughputs) / len(throughputs)
        throughput_median = statistics.median(throughputs)
        throughput_std = statistics.stdev(throughputs) if len(throughputs) > 1 else 0

        # Speedup as total latency divided by total duration
        total_latency = sum(self.latencies)
        speedup = total_latency / total_duration if total_duration else 0

        # Instantiate the Metrics object
        self.metrics.duration = total_duration
        self.metrics.latency_min = latency_min
        self.metrics.latency_max = latency_max
        self.metrics.latency_average = latency_average
        self.metrics.latency_median = latency_median
        self.metrics.latency_std = latency_std
        self.metrics.throughput_min = throughput_min
        self.metrics.throughput_max = throughput_max
        self.metrics.throughput_average = throughput_average
        self.metrics.throughput_median = throughput_median
        self.metrics.throughput_std = throughput_std
        self.metrics.speedup = speedup
        self.metrics.instances = self.instance_count

        # Persist the metrics in the repository
        self.repo.add(self.metrics)

    def operation(self, func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Start of the outer operation
            if self.start_time is None:
                self.start_time = datetime.now()

            artifact = args[0]  # Assuming the first argument is the artifact
            passport = artifact.passport

            if self.task_id and self.task_id != passport.task_id:
                raise ValueError("Task ID has changed unexpectedly.")

            self.task_id = passport.task_id
            operation_type = self.operation_type

            self.metrics = Metrics(
                project_id=passport.project_id,
                job_id=passport.job_id,
                task_id=self.task_id,
                data_type=passport.data_type,
                operation_type=operation_type,
                dt_started=self.start_time,
            )

            result = await func(*args, **kwargs)  # Perform the outer operation

            # Compute and persist metrics after the operation ends
            self.compute_metrics()
            return result

        return wrapper

    def event(self, func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Inner operation for each event instance
            start = time.time()
            result = await func(*args, **kwargs)  # Perform the inner instance operation
            latency = time.time() - start

            # Collect latencies
            self.latencies.append(latency)
            self.instance_count += 1

            return result

        return wrapper
