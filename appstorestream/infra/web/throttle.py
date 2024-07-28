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
# Modified   : Sunday July 28th 2024 08:38:00 am                                                   #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
"""Autothrottle Module"""
import asyncio
import random
from collections import deque
from datetime import datetime


class Throttle:
    """
    A class to manage the throttling of requests based on latency and randomized delays.

    Args:
        min_rate (float): The minimum request rate (requests per second). Default is 1.
        base_rate (float): The base request rate (requests per second). Default is 5.
        max_rate (float): The maximum request rate (requests per second). Default is 100.
        temperature (float): A parameter between 0 and 1 to control the degree of randomization in delays. Default is 0.5.
        burn_in_period (int): The number of initial requests to treat as a burn-in period. Default is 100.
        window_size (int): The number of recent requests to consider for latency calculation. Default is 10.

    Attributes:
        min_rate (float): The minimum request rate.
        base_rate (float): The base request rate.
        max_rate (float): The maximum request rate.
        temperature (float): A parameter to control the degree of randomization in delays.
        burn_in_period (int): The number of initial requests to treat as a burn-in period.
        window_size (int): The number of recent requests to consider for latency calculation.
        send_times (deque): A deque to store the send times of requests.
        recv_times (deque): A deque to store the receive times of requests.
        request_count (int): A counter for the number of requests made.
        burn_in (bool): A flag indicating if the burn-in period is active.

    Methods:
        send(): Marks the datetime before a request is sent.
        recv(): Marks the datetime after a response is received.
        delay(): Executes a delay based on the calculated rate and randomization.

    Usage examples:

    Example usage in an asynchronous context:

    ```python
    import aiohttp
    import asyncio

    async def fetch(url, throttle):
        async with aiohttp.ClientSession() as session:
            await throttle.send()
            async with session.get(url) as response:
                await throttle.recv()
                await throttle.delay()
                return await response.text()

    async def main(urls, throttle):
        tasks = [fetch(url, throttle) for url in urls]
        return await asyncio.gather(*tasks)

    urls = [
        "https://example.com/page1",
        "https://example.com/page2",
        "https://example.com/page3",
        # Add more URLs as needed
    ]

    throttle = Throttle(min_rate=1, base_rate=5, max_rate=100, temperature=0.2, burn_in_period=100)

    # Running the async main function
    results = asyncio.run(main(urls, throttle))

    # Print the results
    for result in results:
        print(result)
    ```
    """

    def __init__(self, min_rate=1, base_rate=5, max_rate=100, temperature=0.5, burn_in_period=100, window_size=10):
        self.min_rate = min_rate
        self.base_rate = base_rate
        self.max_rate = max_rate
        self.temperature = temperature
        self.burn_in_period = burn_in_period
        self.window_size = window_size

        self.send_times = deque(maxlen=window_size)
        self.recv_times = deque(maxlen=window_size)
        self.request_count = 0
        self.burn_in = True

    async def send(self):
        """Marks the datetime before a request is sent."""
        send_time = datetime.now()
        self.send_times.append(send_time)
        self.request_count += 1
        if self.request_count > self.burn_in_period:
            self.burn_in = False

    async def recv(self):
        """Marks the datetime after a response is received."""
        recv_time = datetime.now()
        self.recv_times.append(recv_time)

    def _calculate_latency(self):
        """Calculates the average latency based on the recorded send and receive times."""
        if len(self.send_times) == 0 or len(self.recv_times) == 0:
            return None
        latencies = [(recv - send).total_seconds() for send, recv in zip(self.send_times, self.recv_times)]
        return sum(latencies) / len(latencies)

    def _calculate_delay(self):
        """Calculates the delay based on the current rate and randomization."""
        if self.burn_in:
            return 1.0 / self.base_rate
        latency = self._calculate_latency()
        if latency is None:
            return 1.0 / self.base_rate

        # PID-like controller logic
        rate = self.base_rate
        if latency < 0.1:  # If latency is very low, increase the rate
            rate = min(self.max_rate, self.base_rate + (self.max_rate - self.base_rate) * (0.1 - latency))
        else:  # If latency is higher, decrease the rate
            rate = max(self.min_rate, self.base_rate - (self.base_rate - self.min_rate) * (latency - 0.1))

        delay = 1.0 / rate

        # Randomize delay based on temperature
        random_factor = random.uniform(-self.temperature, self.temperature)
        randomized_delay = delay + delay * random_factor

        return max(0, randomized_delay)

    async def delay(self):
        """Executes a delay based on the calculated rate and randomization."""
        delay_time = self._calculate_delay()
        await asyncio.sleep(delay_time)
