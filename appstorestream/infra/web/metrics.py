#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppStoreStream: Apple App Data and Reviews, Delivered!                              #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appstorestream/infra/web/metrics.py                                                #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appstore-stream.git                             #
# ------------------------------------------------------------------------------------------------ #
# Created    : Wednesday August 21st 2024 06:48:22 am                                              #
# Modified   : Wednesday August 21st 2024 08:40:53 am                                              #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
import time
from collections import deque
from dataclasses import dataclass, field

from appstorestream.core.data import DataClass


# ------------------------------------------------------------------------------------------------ #
@dataclass
class SessionStatistics:
    average: float = 0
    cv: float = 0


# ------------------------------------------------------------------------------------------------ #
@dataclass
class SessionMetricsCollector(DataClass):
    """A class to collect and manage metrics for a session.

    This class records the timestamps for requests and responses, calculates durations,
    and maintains a history of latencies and requests to compute throughput.

    Attributes:
        send_timestamp (float): The timestamp when a request is sent.
        recv_timestamp (float): The timestamp when a response is received.
        duration (float): The duration of the request-response cycle.
        requests (int): The total number of requests sent during the session.
        throughput (float): The calculated throughput of requests per second.
        latencies (deque): A deque to store latencies associated with each request.
    """

    send_timestamp: float = 0
    recv_timestamp: float = 0
    duration: float = 0
    requests: int = 0
    throughput: float = 0
    latencies: deque = field(default_factory=deque)

    def send(self) -> None:
        """Record the current time as the send timestamp."""
        self.send_timestamp = time.time()

    def recv(self) -> None:
        """Record the current time as the receive timestamp and calculate duration.

        The duration is calculated as the difference between the receive and send timestamps.
        """
        self.recv_timestamp = time.time()
        self.duration = self.recv_timestamp - self.send_timestamp

    def add_latency(self, latency: float) -> None:
        """Add a latency value to the latencies deque.

        Args:
            latency (float): The latency of the current request.
        """
        self.latencies.append((self.send_timestamp, latency))
        self.requests += 1

    def get_latencies(self) -> deque:
        """Return the deque of latencies recorded.

        Returns:
            deque: A deque containing tuples of send timestamps and their associated latencies.
        """
        return self.latencies

    def get_throughput(self) -> deque:
        """Calculate and return the throughput of requests.

        The throughput is calculated as the number of requests divided by the duration
        of the request-response cycle. Returns a deque containing the send timestamp
        and the computed throughput.

        Returns:
            deque: A deque containing the send timestamp and the calculated throughput.
                   If the duration is zero, returns an empty deque.
        """
        throughput = self.requests / self.duration if self.duration else 0
        return deque((self.send_timestamp, throughput)) if throughput else deque()


# ------------------------------------------------------------------------------------------------ #
class SessionMetrics:
    """A class to manage and store metrics for a session, including latencies and throughputs."""

    def __init__(self, max_history: int = 300) -> None:
        """Initialize a SessionMetrics instance.

        Args:
            max_history (int, optional): The maximum time window for retaining metrics history.
                                          Defaults to 300 seconds.
        """
        self._max_history = max_history
        self._latencies = deque()
        self._throughputs = deque()

    def update_metrics(self, collector: SessionMetricsCollector) -> None:
        """Update the metrics with data from the collector.

        Args:
            collector (SessionMetricsCollector): The collector containing the latest session metrics.
        """
        self._latencies.extend(collector.get_latencies())
        self._throughputs.extend(collector.get_throughput())
        self._prune()

    def compute_latency_stats(self, time_window: int = None) -> SessionStatistics:
        """Compute statistics for latencies within the specified time window.

        Args:
            time_window (int, optional): The time window in seconds to compute statistics for.

        Returns:
            SessionStatistics: The computed statistics for latencies.
        """
        latencies = (
            list(self._latencies)[-time_window:]
            if time_window and len(self._latencies) >= time_window
            else list(self._latencies)
        )

        if latencies:
            stats = SessionStatistics()
            stats.average = sum(latencies) / len(latencies)
            stats.cv = (
                (sum((x - stats.average) ** 2 for x in latencies) / len(latencies))
                ** 0.5
            ) / stats.average
            return stats
        return SessionStatistics()  # Return empty stats if no latencies

    def compute_throughput_stats(self, time_window: int = None) -> SessionStatistics:
        """Compute statistics for throughputs within the specified time window.

        Args:
            time_window (int, optional): The time window in seconds to compute statistics for.

        Returns:
            SessionStatistics: The computed statistics for throughputs.
        """
        throughputs = (
            list(self._throughputs)[-time_window:]
            if time_window and len(self._throughputs) >= time_window
            else list(self._throughputs)
        )

        if throughputs:
            stats = SessionStatistics()
            stats.average = sum(throughputs) / len(throughputs)
            stats.cv = (
                (sum((x - stats.average) ** 2 for x in throughputs) / len(throughputs))
                ** 0.5
            ) / stats.average
            return stats
        return SessionStatistics()  # Return empty stats if no throughputs

    def _prune(self, time_window: int = None) -> None:
        """Prune metrics that fall outside the specified time window.

        Args:
            time_window (int, optional): The time window in seconds to retain metrics.
                                          If not provided, defaults to max_history.

        This method removes metrics from the deques (latencies, requests)
        that are older than the specified time window.
        """
        current_time = time.time()
        time_window = time_window or self._max_history

        # Prune latencies
        while self._latencies and (current_time - self._latencies[0][0]) > time_window:
            self._latencies.popleft()

        # Prune throughputs
        while (
            self._throughputs and (current_time - self._throughputs[0][0]) > time_window
        ):
            self._throughputs.popleft()
