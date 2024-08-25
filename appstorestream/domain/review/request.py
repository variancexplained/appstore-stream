#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppStoreStream: Apple App Data and Reviews, Delivered!                              #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appstorestream/domain/review/request.py                                            #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appstore-stream.git                             #
# ------------------------------------------------------------------------------------------------ #
# Created    : Saturday July 20th 2024 03:02:29 am                                                 #
# Modified   : Sunday August 25th 2024 03:09:34 am                                                 #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
""""Request Module"""
from __future__ import annotations

import sys
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Collection, DefaultDict, Dict

from appstorestream.core.data import DataClass
from appstorestream.domain.base.request import AsyncRequest, AsyncRequestGen


# ------------------------------------------------------------------------------------------------ #
@dataclass
class ReviewRequestParams(DataClass):
    """Encapsulates the request parameters for the reviews request."""

    app_id: str
    start_index: int
    end_index: int
    header: dict[str, str] = field(default_factory=lambda: defaultdict(str))

    def __post_init__(self) -> None:
        self.header: dict[str, str] = {"X-Apple-Store-Front": "143441-1,29"}

    @property
    def url(self) -> str:
        return f"https://itunes.apple.com/WebObjects/MZStore.woa/wa/userReviewsRow?id={self.app.id}&displayable-kind=11&startIndex={self.start_index}&endIndex={self.end_index}&sort=1"


# ------------------------------------------------------------------------------------------------ #
@dataclass
class ReviewRequest(AsyncRequest):
    """Represents an asynchronous request for AppData.

    Attributes:
        baseurl (str): The base URL for the request.
        param_list (list[Dict]): The list of parameters for the request.
        header DefaultDict[str, str]: Header parameters
    """

    baseurl: str
    param_list: list[Dict[str, object]] = field(default_factory=list)

    header: DefaultDict[str, str] = field(default_factory=lambda: defaultdict(str))


# ------------------------------------------------------------------------------------------------ #
class AppDataRequestGen(AsyncRequestGen):  # type: ignore
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
        app_id: str,
        category_id: int,
        max_requests: int = sys.maxsize,
        batch_size: int = 100,
        start_page: int = 0,
        request_params_cls: type[ReviewRequestParams] = ReviewRequestParams,
    ) -> None:
        self._app_id: str = app_id
        self._category_id: int = category_id
        self._max_requests: int = max_requests
        self._batch_size: int = batch_size
        self._start_page: int = start_page
        self._current_page: int = start_page

        self._request_params = request_params_cls()

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

    def __iter__(self) -> AppDataRequestGen:
        """Returns an iterator object for the request generator.

        Returns:
            AppDataRequestGen: The request generator itself.
        """

        return self

    def __next__(self) -> AppDataRequest:
        """Generates the next batch of asynchronous AppData requests.

        Returns:
            AppDataRequest: The next batch of requests.

        Raises:
            StopIteration: If no more requests can be generated.
        """

        if self._request_count >= self._max_requests:
            raise StopIteration

        baseurl = f"{self._request_params.scheme}://{self._request_params.host}/{self._request_params.command}"

        # Determine current batch size vis-a-vis remaining batches.
        requests_remaining = self._max_requests - self._request_count
        current_batch_size = min(self._batch_size, requests_remaining)
        # Get batch start and stop indices
        batch_start_page = self._current_page
        batch_stop_page = batch_start_page + current_batch_size
        # Formulate parameters for the batch
        param_list = []

        for current_page in range(batch_start_page, batch_stop_page):
            params = {
                "media": self._request_params.media,
                "genreId": self._category_id,
                "term": self._request_params.term,
                "country": self._request_params.country,
                "lang": self._request_params.lang,
                "explicit": self._request_params.explicit,
                "limit": self._request_params.limit,
                "offset": current_page * self._request_params.limit,
            }
            param_list.append(params)
            self._current_page += 1

            self._request_count += 1

        # Create the Request Object
        return AppDataRequest(
            baseurl=baseurl, param_list=param_list, header=next(self._browser_header)
        )
