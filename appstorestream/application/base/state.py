#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppStoreStream: Apple App Data and Reviews, Delivered!                              #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appstorestream/application/base/state.py                                           #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appstore-stream.git                             #
# ------------------------------------------------------------------------------------------------ #
# Created    : Sunday July 28th 2024 03:55:39 pm                                                   #
# Modified   : Sunday July 28th 2024 08:10:21 pm                                                   #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""State Module"""
import logging
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Deque

import aiohttp

from appstorestream.application.base.job import Job
from appstorestream.application.base.response import AsyncResponse
from appstorestream.core.enum import CircuitBreakerStates


# ------------------------------------------------------------------------------------------------ #
@dataclass
class StateManager:
    """Manages the state of responses to determine failure rates within a specified window.

    Attributes:
        window_size (int): The time window in seconds to track responses.
        failure_rate_threshold (float): The threshold for the failure rate to trigger state changes.
        responses (Deque[Any]): A deque to store response tuples with timestamp, request count, and error count.
    """
    window_size: int
    failure_rate_threshold: float
    responses: Deque[Any] = field(default_factory=deque)

    def reset(self) -> None:
        """Resets the state manager by clearing the stored responses."""
        self.responses.clear()

    def failure_rate_exceeded(self, response: AsyncResponse) -> bool:
        """Checks if the failure rate exceeds the threshold based on the stored responses.

        Args:
            response (AsyncResponse): The response object containing the request count and total errors.

        Returns:
            bool: True if the failure rate exceeds the threshold, otherwise False.
        """
        self._add_response(response=response)
        errors = sum(errors for _, _, errors in self.responses)
        requests = sum(requests for _, requests, _ in self.responses)
        error_rate = errors / requests if requests > 0 else 0
        return error_rate > self.failure_rate_threshold

    def _add_response(self, response: AsyncResponse) -> None:
        """Adds a response to the deque and cleans up old responses outside the window size.

        Args:
            response (AsyncResponse): The response object to be added.
        """
        current_time = datetime.now()
        self.responses.append((current_time, response.request_count, response.total_errors))
        self._clean_responses()

    def _clean_responses(self) -> None:
        """Removes responses that are outside the specified time window."""
        while self.responses and (datetime.now() - self.responses[0][0]).total_seconds() > self.window_size:
            self.responses.popleft()


# ------------------------------------------------------------------------------------------------ #

class CircuitBreaker:
    """A circuit breaker to manage job states based on response failure rates.

    Attributes:
        closed_window_size (int): Window size in seconds for the closed state. Default is 300 seconds.
        closed_burnin_period (int): Burn-in period in seconds for the closed state. Default is 300 seconds.
        closed_failure_rate_threshold (float): Failure rate threshold for the closed state. Default is 0.5.
        half_open_window_size (int): Window size in seconds for the half-open state. Default is 600 seconds.
        half_open_failure_rate_threshold (float): Failure rate threshold for the half-open state. Default is 0.3.
        half_open_delay (int): Delay in seconds between requests in the half-open state. Default is 2 seconds.
        short_circuit_errors_window_size (int): Window size in seconds for short-circuit errors. Default is 180 seconds.
        short_circuit_errors_failure_rate_threshold (float): Failure rate threshold for short-circuit errors. Default is 0.9.
        short_circuit_404s_window_size (int): Window size in seconds for short-circuit 404s. Default is 180 seconds.
        short_circuit_404s_failure_rate_threshold (float): Failure rate threshold for short-circuit 404s. Default is 0.7.
        open_cooldown_period (int): Cooldown period in seconds for the open state. Default is 300 seconds.

    Example:
        ```python
        from appstorestream.application.base.job import Job
        from appstorestream.application.base.response import AsyncResponse
        from appstorestream.core.enum import CircuitBreakerStates

        circuit_breaker = CircuitBreaker()
        job = Job()

        circuit_breaker.start(job=job)

        response = AsyncResponse(request_count=10, total_errors=3)

        while job.status not in [Job.Status.TERMINATED, Job.Status.COMPLETE]:
            circuit_breaker.evaluate_response(response=response)
        ```
    """

    def __init__(self,
                 closed_window_size: int = 300,
                 closed_burnin_period: int = 300,
                 closed_failure_rate_threshold: float = 0.5,
                 half_open_window_size: int = 600,
                 half_open_failure_rate_threshold: float = 0.3,
                 half_open_delay: int = 2,
                 short_circuit_errors_window_size: int = 180,
                 short_circuit_errors_failure_rate_threshold: float = 0.9,
                 short_circuit_404s_window_size: int = 180,
                 short_circuit_404s_failure_rate_threshold: float = 0.7,
                 open_cooldown_period: int = 300) -> None:
        self._closed_window_size = closed_window_size
        self._closed_burnin_period = closed_burnin_period
        self._closed_failure_rate_threshold = closed_failure_rate_threshold
        self._half_open_window_size = half_open_window_size
        self._half_open_failure_rate_threshold = half_open_failure_rate_threshold
        self._half_open_delay = half_open_delay
        self._short_circuit_errors_window_size = short_circuit_errors_window_size
        self._short_circuit_errors_failure_rate_threshold = short_circuit_errors_failure_rate_threshold
        self._short_circuit_404s_window_size = short_circuit_404s_window_size
        self._short_circuit_404s_failure_rate_threshold = short_circuit_404s_failure_rate_threshold
        self._open_cooldown_period = open_cooldown_period

        self._starttime = None
        self._job = None

        self._closed_state_manager = StateManager(window_size=self._closed_window_size, failure_rate_threshold=self._closed_failure_rate_threshold)
        self._half_open_state_manager = StateManager(window_size=self._half_open_window_size, failure_rate_threshold=self._half_open_failure_rate_threshold)
        self._short_circuit_error_state_manager = StateManager(window_size=self._short_circuit_errors_window_size, failure_rate_threshold=self._short_circuit_errors_failure_rate_threshold)
        self._short_circuit_404_state_manager = StateManager(window_size=self._short_circuit_404s_window_size, failure_rate_threshold=self._short_circuit_404s_failure_rate_threshold)

        self._state = CircuitBreakerStates.CLOSED

        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def start(self, job: Job) -> None:
        """Starts the circuit breaker with the given job.

        Args:
            job (Job): The job object to be managed by the circuit breaker.
        """
        self._starttime = datetime.now()
        self._job = job

    def evaluate_response(self, response: AsyncResponse) -> None:
        """Evaluates the response and manages the state transitions of the circuit breaker.

        Args:
            response (AsyncResponse): The response object containing the request count and total errors.
        """
        # If burnin, don't start monitoring
        if self._burnin():
            return

        # Check errors for termination condition
        if self._short_circuit_error_state_manager.failure_rate_exceeded(response=response):
            self._terminate_circuit()
            return

        # Check 404s for end of pagination and completion condition
        if self._short_circuit_404_state_manager.failure_rate_exceeded(response=response):
            self._complete_circuit()
            return

        # If in closed state, check for open condition
        if self._state == CircuitBreakerStates.CLOSED:
            if self._closed_state_manager.failure_rate_exceeded(response=response):
                self._open_circuit()

        # If in half-open state, check for open condition. Delay if failure rate not exceeded
        elif self._state == CircuitBreakerStates.HALF_OPEN:
            if self._half_open_state_manager.failure_rate_exceeded(response=response):
                self._open_circuit()
            else:
                time.sleep(self._half_open_delay)

    def _burnin(self) -> bool:
        """Checks if the burn-in period has elapsed.

        Returns:
            bool: True if the burn-in period is still active, otherwise False.
        """
        return (datetime.now() - self._starttime).total_seconds() < self._closed_burnin_period

    def _open_circuit(self) -> None:
        """Transitions the circuit breaker to the open state and starts the cooldown period."""
        self._state = CircuitBreakerStates.OPEN
        self._reset_state_managers()
        self._logger.info("Circuit breaker opened. Waiting for cooldown period.")
        time.sleep(self._open_cooldown_period)
        self._half_open_circuit()

    def _half_open_circuit(self) -> None:
        """Transitions the circuit breaker to the half-open state and introduces delays between requests."""
        self._state = CircuitBreakerStates.HALF_OPEN
        self._logger.info("Circuit breaker half-opened. Introducing delays between requests.")

    def _terminate_circuit(self) -> None:
        """Terminates the circuit and stops further requests."""
        self._state = CircuitBreakerStates.TERMINATED
        self._job.terminate()
        self._logger.info("Circuit breaker terminated. No further requests will be made.")

    def _complete_circuit(self) -> None:
        """Marks the job as complete and stops further data processing."""
        self._state = CircuitBreakerStates.COMPLETE
        self._job.complete()
        self._logger.info("Circuit breaker marked job as complete. No further requests will be made.")

    def _reset_state_managers(self) -> None:
        """Resets all state managers to clear any accumulated responses."""
        self._closed_state_manager.reset()
        self._half_open_state_manager.reset()
        self._short_circuit_error_state_manager.reset()
        self._short_circuit_404_state_manager.reset()
