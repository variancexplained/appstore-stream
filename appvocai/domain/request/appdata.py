#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Acquire                                                                    #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appvocai/domain/request/appdata.py                                                 #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Monday August 26th 2024 10:35:55 pm                                                 #
# Modified   : Sunday September 1st 2024 01:46:45 am                                               #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from typing import Any, Dict, List

from appvocai.domain.request.base import Request, RequestAsync, RequestGen
from appvocai.infra.web.header import BrowserHeaders


# ------------------------------------------------------------------------------------------------ #
@dataclass
class RequestAppData(Request):
    """Represents a request for AppData.

    Attributes:
        baseurl (str): The base URL for the request.
        param_list (list[Dict]): The list of parameters for the request.
        header DefaultDict[str, str]: Header parameters
    """

    genreId: int = 0
    page: int = 0
    request_type: str = "appdata"
    media: str = "software"
    scheme: str = "https"
    host: str = "itunes.apple.com"
    term: str = "app"
    command: str = "search?"
    country: str = "us"
    lang: str = "en-us"
    explicit: str = "yes"
    limit: int = 200
    header_list: BrowserHeaders = BrowserHeaders()

    @property
    def start_index(self) -> int:
        """Returns the starting index for the current page (zero-based)."""
        return self.page * self.limit  # Zero-based index


    @property
    def end_index(self) -> int:
        """Returns the ending index for the current page (zero-based)."""
        return (self.page + 1) * self.limit  # Zero-based index


    @property
    def baseurl(self) -> str:
        return f"{self.scheme}://{self.host}/{self.command}"

    @property
    def headers(self) -> Dict[str, Any]:
        return next(self.header_list)

    @property
    def params(self) -> Dict[str, Any]:
        params = {
            "media": self.media,
            "genreId": self.genreId,
            "term": self.term,
            "country": self.country,
            "lang": self.lang,
            "explicit": self.explicit,
            "limit": self.limit,
            "offset": self.start_index,
        }
        return params


# ------------------------------------------------------------------------------------------------ #
@dataclass
class RequestAsyncAppData(RequestAsync):
    requests: List[RequestAppData] = field(default_factory=list)


# ------------------------------------------------------------------------------------------------ #
class RequestAppDataGen(RequestGen):
    """Encapsulates an asynchronous AppData request generation.

    Args:
        category_id (int): Four digit identifier for app genre or category.
        max_requests (int): Maximum number of apps to process.
        batch_size (int): Number of requests within an async call.
        start_page (int): Page from which to start the requests.
        request_params_cls (type[AppDataRequestParams]): The request parameters
        browser_header (BrowserHeader): Browser header iterator.
    """

    def __init__(
        self,
        category_id: int,
        max_requests: int = sys.maxsize,
        batch_size: int = 100,
        start_page: int = 0,
        limit: int = 200,
        request_cls: type[RequestAppData] = RequestAppData,
    ) -> None:
        self._category_id = category_id
        self._max_requests = max_requests
        self._batch_size = batch_size
        self._start_page = start_page
        self._page = start_page
        self._limit = limit

        self._request_cls = request_cls

        self._request_count = 0

    @property
    def bookmark(self) -> int:
        return self._page

    @property
    def batchsize(self) -> int:
        return self._batch_size

    @property
    def max_requests(self) -> int:
        return self._max_requests

    def __iter__(self) -> RequestAppDataGen:
        """Returns an iterator object for the request generator.

        Returns:
            AppDataAsyncRequestGen: The request generator itself.
        """

        return self

    def __next__(self) -> RequestAsyncAppData:
        """Generates the next batch of asynchronous AppData requests.

        Returns:
            AppDataAsyncRequest: The next batch of requests.

        Raises:
            StopIteration: If no more requests can be generated.
        """

        if self._request_count >= self._max_requests:
            raise StopIteration

        # Determine current batch size vis-a-vis remaining batches.
        requests_remaining = self._max_requests - self._request_count
        current_batch_size = min(self._batch_size, requests_remaining)
        # Get batch start and stop indices
        batch_start_page = self._page
        batch_stop_page = batch_start_page + current_batch_size
        # Formulate list of requests
        async_requests = RequestAsyncAppData()

        for page in range(batch_start_page, batch_stop_page):
            request = RequestAppData(
                genreId=self._category_id, page=page, limit=self._limit,
            )
            async_requests.requests.append(request)
            self._page += 1

            self._request_count += 1

        # Create the Request Object
        return async_requests
