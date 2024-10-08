#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI-Acquire                                                                    #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /acquire/domain/artifact/request/appdata.py                                         #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Monday August 26th 2024 10:35:55 pm                                                 #
# Modified   : Monday September 9th 2024 04:57:55 pm                                               #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
# %%
from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Any, Collection, Dict, Union

from acquire.application.orchestration.job import Context
from acquire.core.enum import DataType
from acquire.domain.artifact.request.base import AsyncRequest, Request, RequestGen
from acquire.infra.web.header import BrowserHeaders

# ------------------------------------------------------------------------------------------------ #
headers = BrowserHeaders()
# ------------------------------------------------------------------------------------------------ #
# mypy: ignore-errors


# ------------------------------------------------------------------------------------------------ #
@dataclass
class RequestAppData(Request):
    """Represents a request for AppData.

    Attributes:
        baseurl (str): The base URL for the request.
        param_list (list[Dict]): The list of parameters for the request.
        header DefaultDict[str, str]: Header parameters
    """

    data_type: DataType = DataType.APPDATA
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

    @property
    def start_index(self) -> int:
        """Returns the starting index for the current page (zero-based)."""
        return self.page * self.limit  # Zero-based index

    @property
    def end_index(self) -> int:
        """Returns the ending index for the current page (zero-based)."""
        return (self.page + 1) * self.limit  # Zero-based index

    @property
    def headers(self) -> Union[Collection[str], Dict[str, Any]]:
        return next(headers)

    @property
    def baseurl(self) -> str:
        return f"{self.scheme}://{self.host}/{self.command}"

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

    def __init__(self) -> None:
        super().__init__()


# ------------------------------------------------------------------------------------------------ #
class RequestAppDataGen(RequestGen[AsyncRequest[RequestAppData]]):
    """Encapsulates an asynchronous AppData request generation.

    Args:
        task_passport (TaskPassport): Class encapsulating identity for the Task.
        category_id (int): Four digit identifier for app genre or category.
        max_requests (int): Maximum number of apps to process.
        batch_size (int): Number of requests within an async call.
        start_page (int): Page from which to start the requests.
        request_params_cls (type[AppDataRequestParams]): The request parameters
        browser_header (BrowserHeader): Browser header iterator.
    """

    def __init__(
        self,
        context: Context,
        max_requests: int = sys.maxsize,
        batch_size: int = 100,
        start_page: int = 0,
        limit: int = 200,
        request_cls: type[RequestAppData] = RequestAppData,
    ) -> None:
        super().__init__()
        self._context = context
        self._max_requests = max_requests
        self._batch_size = batch_size
        self._start_page = start_page
        self._page = start_page
        self._limit = limit

        self._category_id = self._context.category.value

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

    def __next__(self) -> AsyncRequest[RequestAppData]:
        """Generates the next batch of asynchronous AppData requests.

        Returns:
            AsyncRequest: The next batch of requests.

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
        async_request: AsyncRequest = AsyncRequest(context=self._context)

        for page in range(batch_start_page, batch_stop_page):
            request = RequestAppData(context=self._context)
            request.genreId = self._category_id
            request.page = page
            request.limit = self._limit
            async_request.add_request(request=request)
            self._page += 1
            self._request_count += 1

        # Create the Request Object
        return async_request
