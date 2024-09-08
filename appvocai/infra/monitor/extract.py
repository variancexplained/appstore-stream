#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Acquire                                                                    #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appvocai/application/monitor/extract.py                                            #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Friday September 6th 2024 03:51:20 pm                                               #
# Modified   : Saturday September 7th 2024 12:39:27 am                                             #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Extract Monitor Modulce"""
import statistics
import time
from datetime import datetime
from functools import wraps
from typing import Any, Awaitable, Callable, Dict, List, Optional, TypeVar

from pympler import asizeof  # type: ignore

from appvocai.domain.monitor.extract import ExtractMetrics
from appvocai.infra.repo.monitor.extract import ExtractMetricsRepo

# ------------------------------------------------------------------------------------------------ #
R = TypeVar("R")  # Return type of the operation
E = TypeVar("E")  # Return type of the event

# For a general callable, you might not know the argument types upfront, so you can use Any or specific types
# Example for the operation and event callable signatures
OperationCallable = Callable[..., Awaitable[R]]  # Callable for operation
EventCallable = Callable[..., Awaitable[E]]  # Callable for event


# ------------------------------------------------------------------------------------------------ #
# Decorator class
class ExtractMonitorDecorator:

    def __init__(self, repo: ExtractMetricsRepo):
        self.repo = repo
        self.metrics: Optional[ExtractMetrics] = None
        self.task_id: Optional[int] = None
        self.latencies: List[float] = []
        self.instance_count = 0
        self.sizes: List[float] = []
        self.dt_started: Optional[datetime] = None
        self.dt_ended: Optional[datetime] = None

    def compute_metrics(self) -> None:
        # Calculate the latency and throughput statistics
        if not self.latencies:
            raise ValueError("No latencies collected to compute statistics.")

        self.dt_ended = datetime.now()

        total_duration = (
            (self.dt_ended - self.dt_started).total_seconds()
            if self.dt_started and self.dt_ended
            else 0
        )

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
        if self.metrics is not None:
            self.metrics.dt_ended = self.dt_ended
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
            self.metrics.requests = self.instance_count

        # Persist the metrics in the repository
        if self.metrics:
            self.repo.add(metrics=self.metrics)
        else:
            raise RuntimeError("Metrics could not be computed for this operator.")

    def operation(self, func: OperationCallable[R]) -> OperationCallable[R]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Dict[str, Any]) -> R:
            # Start of the outer operation
            if self.dt_started is None:
                self.dt_started = datetime.now()

            artifact = args[0]  # Assuming the first argument is the artifact
            passport = artifact.passport

            if self.task_id and self.task_id != passport.task_id:
                raise ValueError("Task ID has changed unexpectedly.")

            self.metrics = ExtractMetrics(
                project_id=passport.project_id,
                job_id=passport.job_id,
                task_id=passport.task_id,
                data_type=passport.data_type,
                operation_type=passport.operation_type,
                dt_started=self.dt_started,
            )

            result = await func(*args, **kwargs)  # Perform the outer operation

            # Compute and persist metrics after the operation ends
            self.compute_metrics()
            return result

        return wrapper

    def event(self, func: EventCallable[E]) -> EventCallable[E]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Dict[str, Any]) -> E:
            # Inner operation for each event instance
            start = time.time()
            result = await func(*args, **kwargs)  # Perform the inner instance operation
            latency = time.time() - start

            # Collect latencies
            self.latencies.append(latency)
            self.sizes.append(asizeof.asizeof(result))  # Assuming result has a size

            self.instance_count += 1

            return result

        return wrapper
