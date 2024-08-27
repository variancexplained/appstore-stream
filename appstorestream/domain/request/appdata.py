#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : AppStoreStream: Apple App Data and Reviews, Delivered!                              #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.14                                                                             #
# Filename   : /appstorestream/domain/request/appdata.py                                           #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/appstore-stream.git                             #
# ------------------------------------------------------------------------------------------------ #
# Created    : Monday August 26th 2024 10:35:55 pm                                                 #
# Modified   : Tuesday August 27th 2024 01:57:03 am                                                #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
from dataclasses import dataclass
from typing import Any, Dict

from appstorestream.domain.request.base import Request
from appstorestream.infra.web.header import BrowserHeaders


# ------------------------------------------------------------------------------------------------ #
@dataclass
class RequestAppData(Request):
    """Represents a request for AppData.

    Attributes:
        baseurl (str): The base URL for the request.
        param_list (list[Dict]): The list of parameters for the request.
        header DefaultDict[str, str]: Header parameters
    """

    genreId: int  # Category id
    current_page: int
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
    def baseurl(self) -> str:
        return f"{self.scheme}://{self.host}/{self.command}"

    @property
    def headers(self) -> Dict[str, Any]:
        return next(self.header_list)

    @property
    def params(self) -> Dict[str, object]:
        params = {
            "media": self.media,
            "genreId": self.genreId,
            "term": self.term,
            "country": self.country,
            "lang": self.lang,
            "explicit": self.explicit,
            "limit": self.limit,
            "offset": self.current_page * self.limit,
        }
        return params
