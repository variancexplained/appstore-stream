#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppStoreStream: Apple App Data and Reviews, Delivered!                              #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appstorestream/application/appdata/request.py                                      #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appstore-stream.git                             #
# ------------------------------------------------------------------------------------------------ #
# Created    : Saturday July 20th 2024 03:02:29 am                                                 #
# Modified   : Sunday July 28th 2024 02:20:11 pm                                                   #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
""""Request Module"""
from __future__ import annotations

import sys
from collections import defaultdict
from dataclasses import dataclass, field

from appstorestream.application import AsyncRequest, AsyncRequestGen
from appstorestream.core.data import DataClass
from appstorestream.infra.web.header import BrowserHeader


# ------------------------------------------------------------------------------------------------ #
@dataclass
class AppDataRequestParams(DataClass):
    """Encapsulates the request parameters for the app data request."""
    scheme: str = 'https'
    host: str = 'itunes.apple.com'
    term: str = "app"
    command: str = 'search?'
    media: str = 'software'
    country: str = 'us'
    lang: str = "en-us"
    explicit: str = "yes"
    limit: int = 200

# ------------------------------------------------------------------------------------------------ #
@dataclass
class AppDataRequest(AsyncRequest):
    """Represents an asynchronous request for AppData.

    Attributes:
        baseurl (str): The base URL for the request.
        param_list (list[dict]): The list of parameters for the request.
    """

    baseurl: str
    param_list: list[dict] = field(default_factory=list)
    header: defaultdict[dict] = field(default_factory=lambda: defaultdict(dict))


# ------------------------------------------------------------------------------------------------ #
class AppDataAsyncRequestGen(AsyncRequestGen):
    """Encapsulates an asynchronous AppData request generation.

    Args:
        max_requests (int): Maximum number of apps to process.
        request_params_cls (type[AppDataRequestParams]): The request parameters
        browser_header (BrowserHeader): Browser header iterator.
    """

    def __init__(
        self,
        max_requests: int = sys.maxsize,
        batch_size: int = 100,
        start_page: int = 0,
        request_params_cls: type[AppDataRequestParams] = AppDataRequestParams,
        browser_header_cls: type[BrowserHeader] = BrowserHeader,
    ) -> None:
        self._max_requests = max_requests
        self._batch_size = batch_size
        self._start_page = start_page
        self._current_page = start_page
        self._request_params = request_params_cls()
        self._browser_header = browser_header_cls()

    def __iter__(self) -> AppDataAsyncRequestGen:
        """Returns an iterator object for the request generator.

        Returns:
            AppDataAsyncRequestGen: The request generator itself.
        """

        return self

    def __next__(self) -> AppDataRequest:
        """Generates the next batch of asynchronous AppData requests.

        Returns:
            AppDataAsyncRequest: The next batch of requests.

        Raises:
            StopIteration: If no more requests can be generated.
        """

        if self._request_count >= self._max_requests:
            raise StopIteration

        baseurl = f"{self._request_params.scheme}://{self._request_params.host}/{self._request_params.command}"

        # Determine current batch size vis-a-vis remaining batches.
        requests_remaining = self._max_requests - self._request_count
        current_batch_size = min(
            self._batch_size, requests_remaining
        )
        # Get batch start and stop indices
        batch_start_page = self._current_page
        batch_stop_page = batch_start_page + current_batch_size
        # Formulate parameters for the batch
        param_list = []

        for current_page in range(batch_start_page, batch_stop_page):
            params = {
                "media": self._request_params.media,
                "term": self._request_params.term,
                "country": self._request_params.country,
                "lang": self._request_params.lang,
                "explicit": self._request_params.explicit,
                "limit": self._request_params.limit,
                "offset": current_page * self._request_params.limit,
            }
            param_list.append(params)
            self._current_page += current_batch_size

        # Create the Request Object
        return AppDataRequest(
            baseurl=baseurl, param_list=param_list, header=next(self._browser_header)
        )
