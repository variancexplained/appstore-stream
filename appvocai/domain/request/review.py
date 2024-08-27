#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppVoCAI - Acquire                                                                  #
# Version    : 0.2.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appvocai/domain/request/review.py                                                  #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appvocai-acquire                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Tuesday August 27th 2024 12:26:33 am                                                #
# Modified   : Tuesday August 27th 2024 03:49:10 pm                                                #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from typing import Collection, List

from appvocai.domain.request.base import Request, RequestAsync, RequestGen
from appvocai.infra.web.header import STOREFRONT


# ------------------------------------------------------------------------------------------------ #
@dataclass
class RequestAppReview(Request):
    """Represents a request for AppData.

    Attributes:
        baseurl (str): The base URL for the request.
        param_list (list[Dict]): The list of parameters for the request.
        header DefaultDict[str, str]: Header parameters
    """

    app_id: int = 0
    page: int = 0
    limit: int = 400

    @property
    def start_index(self) -> int:
        """Returns the starting index for the current page (zero-based)."""
        return self.page * self.limit  # Zero-based index


    @property
    def end_index(self) -> int:
        """Returns the ending index for the current page (zero-based)."""
        return (self.page + 1) * self.limit  # Zero-based index

    @property
    def headers(self) -> Collection[str]:
        return STOREFRONT["headers"]

    @property
    def baseurl(self) -> str:
        return f"https://itunes.apple.com/WebObjects/MZStore.woa/wa/userReviewsRow?id={self.app_id}&displayable-kind=11&startIndex={self.start_index}&endIndex={self.end_index}&sort=1"

    @property
    def params(self) -> Collection[str]:
        """The AppReview Request has no parameters."""
        return {}
# ------------------------------------------------------------------------------------------------ #
@dataclass
class RequestAsyncAppReview(RequestAsync):
    requests: List[RequestAppReview] = field(default_factory=list)


# ------------------------------------------------------------------------------------------------ #
class RequestAppReviewGen(RequestGen):
    """Encapsulates an asynchronous AppData request generation.

    Args:
        app_id (int): App Identifier
        max_requests (int): Maximum number of apps to process.
        batch_size (int): Number of requests within an async call.
        start_page (int): Page from which to start the requests.
        request_params_cls (type[AppDataRequestParams]): The request parameters
        browser_header (BrowserHeader): Browser header iterator.
    """

    def __init__(
        self,
        app_id: int,
        max_requests: int = sys.maxsize,
        batch_size: int = 100,
        start_page: int = 0,
        max_results_per_page: int = 400,
        request_cls: type[RequestAppReview] = RequestAppReview,
    ) -> None:
        self._app_id = app_id
        self._max_requests = max_requests
        self._batch_size = batch_size
        self._start_page = start_page
        self._current_page = start_page
        self._max_results_per_page = max_results_per_page

        self._request_cls = request_cls

        self._request_count = 0

    @property
    def bookmark(self) -> int:
        return self._current_page

    @property
    def batchsize(self) -> int:
        return self._batch_size

    @property
    def max_requests(self) -> int:
        return self._max_requests

    def __iter__(self) -> RequestAppReviewGen:
        """Returns an iterator object for the request generator.

        Returns:
            AppDataAsyncRequestGen: The request generator itself.
        """

        return self

    def __next__(self) -> RequestAsyncAppReview:
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
        batch_start_page = self._current_page
        batch_stop_page = batch_start_page + current_batch_size
        # Formulate list of requests
        requests = []

        for current_page in range(batch_start_page, batch_stop_page):
            end_index = current_page + self._max_results_per_page
            request = RequestAppReview(
                app_id=self._app_id, start_index=self._start_page, end_index=end_index
            )
            requests.append(request)
            self._current_page += 1

            self._request_count += 1

        # Create the Request Object
        return RequestAsyncAppReview(requests=requests)
