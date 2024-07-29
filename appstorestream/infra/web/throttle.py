#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppStoreStream: Apple App Data and Reviews, Delivered!                              #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appstorestream/infra/web/throttle.py                                               #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appstore-stream.git                             #
# ------------------------------------------------------------------------------------------------ #
# Created    : Friday July 19th 2024 04:44:47 am                                                   #
# Modified   : Monday July 29th 2024 02:43:43 pm                                                   #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Autothrottle Module"""
import asyncio
import random
import time
from collections import deque

from appstorestream.infra.base.service import InfraService

# ------------------------------------------------------------------------------------------------ #


class AThrottle(InfraService):
    """
    Throttling mechanism to control request rate based on latency.

    Attributes:
        min_rate (float): Minimum requests per second.
        base_rate (float): Base requests per second.
        max_rate (float): Maximum requests per second.
        temperature (float): Temperature parameter for randomization (0 to 1).
        current_rate (float): Current requests per second.
        latencies (deque): Deque to store latency values for the sliding window.
        send_time (float): Timestamp when the request was sent.
        burn_in (int): Number of requests during burn-in period where rate adjustments are not made.
        request_count (int): Counter for the number of requests sent.

    Arguments:
        min_rate (float): Minimum requests per second.
        base_rate (float): Base requests per second.
        max_rate (float): Maximum requests per second.
        temperature (float): Temperature parameter for randomization (0 to 1). Default is 0.5.
        window_size (int): The size of the sliding window for latency measurements. Default is 10.
        burn_in (int): Number of initial requests during which rate adjustments are not made. Default is 10.

    Usage:
        throttle = AThrottle(min_rate=5, base_rate=20, max_rate=100, temperature=0.5, window_size=10, burn_in=10)

        # In an async function
        await throttle.send()
        # send request
        await throttle.recv()
        await throttle.delay()
    """

    def __init__(
        self,
        min_rate: float,
        base_rate: float,
        max_rate: float,
        temperature: float = 0.5,
        window_size: int = 10,
        burn_in: int = 10,
    ) -> None:
        self.min_rate = min_rate
        self.base_rate = base_rate
        self.max_rate = max_rate
        self.temperature = temperature
        self.current_rate = base_rate
        self.latencies = deque(maxlen=window_size)
        self.send_time = None
        self.burn_in = burn_in
        self.request_count = 0

    async def send(self) -> None:
        """Marks the time before sending a request."""
        self.send_time = time.monotonic()

    async def recv(self) -> None:
        """Marks the time after receiving a response and calculates latency."""
        recv_time = time.monotonic()
        latency = recv_time - self.send_time
        self.latencies.append(latency)
        self.request_count += 1
        if self.request_count > self.burn_in:
            self.update_rate()

    async def delay(self) -> None:
        """Executes a delay based on the current request rate."""
        delay_time = self.calculate_delay()
        await asyncio.sleep(delay_time)

    def calculate_delay(self) -> float:
        """
        Calculates delay time based on the current request rate and randomization.

        Returns:
            float: Delay time in seconds.
        """
        delay_time = 1.0 / self.current_rate
        random_factor = random.uniform(1.0 - self.temperature, 1.0 + self.temperature)
        return delay_time * random_factor

    def update_rate(self) -> None:
        """
        Updates the request rate based on the average latency observed over the sliding window.
        Increases the rate if average latency is low and decreases if it is high.
        """
        if len(self.latencies) == 0:
            return

        avg_latency = sum(self.latencies) / len(self.latencies)

        # Example logic: Adjust rate based on average latency
        expected_latency = 0.1  # Expected latency in seconds
        if avg_latency < expected_latency:
            self.current_rate = min(self.current_rate * 1.1, self.max_rate)
        else:
            self.current_rate = max(self.current_rate * 0.9, self.min_rate)
