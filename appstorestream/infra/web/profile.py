#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppStoreStream: Apple App Data and Reviews, Delivered!                              #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appstorestream/infra/web/profile.py                                                #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appstore-stream.git                             #
# ------------------------------------------------------------------------------------------------ #
# Created    : Wednesday August 21st 2024 06:48:22 am                                              #
# Modified   : Thursday August 22nd 2024 11:52:06 pm                                               #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
from __future__ import annotations

import logging
import statistics
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Deque, Optional, Tuple
from uuid import uuid4

from appstorestream.core.data import DataClass


# ------------------------------------------------------------------------------------------------ #
#                                   SESSION PROFILE                                                #
# ------------------------------------------------------------------------------------------------ #
@dataclass
class SessionProfile(DataClass):
    """A class encapsulating session performance metrics.

    This class records the timestamps for requests and responses, calculates durations,
    and maintains a history of latencies and requests to compute throughput.

    Attributes:
        session_id (str): A string formatted uuid4 id.
        send_timestamp (float): The timestamp when a request is sent.
        recv_timestamp (float): The timestamp when a response is received.
        duration (float): The duration of the request-response cycle.
        requests (int): The total number of requests sent during the session.
        throughput (float): The calculated throughput of requests per second.
        latencies (deque): A deque to store latencies associated with each request.
    """

    session_id: str = ""
    send_timestamp: float = 0
    recv_timestamp: float = 0
    duration: float = 0
    requests: int = 0
    throughput: float = 0
    latencies: Deque[Tuple[str, float, float]] = field(default_factory=deque)

    def __post_init__(self) -> None:
        self.session_id = str(uuid4)

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
        self.latencies.append((self.session_id, self.send_timestamp, latency))
        self.requests += 1

    def get_latencies(self) -> Deque[Tuple[str, float, float]]:
        """Return the deque of latencies recorded.

        Returns:
            deque: A deque containing Tuples of send timestamps and their associated latencies.
        """
        return self.latencies

    def get_throughput(self) -> Tuple[str, float, float]:
        """Calculate and return the throughput of requests.

        The throughput is calculated as the number of requests divided by the duration
        of the request-response cycle. Returns a deque containing the send timestamp
        and the computed throughput.

        Returns:
            Tuple: A Tuple containing the send timestamp and the calculated throughput.
                   If the duration is zero, returns an empty Tuple.
        """
        self.throughput = self.requests / self.duration if self.duration else 0
        return (self.session_id, self.send_timestamp, self.throughput)


# ------------------------------------------------------------------------------------------------ #
#                                 SESSION STATISTICS                                               #
# ------------------------------------------------------------------------------------------------ #
@dataclass
class SessionStats:
    """Class to encapsulate statistical metrics for a session.

    This class holds statistical values such as minimum, maximum, median,
    average, standard deviation, and coefficient of variation, which are
    commonly used for analyzing performance metrics in sessions.

    Attributes:
        requests (int): Number of requests represented by these stats.
        min (float): The minimum value recorded in the session.
        max (float): The maximum value recorded in the session.
        median (float): The median value of the recorded data.
        average (float): The average value of the recorded data.
        std (float): The standard deviation of the recorded data.
        cv (float): The coefficient of variation, calculated as the ratio of
            the standard deviation to the average.
    """

    min: float = 0
    max: float = 0
    median: float = 0
    average: float = 0
    std: float = 0
    cv: float = 0


# ------------------------------------------------------------------------------------------------ #
#                                   SESSION CONTROL                                                #
# ------------------------------------------------------------------------------------------------ #
@dataclass
class SessionControl:
    """Represents the parameters that control for request sessions.

    This class holds the parameters related to the adaptation of the
    request handling process, including the rate of requests, concurrency,
    and the calculated delay between asynchronous requests.

    Attributes:
        rate (float): The rate of requests per second.
        concurrency (float): The number of concurrent asynchronous requests.
        delay (float): The delay in seconds between async requests.
    """

    rate: float = 0.0  # Requests per second
    concurrency: float = 0.0  # Number of async requests
    delay: float = 0.0  # Delay in seconds between async requests

    def __post_init__(self) -> None:
        """Post-initialization processing to calculate the delay."""
        if self.rate > 0 and self.concurrency > 0:
            self.delay = 1 / self.rate * self.concurrency
        else:
            self.delay = 0  # Set to 0 if rate or concurrency is non-positive


# ------------------------------------------------------------------------------------------------ #
#                                    SESSION HISTORY                                               #
# ------------------------------------------------------------------------------------------------ #
class SessionHistory:
    """A class to manage and store metrics for sessions, including latencies and throughputs."""

    def __init__(self, max_history: int = 3600) -> None:
        """Initialize a SessionHistory instance.

        Args:
            max_history (int, optional): The maximum time window for retaining metrics history.
                                          Defaults to 3600 seconds.
        """
        # Maximum time to retain metrics history
        self._max_history = max_history
        # Store latencies per request
        self._latencies: Deque[Tuple[str, float, float]] = deque()
        # Store throughputs per session
        self._throughputs: Deque[Tuple[str, float, float]] = deque()
        # Store request rate per session from adapter
        self._rates: Deque[Tuple[str, float, float]] = deque()
        # Store delay per session from adapter
        self._delays: Deque[Tuple[str, float, float]] = deque()
        # Store concurrency per session from adapter
        self._concurrencies: Deque[Tuple[str, float, float]] = deque()
        # Store the current session ID
        self._current_session_id: str = ""
        # Logging object for the class.
        self._logger = logging.getLogger(f"{self.__class__.__name__}")

    @property
    def requests(self) -> int:
        """Returns the number of requests in history."""
        return len(self._latencies)

    @property
    def sessions(self) -> int:
        """Returns the number of async request sessions."""
        return len(self._throughputs)

    def add_metrics(self, profile: SessionProfile) -> None:
        """Update the metrics with data from the collector.

        Args:
            profile (SessionProfile): The session profile containing the latest session metrics.
        """
        # Update current session ID
        self._current_session_id = profile.session_id
        # Add latencies from the profile
        self._latencies.extend(profile.get_latencies())
        # Add throughput from the profile
        self._throughputs.append(profile.get_throughput())
        # Remove outdated metrics
        self._prune()

    def add_session_control(self, session_control: SessionControl) -> None:
        """Add session control metrics to the history.

        Args:
            session_control (SessionControl): The session control instance containing rate, concurrency, and delay.
        """
        # Add current rate to history
        self._rates.append(
            (self._current_session_id, time.time(), session_control.rate)
        )
        # Add current delay to history
        self._delays.append(
            (self._current_session_id, time.time(), session_control.delay)
        )
        # Add current concurrency to history
        self._concurrencies.append(
            (self._current_session_id, time.time(), session_control.concurrency)
        )

    def get_requests(self, time_window: Optional[int] = None) -> int:
        """Returns total number of requests or the request count within a time window.

        Args:
            time_window (int, optional): The time window in seconds to compute stats for.

        Returns: int
        """

        # A latency measure represents one request, we'll use that as a proxy for requests count.
        latencies = (
            [latency for _, _, latency in self._latencies][
                -time_window:
            ]  # Get latencies in the specified time window
            if time_window and time_window <= len(self._latencies)
            else [
                latency for _, _, latency in self._latencies
            ]  # Otherwise, get all latencies
        )
        return len(latencies)

    def get_sessions(self, time_window: Optional[int] = None) -> int:
        """Returns total number of sessions or the session count within a time window.
        Args:
            time_window (int, optional): The time window in seconds to compute stats for.

        Returns: int
        """

        # A throughput measure represents one session, we'll use that as a proxy for session count.
        throughputs = (
            [throughput for _, _, throughput in self._throughputs][
                -time_window:
            ]  # Get latencies in the specified time window
            if time_window and time_window <= len(self._throughputs)
            else [
                throughput for _, _, throughput in self._throughputs
            ]  # Otherwise, get all latencies
        )
        return len(throughputs)

    def get_latency_stats(self, time_window: Optional[int] = None) -> SessionStats:
        """Create a statistical snapshot of performance within the specified time window.

        Args:
            time_window (int, optional): The time window in seconds to compute stats for.

        Returns:
            StatisticalSnapshot: The computed stats for latencies and throughputs
                and session control parameters.
        """
        # Create a SessionStats object for latencies
        stats = SessionStats()

        # Obtain all latencies or those for the time window
        latencies = (
            [latency for _, _, latency in self._latencies][
                -time_window:
            ]  # Get latencies in the specified time window
            if time_window and time_window <= len(self._latencies)
            else [
                latency for _, _, latency in self._latencies
            ]  # Otherwise, get all latencies
        )

        if latencies:
            # Compute statistical metrics for latencies
            stats.min = min(latencies)
            stats.max = max(latencies)
            stats.median = statistics.median(latencies)
            stats.average = sum(latencies) / len(latencies)
            stats.std = statistics.stdev(latencies)
            try:
                stats.cv = (
                    (sum((x - stats.average) ** 2 for x in latencies) / len(latencies))
                    ** 0.5
                ) / stats.average
            except ZeroDivisionError as e:
                msg = f"Coefficient of variation for latency is underfined for zero mean. Returning zero."
                self._logger.warning(msg)
                stats.cv = 0
        return stats

    def get_throughput_stats(self, time_window: Optional[int] = None) -> SessionStats:
        # Create a SessionStats object for throughput
        stats = SessionStats()
        # Compute Throughput Stats
        throughputs = (
            [throughput for _, _, throughput in self._throughputs][
                -time_window:
            ]  # Get throughputs in the specified time window
            if time_window and time_window <= len(self._throughputs)
            else [
                throughput for _, _, throughput in self._throughputs
            ]  # Otherwise, get all throughputs
        )

        if throughputs:
            # Compute statistical metrics for throughputs
            stats.min = min(throughputs)
            stats.max = max(throughputs)
            stats.median = statistics.median(throughputs)
            stats.std = statistics.stdev(throughputs)
            stats.average = sum(throughputs) / len(throughputs)
            try:
                stats.cv = (
                    (
                        sum((x - stats.average) ** 2 for x in throughputs)
                        / len(throughputs)
                    )
                    ** 0.5
                ) / stats.average
            except ZeroDivisionError as e:
                msg = f"Coefficient of variation for throughput is underfined for zero mean. Returning zero."
                self._logger.warning(msg)
                stats.cv = 0
        return stats

    def get_rate_stats(self, time_window: Optional[int] = None) -> SessionStats:
        # Create a SessionStats object for rates
        stats = SessionStats()
        # Compute Throughput Stats
        rates = (
            [rate for _, _, rate in self._rates][
                -time_window:
            ]  # Get rates in the specified time window
            if time_window and time_window <= len(self._rates)
            else [rate for _, _, rate in self._rates]  # Otherwise, get all rates
        )

        if rates:
            # Compute statistical metrics for rates
            stats.min = min(rates)
            stats.max = max(rates)
            stats.median = statistics.median(rates)
            stats.std = statistics.stdev(rates)
            stats.average = sum(rates) / len(rates)
            try:
                stats.cv = (
                    (sum((x - stats.average) ** 2 for x in rates) / len(rates)) ** 0.5
                ) / stats.average
            except ZeroDivisionError as e:
                msg = f"Coefficient of variation for request rate is underfined for zero mean. Returning zero."
                self._logger.warning(msg)
                stats.cv = 0

        return stats

    def get_delay_stats(self, time_window: Optional[int] = None) -> SessionStats:
        # Create a SessionStats object for delays
        stats = SessionStats()
        # Compute Throughput Stats
        delays = (
            [delay for _, _, delay in self._delays][
                -time_window:
            ]  # Get delays in the specified time window
            if time_window and time_window <= len(self._delays)
            else [delay for _, _, delay in self._delays]  # Otherwise, get all delays
        )

        if delays:
            # Compute statistical metrics for delays
            stats.min = min(delays)
            stats.max = max(delays)
            stats.median = statistics.median(delays)
            stats.std = statistics.stdev(delays)
            stats.average = sum(delays) / len(delays)
            try:
                stats.cv = (
                    (sum((x - stats.average) ** 2 for x in delays) / len(delays)) ** 0.5
                ) / stats.average
            except ZeroDivisionError as e:
                msg = f"Coefficient of variation for delay is underfined for zero mean. Returning zero."
                self._logger.warning(msg)
                stats.cv = 0
        return stats

    def get_concurrency_stats(self, time_window: Optional[int] = None) -> SessionStats:
        # Create a SessionStats object for concurrencies
        stats = SessionStats()
        # Compute Throughput Stats
        concurrencies = (
            [concurrency for _, _, concurrency in self._concurrencies][
                -time_window:
            ]  # Get concurrencies in the specified time window
            if time_window and time_window <= len(self._concurrencies)
            else [
                concurrency for _, _, concurrency in self._concurrencies
            ]  # Otherwise, get all concurrencies
        )

        if concurrencies:
            # Compute statistical metrics for concurrencies
            stats.min = min(concurrencies)
            stats.max = max(concurrencies)
            stats.median = statistics.median(concurrencies)
            stats.std = statistics.stdev(concurrencies)
            stats.average = sum(concurrencies) / len(concurrencies)
            try:
                stats.cv = (
                    (
                        sum((x - stats.average) ** 2 for x in concurrencies)
                        / len(concurrencies)
                    )
                    ** 0.5
                ) / stats.average
            except ZeroDivisionError as e:
                msg = f"Coefficient of variation for latency is underfined for zero mean. Returning zero."
                self._logger.warning(msg)
                stats.cv = 0

        return stats

    def get_snapshot(self, time_window: Optional[int] = None) -> StatisticalSnapshot:
        requests = self.get_requests(time_window=time_window)
        sessions = self.get_sessions(time_window=time_window)
        latencies = self.get_latency_stats(time_window=time_window)
        throughputs = self.get_throughput_stats(time_window=time_window)
        rates = self.get_rate_stats(time_window=time_window)
        delays = self.get_delay_stats(time_window=time_window)
        concurrency = self.get_concurrency_stats(time_window=time_window)
        snapshot = StatisticalSnapshot(
            requests=requests,
            sessions=sessions,
            latency_stats=latencies,
            throughput_stats=throughputs,
            rate_stats=rates,
            delay_stats=delays,
            concurrency_stats=concurrency,
        )
        return snapshot

    def _prune(self, time_window: Optional[int] = None) -> None:
        """Prune metrics that fall outside the specified time window.

        Args:
            time_window (int, optional): The time window in seconds to retain metrics.
                                          If not provided, defaults to max_history.

        This method removes metrics from the deques (latencies, requests)
        that are older than the specified time window.
        """
        current_time = time.time()  # Get the current time
        time_window = (
            time_window or self._max_history
        )  # Use provided time window or default

        # Prune latencies
        while self._latencies and (current_time - self._latencies[0][1]) > time_window:
            self._latencies.popleft()  # Remove oldest latency entry

        # Prune throughputs
        while (
            self._throughputs and (current_time - self._throughputs[0][1]) > time_window
        ):
            self._throughputs.popleft()  # Remove oldest throughput entry


# ------------------------------------------------------------------------------------------------ #
#                                STATISTICAL SNAPSHOT                                              #
# ------------------------------------------------------------------------------------------------ #
@dataclass
class StatisticalSnapshot(DataClass):
    requests: int = 0
    sessions: int = 0
    latency_stats: SessionStats = SessionStats()
    throughput_stats: SessionStats = SessionStats()
    rate_stats: SessionStats = SessionStats()
    delay_stats: SessionStats = SessionStats()
    concurrency_stats: SessionStats = SessionStats()
